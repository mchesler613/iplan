from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView, FormView
from planner.models import Person, Task, Meeting, Bio, Email
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
from planner.forms import PersonForm, EmailForm, BioForm, MeetingForm, TaskForm, ContactForm
from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
#from django.contrib.auth.decorators import login_required
#from django.utils.decorators import method_decorator
from django.contrib.auth import logout, login
from dotenv import dotenv_values
import requests
from django.contrib.auth.models import User
# useful to parse form time fields to a datetime object, must install separately
# pip install python-dateutil
from dateutil.parser import parse  
from django.core.paginator import Paginator
from requests_oauthlib import OAuth2Session
import secrets
from requests.models import PreparedRequest
from iplan import settings

client_id = settings.GITHUB_OAUTH_CLIENT_ID    
client_secret = settings.GITHUB_OAUTH_SECRET
github = OAuth2Session(client_id)
authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
state = ''
redirect_uri = settings.GITHUB_OAUTH_CALLBACK_URL

# Utility Functions
# a utility function to convert a date string and returns a date in datetime format
# for example: '2021-04-09' returns datetime.datetime(2021, 4, 9, 0, 0)
# we can then compare the datetime to another datetime, e.g.datetime.now().date() 
def date_string_to_date(input_string):
    date_obj = parse(input_string)
    return date_obj.date()

# a utility function to convert a time string and returns a time in datetime format
# for example: '09:00 AM' returns datetime.datetime(2021, 4, 9, 9, 0)
# we can then compare the datetime to another datetime, e.g. datetime.now().time()
def time_string_to_time(input_string):
    time_obj = parse(input_string)
    return time_obj.time()

# Create your views here.
class IndexView(TemplateView):
    template_name = "planner/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class PersonDetailView(DetailView):
    template_name = "planner/person_detail.html"
    model = Person

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #person = Person.objects.get(pk=self.kwargs['pk'])
        try:
            person = get_object_or_404(Person,pk=self.kwargs['pk'])
            person.my_status()
            context['person'] = person
            context['meetings_today'] = person.meetings_today()
            context['tasks_due_today'] = person.tasks_due_today()
        except:
            context['meetings_today'] = {}
            context['tasks_due_today'] = {}
            messages.error(self.request, 'There is no account associated with this login')

        #assert False
        return context

class PersonListView(ListView):
    template_name = "planner/people_list.html"
    model = Person
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # call this to update the status
        ''' bug
        user = self.request.user
        context['person'] = user.person
        '''
        context['status_list'] = {}
        for person in context['person_list']:
            context['status_list'][person.name] = person.my_status()
        #assert False
        return context

# A View of Task QuerySet associated with Person
class TaskListView(ListView):
    template_name = "planner/grid_task_list.html"
    model = Task
    paginate_by = 5
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #person = Person.objects.get(pk=self.kwargs['pk'])
        person = get_object_or_404(Person,pk=self.kwargs['pk'])
        context['person'] = person
        context['person_tasks'] = person.all_tasks()
        context['person_expired_tasks'] = person.expired_tasks()
        context['tasks_due_today'] = person.tasks_due_today()
        context['person_future_tasks'] = person.future_tasks()
        context['time_now'] = timezone.now()
        context['form'] = TaskForm()

        task_dict = {
            'today': person.tasks_due_today(),
            'future': person.future_tasks(),
            'expired': person.expired_tasks(),
        }

        today_paginator = Paginator(task_dict['today'], 3)
        if self.request.GET.get('task') == 'today':
            page_number = self.request.GET.get('page')
        else:
            page_number = 1
        today_page_obj = today_paginator.get_page(page_number)
        context['today_page_obj'] = today_page_obj

        future_paginator = Paginator(task_dict['future'], 3)
        if self.request.GET.get('task') == 'future':
            page_number = self.request.GET.get('page')
        else:
            page_number = 1
        future_page_obj = future_paginator.get_page(page_number)
        context['future_page_obj'] = future_page_obj

        expired_paginator = Paginator(task_dict['expired'], 3)
        if self.request.GET.get('task') == 'expired':
            page_number = self.request.GET.get('page')
        else:
            page_number = 1
        expired_page_obj = expired_paginator.get_page(page_number)
        context['expired_page_obj'] = expired_page_obj

        #assert False
        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        person = get_object_or_404(Person, pk=pk)
        task_form = TaskForm(data=request.POST)
        if task_form.is_bound and task_form.is_valid():
            new_task = task_form.save(commit=False)
            new_task.person = person
            new_task.save()
            task = get_object_or_404(Task, pk=new_task.pk)
            messages.add_message(request, messages.SUCCESS, 'Task Title: %s Task Description: %s added.' %(task.title, task.description))
        else:
            messages.error(request, task_form.errors)

        return HttpResponseRedirect(reverse('planner:task_list', kwargs = {'pk': person.pk}))

# A View of Meeting QuerySet associated with Person
class MeetingListView(ListView):
    template_name = "planner/meeting_list.html"
    model = Meeting
    #paginate_by = 5
    form_class = MeetingForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #person = Person.objects.get(pk=self.kwargs['pk'])
        person = get_object_or_404(Person,pk=self.kwargs['pk'])
        context['person'] = person
        context['meetings_today'] = person.meetings_today()
        context['future_meetings'] = person.future_meetings()
        context['expired_meetings'] = person.expired_meetings()
        context['time_now'] = timezone.now()
        context['form'] = MeetingForm(initial={'participants':person, 'created_by':person})

        meetings_dict = {
            'today': person.meetings_today(),
            'future': person.future_meetings(),
            'expired': person.expired_meetings(),
        }

        today_paginator = Paginator(meetings_dict['today'], 2)
        if self.request.GET.get('meeting') == 'today':
            page_number = self.request.GET.get('page')
        else:
            page_number = 1
        today_page_obj = today_paginator.get_page(page_number)
        context['today_page_obj'] = today_page_obj

        future_paginator = Paginator(meetings_dict['future'], 2)
        if self.request.GET.get('meeting') == 'future':
            page_number = self.request.GET.get('page')
        else:
            page_number = 1
        future_page_obj = future_paginator.get_page(page_number)
        context['future_page_obj'] = future_page_obj

        expired_paginator = Paginator(meetings_dict['expired'], 3)
        if self.request.GET.get('meeting') == 'expired':
            page_number = self.request.GET.get('page')
        else:
            page_number = 1
        expired_page_obj = expired_paginator.get_page(page_number)
        context['expired_page_obj'] = expired_page_obj

        #assert False
        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        person = get_object_or_404(Person, pk=pk)
        meeting_form = MeetingForm(data=request.POST)
        if meeting_form.is_bound and meeting_form.is_valid():
            form_date_only = date_string_to_date(request.POST['date'])
            date_today = datetime.now().date()

            form_time_only = time_string_to_time(request.POST['time'])
            time_now = datetime.now().time()

            if form_date_only < date_today or (form_date_only == date_today and form_time_only < time_now):
                messages.add_message(request, messages.ERROR, 'Meeting date %s and time %s should be in the future' %(form_date_only, form_time_only))
                #return HttpResponseRedirect(reverse('planner:meeting_create_form', kwargs={'pk': pk}))
                return HttpResponseRedirect(reverse('planner:meeting_list', kwargs = {'pk': person.pk}))
            else:
                new_meeting = meeting_form.save()
                meeting = get_object_or_404(Meeting, pk=new_meeting.pk)
                messages.add_message(request, messages.SUCCESS, 'Meeting Title: %s Meeting Purpose: %s added.' %(meeting.title, meeting.purpose))
                return HttpResponseRedirect(reverse('planner:meeting_list', kwargs = {'pk': person.pk}))
        else:
            messages.error(request, meeting_form.errors)
            #return HttpResponseRedirect(reverse('planner:meeting_create_form', kwargs={'pk': pk}))
            return HttpResponseRedirect(reverse('planner:meeting_list', kwargs = {'pk': person.pk}))

class PersonUpdateView(UpdateView):
    model = Person
    fields = '__all__'
    template_name_suffix = '_update_form'


class BioUpdateView(UpdateView):
    model = Bio
    fields = ['bio', 'image']
    template_name_suffix = '_update_form'


class EmailUpdateView(UpdateView):
    model = Email
    fields = ['address']
    # form_class = EmailForm
    template_name_suffix = '_update_form'

class TaskUpdateView(UpdateView):
    model = Task
    template_name_suffix = '_update_form'
    form_class = TaskForm

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        task = get_object_or_404(Task, pk=pk)
        person = task.person
        task_form = TaskForm(instance=task, data=request.POST)
        if task_form.is_bound and task_form.is_valid():
            task_form.save()
            messages.add_message(request, messages.SUCCESS, 'Task Title: %s Task Description: %s updated.' %(task.title, task.description))
            return HttpResponseRedirect(reverse('planner:task_list', kwargs = {'pk': person.pk}))
        else:
            messages.error(request, task_form.errors)
            return HttpResponseRedirect(reverse('planner:task_update_form', kwargs = {'pk': pk}))

        

class MeetingUpdateView(TemplateView):
    template_name = 'planner/meeting_update_form.html'
    form_class = MeetingForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        meeting = get_object_or_404(Meeting,pk=self.kwargs['pk1'])
        person = get_object_or_404(Person,pk=self.kwargs['pk2'])
        context['person'] = person
        context['form'] = MeetingForm(instance=meeting)
        context['time_now'] = timezone.now()
        #assert False
        return context

    def post(self, request, *args, **kwargs):
        meeting_pk = self.kwargs['pk1']
        person_pk = self.kwargs['pk2']
        # retrieve the Meeting model instance based on meeting's pk
        meeting = get_object_or_404(Meeting, pk=meeting_pk)

        # create a MeetingForm based on meeting and form data
        meeting_form = MeetingForm(instance=meeting, data=request.POST)
        
        # convert date and time string

        form_date_only = date_string_to_date(request.POST['date'])
        date_today = datetime.now().date()

        form_time_only = time_string_to_time(request.POST['time'])
        time_now = datetime.now().time()

        if meeting_form.is_bound and meeting_form.is_valid():
            # check that meeting date and time is in the future
            
            if form_date_only < date_today or (form_date_only == date_today and form_time_only < time_now):
                messages.add_message(request, messages.ERROR, 'Meeting date %s and time %s should be in the future' %(form_date_only, form_time_only))
                return HttpResponseRedirect(reverse('planner:meeting_update_form', kwargs={'pk1': meeting_pk, 'pk2': person_pk}))
            else:
                meeting_form.save()
                messages.add_message(request, messages.SUCCESS, 'Meeting Title: %s Meeting Purpose: %s updated' %(meeting.title, meeting.purpose))
                return HttpResponseRedirect(reverse('planner:meeting_list', kwargs={'pk': self.kwargs['pk2']}))
        else:
            messages.error(request, meeting_form.errors)
            return HttpResponseRedirect(reverse('planner:meeting_update_form', kwargs={'pk1': meeting_pk, 'pk2': person_pk}))

        

class PersonDetailUpdateView(TemplateView):
    template_name = 'planner/person_detail_update_form.html'
    
    '''
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    '''
    '''
    Use get_context_data() to pass context to template
    '''
    '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = get_object_or_404(Person,pk=self.kwargs['pk'])
        context['person'] = person
        context['person_form'] = PersonForm(instance=person)
        context['bio_form'] = BioForm(instance=person.bio)
        context['email_form'] = EmailForm(instance=person.email)

        #assert False
        return context
    '''
    
    '''
    Use get() to render request 
    '''
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        person = get_object_or_404(Person, pk=pk)
        context = super().get_context_data(**kwargs)
        context['person'] = person
        context['person_form'] = PersonForm(instance=person)
        try:
            context['bio_form'] = BioForm(instance=person.bio)
            context['email_form'] = EmailForm(instance=person.email)
        except:
            bio = Bio.objects.create(person=person)
            email = Email.objects.create(person=person)
            context['bio_form'] = BioForm(instance=bio)
            context['email_form'] = EmailForm(instance=email)
        return render(request, self.template_name, context)
    

    '''
    This is a custom post method to save one of three forms
    -- PersonForm, BioForm or EmailForm
    on a template, person_detail_update_form.
    This method does not call form.save() but retrieves
    the values from the form and save them in the model
    '''
    def post(self, request, *args, **kwargs):
        # retrieve the primary key from url
        pk = self.kwargs['pk']

        # retrieve the Person model instance based on pk
        person = get_object_or_404(Person, pk=pk)

        # create a PersonForm based on person and form data
        person_form = PersonForm(instance=person, data=request.POST)

        # retrieve the Bio model instance based on person's pk
        bio = get_object_or_404(Bio, person__pk=pk)

        # create a BioForm based on bio and form data
        bio_form = BioForm(instance=bio, data=request.POST)

        # retrieve the Email model instance based on person's pk
        email = get_object_or_404(Email, person__pk=pk)

        # create a EmailForm based on email and form data
        email_form = EmailForm(instance=email, data=request.POST)

        # if the save_person button is pressed
        if 'save_person' in request.POST:
            if person_form.is_bound and person_form.is_valid():
                person_form.save()
                
                messages.add_message(request, messages.SUCCESS, "%s, %s, %s saved." %(person.name, person.age, person.status))
            else:
                messages.error(request, person_form.errors)

        # if the save_bio button is pressed
        elif 'save_bio' in request.POST:
            if bio_form.is_bound and bio_form.is_valid():
                bio_form.save()
                messages.add_message(request, messages.SUCCESS, '%s %s saved.' %(bio.bio, bio.image))
            else:
                messages.error(request, bio_form.errors)

        # if the save_email button is pressed
        elif 'save_email' in request.POST:
            if email_form.is_bound and email_form.is_valid():
                email_form.save()
                messages.add_message(request, messages.SUCCESS, '%s saved.' %(email.address))
            else:
                messages.error(request, email_form.errors)

        #assert False
        return HttpResponseRedirect(reverse('planner:person_detail_update_form', kwargs={'pk': self.kwargs['pk']}))


class TaskDeleteView(DeleteView):
    model = Task
    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        task = get_object_or_404(Task, pk=pk)
        person = task.person
        task.delete()
        messages.add_message(request, messages.SUCCESS, 'Task deleted.')
        return HttpResponseRedirect(reverse('planner:task_list', kwargs = {'pk': person.pk}))

class TaskCreateView(TemplateView):
    model = Task
    form_class = TaskForm
    #template_name_suffix = '_create_form'
    template_name = 'planner/task_create_form.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        person = get_object_or_404(Person, pk=pk)
        context = super().get_context_data(**kwargs)
        context['person'] = person
        #context['form'] = TaskForm(initial={'deadline':'year-month-date'})
        #context['form'] = TaskForm(initial={'deadline':date.today()})
        context['form'] = TaskForm()
        #assert False
        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        person = get_object_or_404(Person, pk=pk)
        task_form = TaskForm(data=request.POST)
        if task_form.is_bound and task_form.is_valid():
            new_task = task_form.save(commit=False)
            new_task.person = person
            new_task.save()
            task = get_object_or_404(Task, pk=new_task.pk)
            messages.add_message(request, messages.SUCCESS, 'Task Title: %s Task Description: %s added.' %(task.title, task.description))
        else:
            messages.error(request, task_form.errors)

        return HttpResponseRedirect(reverse('planner:task_list', kwargs = {'pk': person.pk}))

class MeetingDeleteView(TemplateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'planner/meeting_confirm_delete.html'

    def get_context_data(self, **kwargs):
        meeting_pk = self.kwargs['pk1']
        person_pk = self.kwargs['pk2']
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
        person = get_object_or_404(Person, pk=person_pk)

        context = super().get_context_data(**kwargs)
        context['person'] = person
        context['meeting'] = meeting
        #assert False
        return context

    def post(self, request, *args, **kwargs):
        meeting_pk = self.kwargs['pk1']
        person_pk = self.kwargs['pk2']
        meeting = get_object_or_404(Meeting, pk=meeting_pk)
        meeting.delete()

        # Query from the database and prepare message
        try:
            meeting = Meeting.objects.get(pk=meeting_pk)
            messages.error(request, meeting_form.errors)
        except ObjectDoesNotExist:
            messages.add_message(request, messages.SUCCESS, 'Meeting deleted successfully')

        return HttpResponseRedirect(reverse('planner:meeting_list', kwargs = {'pk': person_pk}))

class MeetingCreateView(TemplateView):
    model = Meeting
    form_class = MeetingForm
    template_name = 'planner/meeting_create_form.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        person = get_object_or_404(Person, pk=pk)
        context = super().get_context_data(**kwargs)
        context['person'] = person
        #context['form'] = MeetingForm(initial={'date':date.today(), 'time':datetime.now()})
        context['form'] = MeetingForm(initial={'participants':person, 'created_by':person})
        context['time_now'] = timezone.now()

        #assert False
        return context

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        person = get_object_or_404(Person, pk=pk)
        meeting_form = MeetingForm(data=request.POST)
        if meeting_form.is_bound and meeting_form.is_valid():
            form_date_only = date_string_to_date(request.POST['date'])
            date_today = datetime.now().date()

            form_time_only = time_string_to_time(request.POST['time'])
            time_now = datetime.now().time()

            if form_date_only < date_today or (form_date_only == date_today and form_time_only < time_now):
                messages.add_message(request, messages.ERROR, 'Meeting date %s and time %s should be in the future' %(form_date_only, form_time_only))
                return HttpResponseRedirect(reverse('planner:meeting_create_form', kwargs={'pk': pk}))
            else:
                new_meeting = meeting_form.save()
                meeting = get_object_or_404(Meeting, pk=new_meeting.pk)
                messages.add_message(request, messages.SUCCESS, 'Meeting Title: %s Meeting Purpose: %s added.' %(meeting.title, meeting.purpose))
                return HttpResponseRedirect(reverse('planner:meeting_list', kwargs = {'pk': person.pk}))
        else:
            messages.error(request, meeting_form.errors)
            return HttpResponseRedirect(reverse('planner:meeting_create_form', kwargs={'pk': pk}))


def logout_request(request):
    logout(request)
    #assert False
    messages.add_message(request, messages.SUCCESS, "You are successfully logged out")
    #return render(request, 'planner/logout.html', context)
    return render(request, 'planner/index.html')


# This class-based view is a response to the Contact Form validation
class ThanksView(TemplateView):
    template_name = 'planner/thanks.html'
    
    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = self.kwargs['success']
        context['visitor'] = self.kwargs['visitor']
        
        return render(request, self.template_name, context)

# This class-based view corresponds to the ContactForm in forms.py
class ContactView(FormView):
    template_name = 'planner/contact.html'
    form_class = ContactForm
    #success_url = '/thanks/'
    success_url = reverse_lazy('planner:contact')

    # This method will validate the form with Simple Captcha
    def is_valid(self, form):
        if form.is_valid():
            human = True    # set for Simple Captcha

    # This method is called when valid form data has been posted
    def form_valid(self, form):

        response = 0
        request = requests.get(form.cleaned_data['linkedin'])
        if request.status_code == 200:
            response = form.send_email()

            #response = 0  # testing
            if response:
                messages.add_message(self.request, messages.SUCCESS, "Thank you for your message. It has been sent.")
            else:
                messages.error(self.request, 'Thank you for your message. There is a problem with the transmission. We apologize for the inconvenience, so please try again at a later time.')
            """
            # Redefine 'success_url' to pass data back to the success_url
            #self.success_url = reverse('planner:thanks', kwargs={'visitor':form.cleaned_data['name'], 'success':response})
            """
            # Return a Http Response
            return super().form_valid(form)
        else:
            messages.error(self.request, 'LinkedIn profile cannot be found. If you only have a private LinkedIn profile, please put the private url in the message text box and change the LinkedIn profile text input to simply http://linkedin.com. Thank you and please try again.')
            # Return a Http Response with filled-in form
            return super().form_invalid(form)

class PersonCreateView(TemplateView):
    model = Person
    fields = ['name', 'status', 'age']
    #fields = '__all__'
    #template_name_suffix = '_detail_create_form'
    template_name = 'planner/person_detail_create_form.html'

    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        context = super().get_context_data(**kwargs)
        context['user'] = user
        try:
            person = get_object_or_404(Person, user=pk)
            context['person_form'] = PersonForm(instance=person)
        except:
            context['person_form'] = PersonForm()
        try:
            bio = Bio.objects.get(person=user.person)
            context['bio_form'] = BioForm(instance=bio)
        except:
            bio = Bio(image=settings.DEFAULT_IMAGE_URL)
            context['bio_form'] = BioForm(instance=bio)
        try:
            email = Email.objects.get(person=user.person)
            context['email_form'] = EmailForm(instance=email)
        except:
            context['email_form'] = EmailForm()
        return render(request, self.template_name, context)
    

    '''
    This is a custom post method to save one of three forms
    -- PersonForm, BioForm or EmailForm
    on a template, person_detail_create_form.
    This method does not call form.save() but retrieves
    the values from the form and save them in the model
    '''
    def post(self, request, *args, **kwargs):
        # retrieve the primary key from url
        pk = self.kwargs['pk']

        # retrieve the User model instance based on pk
        user = get_object_or_404(User, pk=pk)

        # create a Person model instance with user
        person = Person.objects.create(user = user)

        # create a PersonForm based on person and form data
        person_form = PersonForm(instance=person, data=request.POST)

        # creae a Bio model instance based on person
        bio = Bio(person = person)

        # create a BioForm based on bio and form data
        bio_form = BioForm(instance=bio, data=request.POST)

        # create an Email model instance based on person
        email = Email(person=person)

        # create a EmailForm based on email and form data
        email_form = EmailForm(instance=email, data=request.POST)

        # if the save_person button is pressed
        if 'save_person' in request.POST:
            if person_form.is_bound and person_form.is_valid():
                person_form.save()
                
                messages.add_message(request, messages.SUCCESS, "%d %s %d %s" %(person.pk, person.name, person.age, person.status))
            else:
                messages.error(request, person_form.errors)

        if 'save_bio' in request.POST:
            if bio_form.is_bound and bio_form.is_valid():
                bio_form.save()
                messages.add_message(request, messages.SUCCESS, '%d %s %s saved' %(bio.person.pk, bio.bio, bio.image))
            else:
                messages.error(request, bio_form.errors)

        if 'save_email' in request.POST:
            if email_form.is_bound and email_form.is_valid():
                email_form.save()
                messages.add_message(request, messages.SUCCESS, '%d %s' %(email.person.pk, email.address))
            else:
                messages.error(request, email_form.errors)

        #assert False
        return HttpResponseRedirect(reverse('planner:person_detail_create_form', kwargs={'pk': self.kwargs['pk']}))

def github_login(request):
    #authorization_url, state = github.authorization_url(authorization_base_url)
    #assert False
    # https://github.com/login/oauth/authorize?response_type=code&client_id=<client_id>&state=<state>
    params = {
      'response_type': 'code',
      'client_id': client_id,
      'state': secrets.token_urlsafe(16),
    }
    req = PreparedRequest()
    req.prepare_url(authorization_base_url, params)
    print('authorization_url', req.url)
    return HttpResponseRedirect(req.url)

def github_callback(request):
    data = request.GET
    code = data['code']
    state = data['state']

    # returns the URL that calls this function, e.g. https://aws.djangodemo.com/auth/callback/?code=<code>&state=<state>
    response = request.build_absolute_uri()
    print("response = %s, code=%s, state=%s" %(response, code, state))

    # fetch the token from GitHub's API at token_url
    github.fetch_token(token_url, client_secret=client_secret,authorization_response=response)

    # returns a 'requests.get(url)' object
    get_result = github.get('https://api.github.com/user')

    json_dict  = get_result.json()

    dict = {
        'login': json_dict['login'],
        'name': json_dict['name'],
        'bio': json_dict['bio'],
        'blog': json_dict['blog'],
        'email': json_dict['email'],
        'avatar_url': json_dict['avatar_url'],
    }

    context = {'profile': json_dict}

    # create a User and Person for this profile
    try:
        user = User.objects.get(username=json_dict['login'])
        messages.add_message(request, messages.DEBUG, "User %s already exists, Authenticated? %s" %(user.username, user.is_authenticated))
        print("User %s already exists, Authenticated %s" %(user.username, user.is_authenticated))
        context['user'] = user
        context['person'] = user.person
        print("Person %s already exists" %(user.person.name))

        # remember to login to DJango
        login(request, user)
    except:
        user = User.objects.create_user(json_dict['login'], json_dict['email'])
        messages.add_message(request, messages.DEBUG, "User %s is created, Authenticated %s?" %(user.username, user.is_authenticated))
        context['user'] = user
        name = json_dict['name'] if json_dict['name'] else user.username
        person = Person.objects.create(name=name, user=user)
        bio = json_dict['bio'] if json_dict['bio'] else 'No bio yet.'
        bio = Bio.objects.create(bio=bio, image=json_dict['avatar_url'], person=person)
        address = json_dict['email'] if json_dict['email'] else user.username+'@djangoschool.com'
        email = Email.objects.create(address=address, person=person)
        context['person'] = person
        print("User %s is created, Authenticated %s, Person %s is created" %(user.username, user.is_authenticated, person.name))

        # remember to login to DJango
        login(request, user)

    return render(request, 'planner/index.html', context)


# debugging only
def login_request(request):
    return render(request, 'planner/github_login.html')
