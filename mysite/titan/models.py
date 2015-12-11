from django.db import models
import datetime


# Create your models here.
class User(models.Model):
	id = models.IntegerField(primary_key=True)
	email = models.EmailField()
	first_name = models.CharField(max_length=32)
	last_name = models.CharField(max_length=32)
	password = models.CharField(max_length=32)
	gender = models.CharField(max_length=10)        # 'M' for male, 'F' for female, 'O' for other
	birth_year = models.IntegerField()
	account_type = models.CharField(max_length=32)  # 'S' for students, 'P' for professors
	ethnicity = models.CharField(max_length=10)     # dropdown of options
	sign_up_date = models.DateTimeField(default=datetime.datetime.now())
	last_sign_in_date = models.DateTimeField(default=datetime.datetime.now())
	num_posts = models.IntegerField(default=0)

	def __str__(self):
		return u'%s %s' % (self.first_name, self.last_name)

	class Meta:
		verbose_name_plural = "users"


class Course(models.Model):
	id = models.IntegerField(primary_key=True)
	course_name = models.CharField(max_length=32)
	course_description = models.TextField()

	def __str__(self):
		return self.course_name

	class Meta:
		verbose_name_plural = "courses"


class Course_Taken(models.Model):
	user_id = models.IntegerField()
	prof_id = models.IntegerField()
	course_id = models.IntegerField()
	skill_level = models.IntegerField(null=True, blank=True, default=None)
	semester_taken = models.CharField(max_length=10)
	year_taken = models.IntegerField()
	current = models.BooleanField()
	prof_difficulty = models.IntegerField(null=True, blank=True, default=None)
	course_difficulty = models.IntegerField(null=True, blank=True, default=None)
	date_added = models.DateTimeField(default=datetime.datetime.now())

	class Meta:
		verbose_name_plural = "courses taken"


class Professor(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)


class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    course_id = models.IntegerField()
    title = models.TextField()
    content = models.TextField()
    date_posted = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.title


class Answer(models.Model):
    id = models.IntegerField(primary_key=True)
    question_id = models.IntegerField()
    user_id = models.IntegerField()
    course_id = models.IntegerField()
    content = models.TextField()
    date_posted = models.DateTimeField(default=datetime.datetime.now())


class Question_Rating(models.Model):
    id = id = models.IntegerField(primary_key=True)
    question_id = models.IntegerField()
    rating = models.IntegerField()
    rater_id = models.IntegerField() # new
    date_rated = models.DateTimeField(default=datetime.datetime.now())

    class Meta:
        verbose_name_plural = "question ratings"


class Answer_Rating(models.Model):
    id = id = models.IntegerField(primary_key=True)
    answer_id = models.IntegerField()
    rating = models.IntegerField()
    rater_id = models.IntegerField() # new
    date_rated = models.DateTimeField(default=datetime.datetime.now())


class Message(models.Model):
    id = models.IntegerField(primary_key=True)
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    title = models.TextField()
    content = models.TextField()
    date_sent = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.title


class Hangout(models.Model):
    id = models.IntegerField(primary_key=True)
    host_id = models.IntegerField()
    course_id = models.IntegerField()
    title = models.CharField(max_length=64)
    info = models.TextField()
    location = models.CharField(max_length=64)
    date = models.DateField()
    time = models.TimeField()
    date_created = models.DateTimeField(default=datetime.datetime.now())

    def __str__(self):
        return self.title















