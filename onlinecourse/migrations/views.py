from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Question, Choice, Submission, Learner, Enrollment


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(
        request,
        "onlinecourse/course_details_bootstrap.html",
        {"course": course},
    )


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method != "POST":
        questions = course.questions.prefetch_related("choices").all()
        return render(
            request,
            "onlinecourse/exam.html",
            {"course": course, "questions": questions},
        )

    learner, _ = Learner.objects.get_or_create(user=request.user)
    enrollment, _ = Enrollment.objects.get_or_create(
        learner=learner,
        course=course,
    )

    submission = Submission.objects.create(enrollment=enrollment)
    total_score = 0

    questions = course.questions.prefetch_related("choices").all()

    for question in questions:
        selected_id = request.POST.get(str(question.id))
        selected_choice = None

        if selected_id:
            selected_choice = Choice.objects.filter(
                id=selected_id,
                question=question,
            ).first()

        if selected_choice:
            submission.choices.add(selected_choice)
            total_score += question.is_get_score([selected_choice.id])

    return redirect(
        "show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, id=course_id)
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        enrollment__course=course,
        enrollment__learner__user=request.user,
    )

    selected_choices = set(
        submission.choices.values_list("id", flat=True)
    )
    results = []
    score = 0
    max_score = 0

    for question in course.questions.prefetch_related("choices").all():
        correct_choices = list(
            question.choices.filter(is_correct=True)
        )
        chosen_choices = list(
            question.choices.filter(id__in=selected_choices)
        )
        question_score = question.is_get_score(
            [choice.id for choice in chosen_choices]
        )

        score += question_score
        max_score += question.grade

        results.append({
            "question": question,
            "choices": list(question.choices.all()),
            "selected_choices": chosen_choices,
            "correct_choices": correct_choices,
            "question_score": question_score,
        })

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        {
            "course": course,
            "submission": submission,
            "results": results,
            "score": score,
            "max_score": max_score,
        },
    )
