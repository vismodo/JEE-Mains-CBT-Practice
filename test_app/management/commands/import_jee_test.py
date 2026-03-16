import tempfile
import os
from django.core.management.base import BaseCommand
import bs4
import requests
import django
from django.core.files.base import ContentFile
import urllib3
from datetime import date
from test_app.models import Test, Question
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def cfile(image_url):
    img_response = requests.get(image_url)
    if img_response.status_code == 200:
        return ContentFile(img_response.content)
    else:
        print(f"Failed to download image from {image_url}")

def import_test(url, answer_file_path):
    """
    PUT YOUR SCRIPT HERE.

    Must return:
    "1"  -> success
    "0"  -> invalid URL
    "-1" -> download error
    """
    akey_file = open(answer_file_path, 'r')
    akey = akey_file.read().strip().split("\n")
    answer_key = {qid: ans for qid, ans in (line.split(" ", 1) for line in akey)}
    response = requests.get(url)
    if response.status_code != 200:
        return 0
    html_content = response.text
    try:
        soup = bs4.BeautifulSoup(html_content, 'html.parser')
        date_element = soup.select_one("body > div.wrapper > div.main-info-pnl > table > tbody > tr:nth-child(4) > td:nth-child(2)")
        day,month,year = [int(item) for item in date_element.text.split("/")]
        date_obj = date(year=year, month=month, day=day)
        shift_element = soup.select_one("body > div.wrapper > div.main-info-pnl > table > tbody > tr:nth-child(4) > td:nth-child(2)")
        shift = shift_element.text.lower().count("pm")
        name = f"JEE Mains {day} {months[month-1]} {year}, Shift {['I','II'][shift-2]}"
        
        test_obj = Test.objects.create(name=name, shift=(shift==2),date=date_obj)
        test_obj.save()
        n=0
        def question_data(question_td):
            qtable, datatable = question_td.find_all('table')
            data_trs = datatable.find_all('tr')
            imgurls = qtable.find_all('img')
            qid = data_trs[1].find_all('td')[1].text.strip()
            ans = answer_key[qid].strip()
            if len(imgurls) > 1:
                mode = 0
                options = []
                options_images = []
                for x in range(4):
                    option_id = data_trs[2+x].find_all('td')[1].text.strip()
                    option_image = imgurls[x+1]['src']
                    options_images.append(option_image)
                    options.append(option_id)
                correct = []
                if not ans == "Drop":
                    for i in ans.split(","):
                        p = i.strip()
                        correct.append(options.index(p)+1)
            else:
                mode = 1
                options_images = []
                correct = []
                if not ans == "Drop":
                    for i in ans.split(","):
                        correct.append(int(i))
            question_image = imgurls[0]['src']
            return qid, question_image, mode, options_images, correct

        question_tds = soup.find_all('td', class_='rw')
        for question_td in question_tds:
            if n in range(25):
                subject = "Mathematics"
            elif n in range(25, 50):
                subject = "Physics"
            elif n in range(50, 75):
                subject = "Chemistry"
            n+=1
            qid, question_image, mode, options_images, correct = question_data(question_td)
            question_obj = Question.objects.create(test=test_obj, subject=subject, section=(mode==1), question_id=qid, question_number=n, correct=correct)
            question_obj.save()
            try:
                question_obj.question.save(f"{qid}.jpg", cfile("https://cdn3.digialm.com" + question_image), save=False)
                if not mode:
                    question_obj.option_1.save(f"{qid}_1.jpg", cfile("https://cdn3.digialm.com" + options_images[0]), save=False)
                    question_obj.option_2.save(f"{qid}_2.jpg", cfile("https://cdn3.digialm.com" + options_images[1]), save=False)
                    question_obj.option_3.save(f"{qid}_3.jpg", cfile("https://cdn3.digialm.com" + options_images[2]), save=False)
                    question_obj.option_4.save(f"{qid}_4.jpg", cfile("https://cdn3.digialm.com" + options_images[3]), save=False)
                question_obj.save()
                print("Saved Question No.", n)
            except Exception as e:
                print(f"Error saving question image for {qid}: {e}")
                print(f"Question image URL: https://cdn3.digialm.com{question_image}")
                print(f"Question ID: {question_obj.id}")
                print("Cancelling Paper Download, Deleting Test Object")
                test_obj.delete()
                raise e
        return 1
            

    except Exception as e:
        print(e)
        return -1


class Command(BaseCommand):

    help = "Import JEE test from response sheet"

    def handle(self, *args, **kwargs):

        print("\n=== Create Test From JEE Response Sheet ===\n")

        while True:

            url = input("Enter response sheet URL: ").strip()

            if not url:
                print("URL cannot be empty.\n")
                continue

            # create temporary answer key file
            temp = tempfile.NamedTemporaryFile(
                mode="w+",
                delete=False,
                suffix=".txt"
            )

            answer_path = temp.name

            temp.write("# Enter answer key here\n")
            temp.write("# Example format:\n")
            temp.write("1 A\n")
            temp.write("2 B\n")
            temp.write("3 D\n")

            temp.close()

            print("\nOpening answer key editor...\n")

            try:

                # open editor
                if os.name == "nt":
                    os.system(f'notepad "{answer_path}"')
                else:
                    os.system(f'nano "{answer_path}"')

                print("\nProcessing test...\n")

                result = import_test(url, answer_path)

                if result == 1:
                    print("Test successfully created.\n")
                    break

                elif result == 0:
                    print("Could not load response sheet URL. Try again.\n")

                elif result == -1:
                    print("Error downloading response sheet. Try again.\n")

                else:
                    print("Unknown error.\n")

            finally:
                # delete temp answer file
                if os.path.exists(answer_path):
                    try:
                        os.remove(answer_path)
                    except:
                        print("Couldn't delete temporary file:", answer_path)