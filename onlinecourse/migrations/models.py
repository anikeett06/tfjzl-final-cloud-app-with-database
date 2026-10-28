from django.db import models
from django.contrib.auth.models import User


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_time = models.BooleanField(default=True)
    total_learners = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    occupation = models.CharField(max_length=200, blank=True)
    social_link = models.URLField(blank=True)

    def __str__(self):
        return self.user.username


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    instructors = models.ManyToManyField(
        Instructor, related_name="courses", blank=True
    )

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.learner} - {self.course}"


class Question(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="questions"
    )
    question_text = models.TextField()
    grade = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text

    def is_get_score(self, selected_choices):
        correct_ids = set(
            self.choices.filter(is_correct=True).values_list("id", flat=True)
        )
        selected_ids = {int(choice_id) for choice_id in selected_choices}
        return self.grade if correct_ids == selected_ids else 0


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices"
    )
    choice_text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="submissions"
    )
    choices = models.ManyToManyField(Choice, related_name="submissions")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission for {self.enrollment}"
