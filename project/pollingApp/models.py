import datetime
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")


    def __str__(self):
        return self.question_text


    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    

    @classmethod
    def total_questions(cls):
        return cls.objects.count()


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

    
    @classmethod
    def total_votes(cls):
        return cls.objects.aggregate(total_votes=models.Sum('votes'))['total_votes'] or 0


    @property
    def percentage_of_votes(self):
        total_votes = self.question.choice_set.aggregate(total_votes=models.Sum('votes'))['total_votes'] or 0
        if total_votes == 0:
            return 0
        else:
            percentage = (self.votes / total_votes) * 100
            return round(percentage, 1)  