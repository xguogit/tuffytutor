from django.contrib import admin
from mysite.titan.models import User, Course, Course_Taken, Question, Answer, Message, Hangout, Professor, Question_Rating

admin.autodiscover()
# Register your models here.

class user_admin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')

class course_admin(admin.ModelAdmin):
    list_display = ('course_name', 'course_description')

class course_taken_admin(admin.ModelAdmin):
    list_display = ('user_id', 'course_id', 'skill_level', 'semester_taken', 'year_taken', 'current')

class hangout_admin(admin.ModelAdmin):
    list_display = ('id', 'host_id', 'course_id', 'title', 'info', 'location', 'date', 'time', 'date_created')

class professor_admin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name')

class question_rating_admin(admin.ModelAdmin):
    list_display = ('id', 'question_id', 'rating', 'rater_id', 'date_rated')

admin.site.register(User, user_admin)
admin.site.register(Course, course_admin)
admin.site.register(Course_Taken, course_taken_admin)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Message)
admin.site.register(Hangout, hangout_admin)
admin.site.register(Professor, professor_admin)
admin.site.register(Question_Rating, question_rating_admin)