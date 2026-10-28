
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Question, Choice, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course}
    )


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = course.questions.prefetch_related("choices").all()

    if request.method == "POST":
        score = 0
        for question in questions:
            selected_choice_id = request.POST.get(str(question.id))
            if selected_choice_id:
                choice = Choice.objects.filter(
                    id=selected_choice_id,
                    question=question
                ).first()
                if choice and choice.is_correct:
                    score += question.grade

        submission = Submission.objects.create(
            user=request.user,
            course=course,
            total_score=score
        )
        return redirect("show_exam_result", submission_id=submission.id)

    return render(
        request,
        "onlinecourse/exam.html",
        {"course": course, "questions": questions}
    )


@login_required
def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )
    questions = submission.course.questions.prefetch_related("choices").all()

    return render(
        request,
        "onlinecourse/exam_result.html",
        {
            "submission": submission,
            "questions": questions,
        }
    )
