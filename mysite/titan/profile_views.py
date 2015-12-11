from django.shortcuts import render
from django.http import HttpResponseRedirect
from mysite.titan.models import User, Course, Course_Taken, Hangout, Professor, Question, Answer, Question_Rating, Answer_Rating, Message
import datetime
import time
import hashlib

current_year = 2015
current_semester = "Fall"

def profile(request):
    if "user_id" in request.session:
        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'profile.html', {'user_info': user_info, 'all_courses': all_courses, 'current_courses': current_courses, 'previous_courses': previous_courses, 'hangouts': hangouts, 'user_rating': user_rating, 'activity_tuple': activity_tuple, 'num_posts': num_posts})
    else:
        return HttpResponseRedirect('/')

    return render(request, 'profile.html')


def load_user_info(request):
    user_info = User.objects.get(id = request.session['user_id'])

    # load all courses
    all_courses = Course.objects.all()

    # load user courses
    user_courses = Course_Taken.objects.filter(user_id = request.session['user_id'])
    current_courses = []
    previous_courses = []
    hangouts = []

    # translate course id's into course names
    for course in user_courses:
        course_value = Course.objects.get(id = course.course_id)
        if course.current == True:
            current_courses.append((course_value.course_name, course.skill_level, course.course_id))
            # load user hangouts
            hangout_list = Hangout.objects.filter(course_id=course_value.id)
            for hangout in hangout_list:
                hangouts.append(hangout)
        else:
            previous_courses.append((course_value.course_name, course.skill_level, course.course_id))


    # load user rating
    answers = Answer.objects.filter(user_id = request.session['user_id'])

    rating_counter = 0

    for answer in answers:
        answer_ratings = Answer_Rating.objects.filter(answer_id = answer.id)

        for answer_rating in answer_ratings:
            rating_counter += answer_rating.rating

    # load user activity
    user_added = User.objects.get(id = request.session['user_id'])
    courses_added = Course_Taken.objects.filter(user_id = request.session['user_id'])
    questions_added = Question.objects.filter(user_id = request.session['user_id'])
    answers_added = Answer.objects.filter(user_id = request.session['user_id'])
    question_ratings = Question_Rating.objects.filter(rater_id = request.session['user_id'])
    answer_ratings = Answer_Rating.objects.filter(rater_id = request.session['user_id'])
    hangouts_added = Hangout.objects.filter(host_id = request.session['user_id'])
    received_messages = Message.objects.filter(receiver_id = request.session['user_id'])
    sent_messages = Message.objects.filter(sender_id = request.session['user_id'])

    activity_tuple = []
    num_posts = 0

    activity_tuple.append(("Welcome To Tuffy Tutors!", user_added.sign_up_date))

    for course in courses_added:
        course_query = Course.objects.get(id = course.course_id)
        activity_string = "Course added: "+ str(course_query.course_name)
        activity_tuple.append((activity_string, course.date_added))

    for question in questions_added:
        activity_string = "Question posted: "+ str(question.title)
        activity_tuple.append((activity_string, question.date_posted))
        num_posts += 1

    for answer in answers_added:
        question_query = Question.objects.get(id = answer.question_id)
        activity_string = "Answer posted for question: "+ str(question_query.title)
        activity_tuple.append((activity_string, answer.date_posted))
        num_posts += 1

    for q_rating in question_ratings:
        question_query = Question.objects.get(id = q_rating.question_id)
        if q_rating.rating == 1:
            activity_string = "Upvoted question: "+ str(question_query.title)
        elif q_rating.rating == -1:
            activity_string = "Downvoted question: "+ str(question_query.title)
        activity_tuple.append((activity_string, q_rating.date_rated))

    for a_rating in answer_ratings:
        answer_query = Answer.objects.get(id = a_rating.answer_id)
        question_query = Question.objects.get(id = answer_query.question_id)
        if a_rating.rating == 1:
            activity_string = "Upvoted answer for question: "+ str(question_query.title)
        elif a_rating.rating == -1:
            activity_string = "Downvoted answer for question: "+ str(question_query.title)
        activity_tuple.append((activity_string, a_rating.date_rated))

    for hangout in hangouts_added:
        activity_string = "Hangout added: "+ str(hangout.title)
        activity_tuple.append((activity_string, hangout.date_created))

    for message in received_messages:
        user = User.objects.get(id = message.sender_id)
        activity_string = "Message received from: "+ str(user.first_name) + " " + str(user.last_name)
        activity_tuple.append((activity_string, message.date_sent))

    for message in sent_messages:
        user = User.objects.get(id = message.receiver_id)
        activity_string = "Message sent to: "+ str(user.first_name) + " " + str(user.last_name)
        activity_tuple.append((activity_string, message.date_sent))

    activity_tuple = sorted(activity_tuple, key=lambda x: x[1], reverse = True)

    return ((user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, rating_counter, activity_tuple, num_posts))


def edit_profile(request):
    if "user_id" in request.session:

        errors = []

        if request.POST.get('edit_user'):

            if not request.POST.get('first_name', ''):
                if not request.POST.get('last_name', ''):
                    if not request.POST.get('password', ''):
                        errors.append('No value was entered for modification')

            if request.POST.get('first_name'):
                user_query = User.objects.get(id = request.session['user_id'])
                user_query.first_name = request.POST.get('first_name').upper()
                user_query.save()

            if request.POST.get('last_name'):
                user_query = User.objects.get(id = request.session['user_id'])
                user_query.last_name = request.POST.get('last_name').upper()
                user_query.save()

            if request.POST.get('password'):
                if request.POST.get('password_confirm'):
                    if request.POST.get('password') == request.POST.get('password_confirm'):
                        user_query = User.objects.get(id = request.session['user_id'])
                        hashed_password = hashlib.md5(request.POST.get('password').encode('utf-8')).hexdigest()
                        user_query.password = hashed_password
                        user_query.save()
                    else:
                        errors.append('Passwords do not match')
                else:
                    errors.append('Confirm Password')

        if request.POST.get('edit_course'):
            if request.POST.get('course_id') != "NULL":
                change = 0
                course_query = Course_Taken.objects.get(user_id = request.session['user_id'], course_id = request.POST.get('course_id'))
                if request.POST.get('skill_level') != "NULL":
                    course_query.skill_level = request.POST.get('skill_level')
                    course_query.save()
                    change += 1
                if request.POST.get('course_difficulty') != "NULL":
                    course_query.course_difficulty = request.POST.get('course_difficulty')
                    course_query.save()
                    change += 1
                if request.POST.get('professor_difficulty') != "NULL":
                    course_query.prof_difficulty = request.POST.get('professor_difficulty')
                    course_query.save()
                    change += 1
                if change == 0:
                    errors.append('No Change Made')
            else:
                errors.append('No Course Selected')

        if request.POST.get('remove_course'):
            if request.POST.get('course_id') != "NULL":
                course_query = Course_Taken.objects.get(user_id = request.session['user_id'], course_id = request.POST.get('course_id'))
                course_query.delete()
            else:
                errors.append('No Course Selected')

        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)
        ratings = [1, 2, 3, 4, 5]

        return render(request, 'edit_profile.html', {'user_info': user_info, 'all_courses': all_courses, 'current_courses': current_courses, 'previous_courses': previous_courses, 'ratings': ratings, 'errors': errors, 'num_posts': num_posts, 'user_rating': user_rating})
    else:
        return HttpResponseRedirect('/')


def add_current_course(request):
    if "user_id" in request.session:
        # load all courses
        all_courses = Course.objects.all()
        errors = []
        professors = Professor.objects.all()

        if request.POST.get('add_current_course_button'):
            if request.POST.get('course') == "NULL":
                errors.append('Select a Course')
            else:
                # get course id
                course = Course.objects.get(course_name=request.POST.get('course'))
                this_course_id = course.id

                # check if course was already added
                course_query = Course_Taken.objects.filter(user_id=request.session['user_id'], course_id=this_course_id)
                if len(course_query) > 0:
                    # duplicate course
                    errors.append('Course was already added')

            if request.POST.get('professor') == "NULL":
                errors.append('Select a Professor')

            if not errors:
                new_course_taken = Course_Taken(user_id=request.session['user_id'], prof_id=request.POST.get('professor'), course_id=this_course_id, semester_taken=current_semester, year_taken=current_year, current=True, date_added = datetime.datetime.now())
                new_course_taken.save()
                return HttpResponseRedirect('/profile/')

        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'add_current_course.html', {'courses': all_courses, 'professors': professors, 'errors': errors, 'num_posts': num_posts, 'user_info': user_info, 'user_rating': user_rating})
    else:
        return HttpResponseRedirect('/')


def add_previous_course(request):
    if "user_id" in request.session:
        # load all courses
        all_courses = Course.objects.all()

        years = []

        for i in range(26):
            years.append(1990+i)

        errors = []

        professors = Professor.objects.all()

        if request.POST.get('add_previous_course_button'):
            if request.POST.get('course_name') == "NULL":
                errors.append('Select a Course')
            else:
                course = Course.objects.get(course_name=request.POST.get('course_name'))
                this_course_id = course.id

            if request.POST.get('semester_taken') == "NULL":
                errors.append('Select a Semester')

            if request.POST.get('year_taken') == "NULL":
                errors.append('Select a Year')

            if request.POST.get('skill_level') == "NULL":
                errors.append('Select a Skill Level')

            if request.POST.get('professor_taken') == "NULL":
                errors.append('Select a Professor')

            if request.POST.get('course_difficulty') == "NULL":
                errors.append('Rate the Course')

            if request.POST.get('professor_rating') == "NULL":
                errors.append('Rate the Professor')


            if not errors:
                new_course_taken = Course_Taken(user_id=request.session['user_id'], prof_id=request.POST.get('professor_taken'), skill_level = request.POST.get('skill_level'), course_id=this_course_id, semester_taken=request.POST.get('semester_taken'), year_taken=request.POST.get('year_taken'), current=False, prof_difficulty=request.POST.get('professor_rating'), course_difficulty=request.POST.get('course_difficulty'), date_added = datetime.datetime.now())
                new_course_taken.save()
                return HttpResponseRedirect('/profile/')

        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'add_previous_course.html', {'courses': all_courses, 'years': years, 'professors': professors, 'errors': errors, 'num_posts': num_posts, 'user_info': user_info, 'user_rating': user_rating})
    else:
        return HttpResponseRedirect('/')

def add_hangout(request):
    if "user_id" in request.session:
        course_query = Course_Taken.objects.filter(user_id=request.session['user_id'], current=True)
        user_courses = []

        for course in course_query:
            temp = Course.objects.get(id=course.course_id)
            user_courses.append(temp.course_name)

        current_date = time.strftime("%Y-%m-%d")

        errors = []

        if request.POST.get('add_hangout_button'):
            if not request.POST.get('hangout_title', ''):
                errors.append('Enter a Title')

            if not request.POST.get('hangout_location', ''):
                errors.append('Enter a Location')

            if not request.POST.get('hangout_info', ''):
                errors.append('Enter Info')

            if request.POST.get('hangout_course') == "NULL":
                errors.append('Select a Course')

            if not request.POST.get('hangout_date', ''):
                errors.append('Select a Hangout Date')
            else:
                a = datetime.datetime.strptime(request.POST.get('hangout_date'), "%Y-%m-%d")
                b = datetime.datetime.strptime(current_date, "%Y-%m-%d")

                if b > a:   # selected date is in the past
                    errors.append('Select a Valid Date')

            if not request.POST.get('hangout_time', ''):
                errors.append('Select a Hangout Time')

            if not errors:
                # get course id
                course = Course.objects.get(course_name=request.POST.get('hangout_course'))
                this_course_id = course.id

                new_hangout = Hangout(host_id=request.session['user_id'], course_id=this_course_id, title=request.POST.get('hangout_title'), info=request.POST.get('hangout_info'), location=request.POST.get('hangout_location'), date=request.POST.get('hangout_date'), time=request.POST.get('hangout_time'), date_created = datetime.datetime.now())
                new_hangout.save()
                return HttpResponseRedirect('/profile/')

        user_info, all_courses, user_courses1, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'add_hangout.html', {'user_courses': user_courses, 'current_date': current_date, 'errors': errors, 'num_posts': num_posts, 'user_rating': user_rating, 'user_info': user_info})

    else:
        return HttpResponseRedirect('/')



def course(request, course_id):
    course_id = int(course_id)
    course_info = Course.objects.get(id = course_id)

    # load course hangouts
    hangouts = Hangout.objects.filter(course_id = course_id)

    # load current users
    course_taken_query = Course_Taken.objects.filter(course_id = course_id)

    # load previous users
    previous_course_taken = Course_Taken.objects.filter(course_id = course_id, current=False)

    current_users = []
    previous_users = []

    current_list = Course_Taken.objects.filter(course_id = course_id, current=True)
    previous_list = Course_Taken.objects.filter(course_id = course_id, current=False)

    for item in current_list:
        user_query = User.objects.get(id = item.user_id)
        current_users.append(user_query)

    for item in previous_list:
        user_query = User.objects.get(id = item.user_id)
        previous_users.append(user_query)

    # get average course difficulty
    q_one = Course_Taken.objects.filter(course_id = course_id, current=False)
    sum = 0
    avg_course_difficulty = 0

    for q in q_one:
        sum += q.course_difficulty

    if len(q_one) > 0:
        avg_course_difficulty = sum / len(q_one)
    else:
        avg_course_difficulty = 0


    prof = Professor.objects.all()
    num_prof = len(prof)
    total = -1
    best_prof = -1

    for i in range(num_prof):
        q_two = Course_Taken.objects.filter(course_id = course_id, current=False, prof_id = i+1)
        for q in q_two:
            sum += q.prof_difficulty
        if sum > total:
            total = sum
            best_prof = i + 1

    if best_prof != -1:
        highest_rated_prof = Professor.objects.get(id = best_prof)


    num_users = len(course_taken_query)
    num_previous_users = len(previous_course_taken)

    male = 0
    female = 0
    other = 0
    NA = AM = BL = HI = AS = WH = DE = OT = 0

    male_skill_level = 0
    female_skill_level = 0

    for course_taken in course_taken_query:
        user_query = User.objects.get(id = course_taken.user_id)
        if user_query.gender == "MALE":
            male += 1
            if course_taken.skill_level is not None:
                male_skill_level += course_taken.skill_level
        if user_query.gender == "FEMALE":
            female += 1
            if course_taken.skill_level is not None:
                female_skill_level += course_taken.skill_level
        if user_query.gender == "OTHER":
            other += 1
        if user_query.ethnicity == "NA":
            NA += 1
        if user_query.ethnicity == "AM":
            AM += 1
        if user_query.ethnicity == "BL":
            BL += 1
        if user_query.ethnicity == "HI":
            HI += 1
        if user_query.ethnicity == "AS":
            AS += 1
        if user_query.ethnicity == "WH":
            WH += 1
        if user_query.ethnicity == "DE":
            DE += 1
        if user_query.ethnicity == "OT":
            OT += 1

    if male_skill_level != 0:
        avg_male_skill_level = male_skill_level / male
    else:
        avg_male_skill_level = 0
    if female_skill_level != 0:
        avg_female_skill_level = female_skill_level / female
    else:
        avg_female_skill_level = 0


    if request.POST.get('upvote'):
        question_id = request.POST.get('question_id')
        question_rating_query = Question_Rating.objects.filter(rater_id = request.session['user_id'], question_id = question_id)
        if len(question_rating_query) == 0:
            # check if user is the one that asked the question
            question_query = Question.objects.filter(user_id = request.session['user_id'], id = question_id)
            if len(question_query) == 0:
                new_upvote = Question_Rating(question_id = question_id, rating = 1, rater_id = request.session['user_id'], date_rated = datetime.datetime.now())
                new_upvote.save()

    if request.POST.get('downvote'):
        question_id = request.POST.get('question_id')
        question_rating_query = Question_Rating.objects.filter(rater_id = request.session['user_id'], question_id = question_id)
        if len(question_rating_query) == 0:
            # check if user is the one that asked the question
            question_query = Question.objects.filter(user_id = request.session['user_id'], id = question_id)
            if len(question_query) == 0:
                new_upvote = Question_Rating(question_id = question_id, rating = -1, rater_id = request.session['user_id'], date_rated = datetime.datetime.now())
                new_upvote.save()

    # load course questions
    questions = Question.objects.filter(course_id = course_id)
    question_tuple = []

    for question in questions:
        # load course rating
        rating_query = Question_Rating.objects.filter(question_id = question.id)

        # add up ratings for this question
        rating_value = 0
        for this_rating in rating_query:
            rating_value += this_rating.rating

        user_query = User.objects.get(id = question.user_id)
        question_tuple.append((question.id, question.title, question.date_posted, rating_value, user_query.first_name, user_query.last_name))

    question_tuple = sorted(question_tuple, key=lambda x: x[3], reverse = True)

    user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

    # load course hangouts
    hangouts = Hangout.objects.filter(course_id = course_id)

    return render(request, 'course.html', {'highest_rated_prof': highest_rated_prof,'avg_course_difficulty': avg_course_difficulty, 'num_previous_users': num_previous_users, 'num_users': num_users, 'course': course_info, 'hangouts': hangouts, 'current_users': current_users, 'previous_users': previous_users, 'question_tuple': question_tuple, 'user_info': user_info, 'user_rating': user_rating, 'num_posts': num_posts, 'male': male, 'female': female, 'other': other, 'NA': NA, 'AM': AM, 'BL': BL, 'HI': HI, 'AS': AS, 'WH': WH, 'DE': DE, 'OT': OT, 'avg_male_skill_level': avg_male_skill_level, 'avg_female_skill_level': avg_female_skill_level})


def post_question(request, course_id):
    if "user_id" in request.session:

        errors = []

        if request.POST.get('post_question_button'):
            if not request.POST.get('question_title', ''):
                errors.append('Enter Question Title')

            if not request.POST.get('question_content', ''):
                errors.append('Enter Question Content')

            if not errors:
                new_question = Question(user_id = request.session['user_id'], course_id = course_id, title = request.POST.get('question_title'), content = request.POST.get('question_content'), date_posted = datetime.datetime.now())
                new_question.save()
                url = '/course/'+ str(course_id)
                return HttpResponseRedirect(url)

        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'post_question.html', {'course_id': course_id, 'errors': errors, 'user_info': user_info, 'user_rating': user_rating, 'num_posts': num_posts})
    else:
        return HttpResponseRedirect('/')


def question(request, course_id, question_id):
    if "user_id" in request.session:
        course_info = Course.objects.get(id = course_id)
        question_info = Question.objects.get(id = question_id)

        errors = []

        if request.POST.get('answer_button'):
            if not request.POST.get('answer_content', ''):
                errors.append('Enter an Answer')

            if not errors:
                new_answer = Answer(question_id = question_info.id, user_id = request.session['user_id'], course_id = course_info.id, content = request.POST.get('answer_content'), date_posted = datetime.datetime.now())
                new_answer.save()

        if request.POST.get('upvote'):
            answer_id = request.POST.get('answer_id')
            answer_rating_query = Answer_Rating.objects.filter(rater_id = request.session['user_id'], answer_id = answer_id)
            if len(answer_rating_query) == 0:
                # check if user is the one that posted the answer
                answer_query = Answer.objects.filter(user_id = request.session['user_id'], id = answer_id)
                if len(answer_query) == 0:
                    new_upvote = Answer_Rating(answer_id = answer_id, rating = 1, rater_id = request.session['user_id'], date_rated = datetime.datetime.now())
                    new_upvote.save()

        if request.POST.get('downvote'):
            answer_id = request.POST.get('answer_id')
            answer_rating_query = Answer_Rating.objects.filter(rater_id = request.session['user_id'], answer_id = answer_id)
            if len(answer_rating_query) == 0:
                # check if user is the one that posted the answer
                answer_query = Answer.objects.filter(user_id = request.session['user_id'], id = answer_id)
                if len(answer_query) == 0:
                    new_upvote = Answer_Rating(answer_id = answer_id, rating = -1, rater_id = request.session['user_id'], date_rated = datetime.datetime.now())
                    new_upvote.save()

        answers = Answer.objects.filter(question_id = question_id)
        answer_tuple = []

        for answer in answers:
            rating_query = Answer_Rating.objects.filter(answer_id = answer.id)

            rating_value = 0
            for this_rating in rating_query:
                rating_value += this_rating.rating

            user_query = User.objects.get(id = answer.user_id)
            answer_tuple.append((answer.id, answer.content, answer.date_posted, rating_value, user_query.first_name, user_query.last_name))

        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'question.html', {'course': course_info, 'question': question_info, 'answer_tuple': answer_tuple, 'errors': errors, 'user_info': user_info, 'user_rating': user_rating, 'num_posts': num_posts})

    else:
        return HttpResponseRedirect('/')


def message(request):
    if "user_id" in request.session:
        message_tuple = []

        received_messages = Message.objects.filter(receiver_id = request.session['user_id'])
        sent_messages = Message.objects.filter(sender_id = request.session['user_id'])

        for message in received_messages:
            user_query = User.objects.get(id = message.sender_id)
            message_tuple.append((message.title, message.content, message.date_sent, user_query.id, user_query.first_name, user_query.last_name, 'Received', message.id))

        for message in sent_messages:
            user_query = User.objects.get(id = message.receiver_id)
            message_tuple.append((message.title, message.content, message.date_sent, user_query.id, user_query.first_name, user_query.last_name, 'Sent', message.id))

        message_tuple = sorted(message_tuple, key=lambda x: x[2], reverse = True)

        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'message.html', {'message_tuple': message_tuple, 'user_info': user_info, 'user_rating': user_rating, 'num_posts': num_posts})
    else:
        return HttpResponseRedirect('/')

def new_message(request):
    if "user_id" in request.session:
        course_taken_query = Course_Taken.objects.filter(user_id = request.session['user_id'])
        user_id_list = []
        user_list = []

        for course_taken in course_taken_query:
            query = Course_Taken.objects.filter(course_id = course_taken.course_id)

            for user in query:
                user_query = User.objects.get(id = user.user_id)
                if user_query.id not in user_id_list:
                    if user_query.id != request.session['user_id']:
                        user_id_list.append(user_query.id)
                        user_list.append((user_query.id, user_query.first_name, user_query.last_name))

        errors = []

        if request.POST.get('message_send_button'):
            if request.POST.get('recipient') == "NULL":
                errors.append('Select a Recipient')

            if not request.POST.get('message_subject', ''):
                errors.append('Enter a Subject')

            if not request.POST.get('message_body', ''):
                errors.append('Enter a Body')

            if not errors:
                new_message = Message(sender_id = request.session['user_id'], receiver_id = request.POST.get('recipient'), title = request.POST.get('message_subject'), content = request.POST.get('message_body'), date_sent = datetime.datetime.now())
                new_message.save()
                return HttpResponseRedirect('/message/')

        user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

        return render(request, 'new_message.html', {'user_list': user_list, 'user_info': user_info, 'user_rating': user_rating, 'num_posts': num_posts})
    else:
        return HttpResponseRedirect('/')


def hangout(request, hangout_id):

    hangout_info = Hangout.objects.get(id = hangout_id)

    # get host name
    host = User.objects.get(id = hangout_info.host_id)

    # get course name
    course = Course.objects.get(id = hangout_info.course_id)

    course_taken_query = Course_Taken.objects.filter(course_id = hangout_info.course_id)

    user_list = []

    for course_taken in course_taken_query:
        user_query = User.objects.get(id = course_taken.user_id)
        user_list.append((user_query.id, user_query.first_name, user_query.last_name))

    user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

    return render(request, 'hangout.html', {'hangout_info': hangout_info, 'user_list': user_list, 'host': host, 'course': course, 'user_info': user_info, 'user_rating': user_rating, 'num_posts': num_posts})


def course_list(request):
    user_info, all_courses, user_courses, current_courses, previous_courses, hangouts, user_rating, activity_tuple, num_posts = load_user_info(request)

    courses = Course.objects.all()
    course_tuple = []

    for course in courses:
        taken = Course_Taken.objects.filter(course_id = course.id)
        course_tuple.append((course.id, course.course_name, course.course_description, len(taken)))

    return render(request, 'course_list.html', {'user_info': user_info, 'user_rating': user_rating, 'num_posts': num_posts, 'course_tuple': course_tuple})


def badge(request, user_id):
    user_query = User.objects.get(id = user_id)

    # load user rating
    answers = Answer.objects.filter(user_id = user_query.id)

    rating_counter = 0

    for answer in answers:
        answer_ratings = Answer_Rating.objects.filter(answer_id = answer.id)

        for answer_rating in answer_ratings:
            rating_counter += answer_rating.rating

    # load num posts for user
    questions = Question.objects.filter(user_id = user_id)
    answers = Answer.objects.filter(user_id = user_id)

    badge_num_posts = len(questions) + len(answers)

    # load courses for user
    courses = Course_Taken.objects.filter(user_id = user_id)
    course_list = []

    for course in courses:
        a = Course.objects.get(id = course.course_id)
        course_list.append(a)

    return render(request, 'badge.html', {'badge_user': user_query, 'badge_user_rating': rating_counter, 'badge_num_posts': badge_num_posts, 'badge_course': course_list})


def reply(request, message_id):
    message_query = Message.objects.get(id = message_id)

    sender = message_query.sender_id

    recipient = User.objects.get(id = sender)

    errors = []

    if request.POST.get('reply_send_button'):
        if not request.POST.get('reply_subject', ''):
            errors.append('Enter a Subject')

        if not request.POST.get('reply_body', ''):
            errors.append('Enter a Body')

        if not errors:
            new_message = Message(sender_id = request.session['user_id'], receiver_id = sender, title = request.POST.get('reply_subject'), content = request.POST.get('reply_body'), date_sent = datetime.datetime.now())
            new_message.save()
            return HttpResponseRedirect('/message/')

    return render(request, 'reply.html', {'errors': errors, 'recipient': recipient, 'message_id': message_id})




