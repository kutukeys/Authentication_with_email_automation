
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from gfg import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from . tokens import generate_token

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username = username):
            messages.error(request, "Username already exist! please try some other username")
            return redirect('home')

        if User.objects.filter(email = email):
            messages.error(request, 'email already exist, please try some other email')
            return redirect('home')

        if len(username)>10:
            messages.error(request, "Username cannot be more than 10 characters")

        if pass1 != pass2:
            messages.error(request, "Passwords mismatch!")

        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!")


        new_user = User.objects.create_user(username, email, pass1)
        new_user.first_name = fname
        new_user.last = lname
        new_user.is_active = False

        new_user.save()

        messages.success(request, "Your account has been created successfully and we have sent you a confirmation Email.")

        # Welcome Email
        subject = "Welcome to GFG - Django login!"
        message = "Hello " + new_user.first_name + "\n  Welcome to EassyCodes!! \n Thank you for checking my website out \n i have also sent you a confirmation email, please confirm your email address to get going. \n\n Regards, Israel Kutu "
        from_email = settings.EMAIL_HOST_USER
        to_list = [new_user.email]

        email = EmailMessage(
            subject,
            message,
            from_email,
            to_list

        )

        email.fail_silently = False
        email.send()

        # Email Address Confirmation Email

        current_site = get_current_site(request)
        email_subject = "Confirm Your Email at GFG - Django Login!"
        message2 = render_to_string('email_confirmation.html', {
            'name': new_user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
            'token': generate_token().make_token(new_user),

        })

        email_token = EmailMessage(
            email_subject,
            message2,
            from_email,
            to_list
        )
        email_token.fail_silently =  False
        email_token.send()



        # subject = 'Welcome to GFG - Django login!'
        # message = "Hello " + new_user.first_name + "Welcome to EassyCodes!! \n Thank you for checking my website out \n i have also sent you a confirmation email, please confirm your email address to get going. \n\n Regards, Israel Kutu "
        # from_email = settings.EMAIL_HOST_USER
        # to_list = [new_user.email]
        # send_mail(subject, message, from_email, to_list, fail_silently = True)

        return redirect('signin')

    return render(request, "authentication/signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(request, username = username, password=pass1 )

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {'fname': fname})
        else:
            messages.error(request, "Wrong credentials")
            return redirect('home')

    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "logged out successfully")
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        new_user = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        new_user = None

    if new_user is not None and generate_token.check_token(new_user, token):
        new_user.is_active = True
        new_user.save()
        login(request, new_user)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')
