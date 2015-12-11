from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from mysite.titan.models import User, Course, Course_Taken
import datetime
import hashlib


# Create your views here.
def index(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('email', ''):
            errors.append('Enter an Email')
        else:
            if not request.POST.get('password', ''):
                errors.append('Enter a Password')
            else:
                try:
                    user_query = User.objects.get(email = request.POST['email'].upper())
                except User.DoesNotExist:
                    errors.append('Email Does Not Exist')
                else:
                    hashed_password = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()

                    if user_query.password == hashed_password:
                        request.session['user_id'] = user_query.id
                        # update last sign in date
                        user = User.objects.get(id = user_query.id)
                        user.last_sign_in_date = datetime.datetime.now()
                        user.save()
                        return HttpResponseRedirect('/profile/')
                    else:
                        errors.append('Wrong Password')

    return render(request, 'index.html', {'errors': errors})


def register(request):
    years = []
    for i in range(51):
        years.append(1960+i)

    errors = []
    if 'cancel' in request.POST:
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        if request.POST.get('email') and '@' not in request.POST['email'] or '.edu' not in request.POST['email']:
            errors.append('Enter a valid Cal State Fullerton E-mail address.')
        else:
            if request.POST['email'] != request.POST['email_confirm']:
                errors.append('Email Mismatch')
            else:
                # check if email is already in the database
                user_query = User.objects.filter(email = request.POST['email'])
                if user_query:
                    # email is being used
                    errors.append('Email is being used')
        if not request.POST.get('first_name', ''):
            errors.append('Enter a First Name')
        if len(request.POST['first_name']) > 32:
            errors.append('First Name must be 32 letters or less')
        if len(request.POST['last_name']) > 32:
            errors.append('Last Name must be 32 letters or less')
        if not request.POST.get('last_name', ''):
            errors.append('Enter a Last Name.')
        if not request.POST.get('password', ''):
            errors.append('Enter a Password')
        else:
            if request.POST['password'] != request.POST['password_confirm']:
                errors.append('Password Mismatch')

        user_gender = request.POST.get('gender')
        if user_gender == "NULL":
            errors.append('Select a Gender')

        # get date of birth value
        user_birth_year = request.POST.get('birth_year')
        if user_birth_year == "NULL":
            errors.append('Select a Birth Year')

        user_type = request.POST.get('user_type')
        if user_type == "NULL":
            errors.append('Select an Account Type')

        user_ethnicity = request.POST.get('ethnicity')
        if user_ethnicity == "NULL":
            errors.append('Select an Ethnicity')

        if not request.POST.get('agreement', False):
            errors.append('Accept the Agreement below')

        if not errors:
            hashed_password = hashlib.md5(request.POST['password'].encode('utf-8')).hexdigest()
            new_user = User(first_name=request.POST['first_name'].upper(), last_name=request.POST['last_name'].upper(), email = request.POST['email'].upper(), password = hashed_password, account_type = request.POST.get('user_type'), gender = user_gender, birth_year = user_birth_year, ethnicity = user_ethnicity)
            new_user.save()
            return HttpResponseRedirect('/')
    return render(request, 'register.html', {'errors': errors, 'email': request.POST.get('email', ''), 'first_name': request.POST.get('first_name', ''), 'last_name': request.POST.get('last_name', ''), 'years': years})


def logout(request):
    if "user_id" in request.session:
        del request.session['user_id']
        return HttpResponseRedirect('/')
    else:
    	return HttpResponseRedirect('/')


def edit_profile(request):
    return render(request, 'edit_profile.html')


def test(request):
    males = len(User.objects.filter(gender="MALE"))
    females = len(User.objects.filter(gender="FEMALE"))
    other = len(User.objects.filter(gender="OTHER"))

    return render(request, 'test.html', {'males': males, 'females': females, 'other': other})