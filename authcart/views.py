from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import PasswordResetTokenGenerator


# Create your views here.

def signup(request):
    if request.method=="POST":
        email=request.POST['email']   
        password=request.POST['pass1']   
        confirm_password=request.POST['pass2']   
        if password != confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'signup.html')
        
        try:                                                            #Using Try Block to catch the error if the user(email) already exists
            if User.objects.get(username=email):
                messages.info(request,"Email is Taken")
                return render(request,'signup.html')

        except Exception as identifier:
            pass                                                        #Creating the except block as the try block needs an except block as well 

        user = User.objects.create_user(email,email,password)           #Username, email, password
        user.is_active=False                                            # Turning of the user as an active user to send him an email to authinticate and activate his email 
        user.save()
        email_subject="Activate Your Account"
        message=render_to_string('activate.html', {
            'user':user,
            'domain':'127.0.0.1:8000',                                   #I should change this when hosting the website => Website name ==> empower.in (or) empower.com
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),           # Every user will have a primary key and I am encrypting that primary key
            'token':generate_token.make_token(user)                      # Generating one token for that primary key

        })


        # Generating the activating email
        # email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])  #==> [email] == the email id of the person that sign up's into our page
        # email_message.send()          # Need an email id to send this email to the user


        messages.success(request,f"Activation Link sent to your Email {message}")    # Directly passing the link to the user onspot
        return redirect(request,'/auth/login')
    return render(request,'signup.html')


class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_text(urlsafe_base64_decode(uidb64)) # Decoding the uid
            user=User.objects.get(pk=uid)  
        
        except Exception as identifier:
            user=None
        
        if user is not None and generate_token.check_token(user,token):     # Checking if the user is present in the database 
            user.is_active=True                                             # Activating Access to the user once he clickes on the link sent to him
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/auth/login')
        return render(request,'activatefail.html')    


    
def handlelogin(request):
    if request.method=="POST":

        username=request.POST['email']
        userpassword=request.POST['pass1']
        myuser=authenticate(username=username,password=userpassword)         #Authinticating the username and password

        if myuser is not None:
            login(request,myuser)
            messages.success(request,"Login SuccessFul")
            return redirect('/')

        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/auth/login')

    return render(request,'login.html')



def handlelogout(request):
    logout(request)
    messages.info(request,"Logout Success")
    return redirect('/auth/login')


class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'request-reset-email.html')

    def post(self,request):
        email = request.POST['email']
        user = User.objects.filter(email=email)

        if user.exists():
            # current_site = get_current_site(request)
            email_subject = '[Reset Your Password]'
            message = render_to_string('reset-user-password.html',{
                'domain' : '127.0.0.1:8000',
                'uid' : urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token' : PasswordResetTokenGenerator().make_token(user[0])
            })

            # email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])  #Need an Email host to send emails
            # # EmailThread(email_message).start()
            # email_message.send()
            
            messages.info(request,f"WE HAVE SENT YOU AN EMAIL WITH INSTRUCTIONS TO RESET THE PASSWORD {message}")
            return render(request,'request-reset-email.html')



class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64' : uidb64,
            'token' : token,
        }

        try: 
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render(request,'request-reset-email.html')

        except DjangoUnicodeDecodeError as identifier:
            pass

        return render(request,'set-new-password.html',context)

    def post(self,request,uidb64,token):
        context = {
            'uidb64' : uidb64,
            'token' : token,
        }

        password = request.POST['pass1']
        confirm_password = request.POST['pass2']
        if password != confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'set-new-password.html',context)
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request,"Password Reset Success Please Login with New Password")  
            return redirect('/auth/login')
        
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request,"Something Went Wrong")
            return render(request,"set-new-password.html",context)