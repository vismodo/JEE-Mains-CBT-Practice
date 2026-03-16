from django.db import models

# Create your models here.
class Test(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    shift = models.BooleanField()  # False for Shift 1, True for Shift 2

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50)  # 'Physics', 'Chemistry', 'Mathematics'
    section = models.BooleanField()  # False for Section 1 (MCQ), True for Section 2 (Numerical)
    question = models.ImageField(upload_to='static/questions/')
    question_id = models.CharField(max_length=20)
    question_number = models.IntegerField()
    option_1 = models.ImageField(upload_to='static/options/')
    option_2 = models.ImageField(upload_to='static/options/')
    option_3 = models.ImageField(upload_to='static/options/')
    option_4 = models.ImageField(upload_to='static/options/')
    correct = models.JSONField(
        default=list,
        blank=True
    )

class TestAttempt(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    started = models.DateTimeField(auto_now_add=True)
    finished=models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    active_question = models.IntegerField(default=1)

class QuestionAttempt(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected = models.IntegerField(default=0)
    class Type(models.IntegerChoices):
        UNATTEMPTED = 1, "Unattempted"
        ATTEMPTED = 2, "Attempted"
        UA_MARKED = 3, "Unattempted & Marked For Review"
        A_MARKED = 4, "Attempted & Marked For Review"
        UNSEEN = 5, "Unseen"
    type=models.IntegerField(choices=Type.choices, default=Type.UNSEEN)
