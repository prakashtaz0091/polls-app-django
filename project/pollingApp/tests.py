import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question



class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)




def create_question(question_text, days):
    time = timezone.now()+datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("pollingApp:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])


    def test_past_question(self):
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse("pollingApp:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[question])


    def test_future_question(self):
        create_question(question_text="future question.",days=30)
        response = self.client.get(reverse("pollingApp:index"))
        self.assertContains(response,"No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])   


    def test_future_question_and_past_question(self):
        question=create_question(question_text="Past question.",days=-30)
        create_question(question_text="Future question.", days=30)
        response=self.client.get(reverse("pollingApp:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[question])


    def test_two_past_questions(self):
        question1=create_question(question_text="Past question 1.", days=-30)   
        question2=create_question(question_text="Past question 2.", days=-5)
        response=self.client.get(reverse("pollingApp:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[question2,question1])    



class DetailViewTest(TestCase):
    def setUp(self):
        # Create a question with pub_date in the past
        self.past_question = Question.objects.create(
            question_text="Past question.", 
            pub_date=timezone.now() - timezone.timedelta(days=1)
        )
        # Create a question with pub_date in the future
        self.future_question = Question.objects.create(
            question_text="Future question.", 
            pub_date=timezone.now() + timezone.timedelta(days=1)
        )

    def test_get_queryset(self):
        """
        Test that get_queryset() excludes future questions.
        """
        # Simulate a request to the view for the past question
        response = self.client.get(reverse('pollingApp:detail', args=(self.past_question.id,)))
        
        # Verify that the past question is in the response context
        self.assertEqual(response.context['question'], self.past_question)
        
        # Verify that the future question is not in the response context
        self.assertNotEqual(response.context['question'], self.future_question)

