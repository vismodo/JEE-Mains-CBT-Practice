from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Question


@receiver(post_delete, sender=Question)
def delete_question_files(sender, instance, **kwargs):

    fields = [
        instance.question,
        instance.option_1,
        instance.option_2,
        instance.option_3,
        instance.option_4
    ]

    for f in fields:
        if f and f.name:
            f.delete(save=False)