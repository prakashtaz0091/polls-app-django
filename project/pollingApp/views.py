from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.db.models import F
from .models import Choice, Question
from django.utils import timezone
from django.contrib import messages

class IndexView(generic.ListView):
    template_name = "pollingApp/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model=Question
    template_name="pollingApp/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "pollingApp/results.html"



def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "pollingApp/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    
    else:
        if request.session.get('has_voted_%s' % question_id, False):
            # User has already voted
            messages.warning(request, f"""You have successfully voted in "{selected_choice.choice_text}" for "{question.question_text}" """)
            return HttpResponseRedirect(reverse("pollingApp:index"))
        
        # Increment the vote count
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        
        # Set session variable to indicate that the user has voted
        request.session['has_voted_%s' % question_id] = True
        
        # Redirect to the results page
        return HttpResponseRedirect(reverse("pollingApp:results", args=(question.id,)))



