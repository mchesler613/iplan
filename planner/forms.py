from django import forms
from django.forms import ModelForm, TextInput
from planner.models import Person, Email, Bio, Meeting, Task
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from iplan import settings
from captcha.fields import CaptchaField
from django.urls import reverse
import smtplib
from dotenv import dotenv_values

# This form is used in PersonDetailUpdateView in views.py
class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = '__all__'
        fields = ['name', 'status', 'age']
        

# This form is used in PersonDetailUpdateView in views.py
class EmailForm(ModelForm):
    class Meta:
        model = Email
        # fields = '__all__'
        fields = ['address']

# This form is used in PersonDetailUpdateView in views.py
class BioForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].disabled = True

    class Meta:
        model = Bio
        # fields = '__all__'
        fields = ['bio', 'image']

'''
This form is used in
MeetingUpdateView and MeetingDeleteView
in views.py
'''
class MeetingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['created_by'].disabled = True

    class Meta:
        model = Meeting
        fields = '__all__'
        #fields = ['title', 'purpose', 'date', 'time', 'participants']
        widgets = {
            'date': forms.DateInput(attrs={'class':'datepicker'}),
            'time': forms.TimeInput(attrs={'class':'timepicker'}),
        }

# This form is used in TaskCreateView in views.py
class TaskForm(ModelForm):
    class Meta:
        model = Task
        #fields = '__all__'
        fields = ['title', 'description', 'deadline']
        widgets = {
            'deadline': forms.DateInput(attrs={'class':'datepicker'}),
        }

# This form is used in ContactView in views.py
class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    linkedin = forms.URLField(label='LinkedIn profile', initial='http://linkedin.com/in/')
    subject = forms.CharField(initial='Request a Demo account')
    message = forms.CharField(widget=forms.Textarea, initial="Hi, I'd like to test out this demo, thanks.")
    captcha = CaptchaField()

    def send_email(self):
        origin = settings.SITE_URL + reverse('planner:contact')
        subject = '[ContactForm] from %s' %origin
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        linkedin = self.cleaned_data['linkedin']
        message = self.cleaned_data['message']
        body = """
        Name: %s
        Email: %s
        LinkedIn: %s
        Content: %s
        """ %(name, email, linkedin, message)
        sender = settings.EMAIL_HOST_USER
        receipient = 'djangomail@djangodemo.com'
        
        response = 0

        try:
            response = send_mail(
                subject,
                body,
                sender,
                [receipient],
                fail_silently=False,
                #auth_user='bad_user',
            )
        except smtplib.SMTPException:
            #assert False
            pass

        return response
