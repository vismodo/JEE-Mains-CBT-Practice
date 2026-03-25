from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Test, TestAttempt, QuestionAttempt, Question
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
    if request.user.is_authenticated:
        p = TestAttempt.objects.filter(user=request.user, active=True)
        if len(p) > 1:
            for x in p:
                x.active = False
                x.finished = None
                x.save()
            return redirect("test_app:index")
        elif len(p) == 1:
            return redirect("test_app:test")
        tests = Test.objects.all().order_by('date')
        return render(request, 'dash.html', {'user_name': request.user.username, "tests": tests, "attempts": reversed(TestAttempt.objects.filter(user=request.user)), "admin_show": request.user.is_superuser})
    else:
        return redirect('accounts:login')

def start_test(request, test_id):
    test = Test.objects.get(id=test_id)
    p = TestAttempt.objects.filter(user=request.user, active=True)
    if len(p) > 1:
        for x in p:
            x.active = False
            x.finished = None
            x.save()
        return redirect("test_app:index")
    elif len(p) == 1:
        return redirect("test_app:test")
    testattempt = TestAttempt.objects.create(user=request.user, test=test, score=0, total_questions=0, active=True, active_question=1)
    quests = Question.objects.filter(test=test)
    attempts=[]
    for q in quests:
        attempts.append(QuestionAttempt(attempt=testattempt, question=q))
    QuestionAttempt.objects.bulk_create(attempts, batch_size=25)
    testattempt.started=timezone.now()
    testattempt.save()
    return redirect('test_app:test')


@login_required
def test_view(request):
    try:
        testattempt = TestAttempt.objects.get(user=request.user, active=True)
    except TestAttempt.DoesNotExist:
        return redirect("test_app:index")
    except TestAttempt.MultipleObjectsReturned:
        for x in TestAttempt.objects.filter(user=request.user, active=True):
            x.active = False
            x.finished = None
            x.save()
        return redirect('test_app:index')
    active_question = Question.objects.get(test=testattempt.test, question_number=testattempt.active_question)
    if request.method == "POST":
        if 's' in request.POST.get('action'):
            q_attempt = QuestionAttempt.objects.get(attempt=testattempt, question=active_question)
            if request.POST.get('selected_option'):
                selected_option = int(request.POST.get('selected_option', 0))
                q_attempt.selected = selected_option
                q_attempt.type = QuestionAttempt.Type.ATTEMPTED
            else:
                q_attempt.type = QuestionAttempt.Type.UNATTEMPTED
            q_attempt.save()
        if 'submit' in request.POST.get('action'):
            testattempt.active = False
            testattempt.finished = timezone.now()
            testattempt.save()
            return redirect('test_app:testanalysis', testattempt.id)
        if 'm' in request.POST.get('action'):
            q_attempt = QuestionAttempt.objects.get(attempt=testattempt, question=active_question)
            if q_attempt.type == QuestionAttempt.Type.ATTEMPTED:
                q_attempt.type = QuestionAttempt.Type.A_MARKED
            elif q_attempt.type == QuestionAttempt.Type.UNATTEMPTED:
                q_attempt.type = QuestionAttempt.Type.UA_MARKED
            q_attempt.save()
        if 'n' in request.POST.get('action'):
             try:
                 q_attempt = QuestionAttempt.objects.get(attempt=testattempt, question=testattempt.active_question+1)
                 testattempt.active_question += 1
                 testattempt.save()
             except:
                 pass
        if 'c' in request.POST.get('action'):
            q_attempt = QuestionAttempt.objects.get(attempt=testattempt, question=active_question)
            q_attempt.selected = 0
            if q_attempt.type != QuestionAttempt.Type.UNATTEMPTED:
                q_attempt.type = QuestionAttempt.Type.UNATTEMPTED
            q_attempt.save()
        return redirect('test_app:test')
    
    question_stat = []
    questions = QuestionAttempt.objects.filter(attempt=testattempt)
    q_attempt = QuestionAttempt.objects.get(attempt=testattempt, question__question_number=testattempt.active_question)
    if q_attempt.type == QuestionAttempt.Type.UNSEEN:
        q_attempt.type = QuestionAttempt.Type.UNATTEMPTED
        q_attempt.save()
    for q in questions:
        question_stat.append(q.type)
    return render(request, 'test.html', {'test': testattempt.test, 'test_start_time': testattempt.started, 'question_stat': question_stat, 'question': active_question, 'current_opt': q_attempt.selected, 'not_visited': question_stat.count(QuestionAttempt.Type.UNSEEN), 'not_answered': question_stat.count(QuestionAttempt.Type.UNATTEMPTED), 'answered': question_stat.count(QuestionAttempt.Type.ATTEMPTED), 'marked': question_stat.count(QuestionAttempt.Type.UA_MARKED), 'marked_answered': question_stat.count(QuestionAttempt.Type.A_MARKED)})

@login_required
def nav_question(request, question_number):
    try:
        testattempt = TestAttempt.objects.get(user=request.user, active=True)
        q_attempt = QuestionAttempt.objects.get(attempt=testattempt, question__question_number=question_number)
        if q_attempt.type == QuestionAttempt.Type.UNSEEN:
            q_attempt.type = QuestionAttempt.Type.UNATTEMPTED
            q_attempt.save()
        testattempt.active_question = question_number
        testattempt.save()
    except:pass
    return redirect('test_app:test')
@login_required
def test_analysis(request, attempt_id):
    try:
        testattempt = TestAttempt.objects.get(id=attempt_id, active=False)
        if not (request.user.is_superuser or testattempt.user.id == request.user.id):
            raise Exception("Unauthorised access to test attempt")
        question_attempts = QuestionAttempt.objects.filter(attempt=testattempt).select_related('question')
        score = [0,0,0]
        analysis = []
        subjects = {"Mathematics": 0, "Physics": 1, "Chemistry": 2}
        stat = {
            1: "Unattempted",
            2: "Attempted",
            3: "Unattempted & Marked For Review",
            4: "Attempted & Marked For Review",
            5: "Unseen"
        }
        for qa in question_attempts:
            p = stat[qa.type]
            r = qa.question.correct
            s = qa.selected
            if r == []:
                score[subjects[qa.question.subject]] += 4
                p = "Dropped"
                q = 1
            elif qa.type == QuestionAttempt.Type.UNATTEMPTED or qa.type == QuestionAttempt.Type.UA_MARKED or qa.type == QuestionAttempt.Type.UNSEEN:
                score[subjects[qa.question.subject]] +=0
                q = 2
                s = "Unattempted"
            elif s in r:
                score[subjects[qa.question.subject]] += 4
                q=0
            else:
                score[subjects[qa.question.subject]] -= 1
                q=3
            if r != []:
                r = str(r).replace("[","").replace("]","")
            analysis.append({
                'question': qa.question,
                'selected_option': s,
                'correct_option': r,
                'is_correct': q,
                'status': p
            })
            
        testattempt.total_questions = question_attempts.count()
        total = score[0]+score[1]+score[2]
        testattempt.score = total
        testattempt.save()
        return render(request, 'testanalysis.html', {'score': score, 'analysis': analysis, 'testattempt': testattempt, 'total': total, 'percentage': int(total / (testattempt.total_questions * 4) * 10000)/100})
    except Exception as e:
        print(e)
        return redirect('test_app:index')