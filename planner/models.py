from django.db import models
from datetime import date, timedelta, datetime
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from dateutil.parser import parse

# Person has one-to-many relationship with Task & Meeting
# Person has one-to-one relationship with Email
class Person(models.Model):
    STATUS = [
        ('AWAY', 'I am away'),
        ('BUSY', 'I am busy'),
        ('MEETING', 'I am in a meeting'),
        ('IDLE', 'I am available')
    ]

    # define attributes here
    name = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=STATUS, default='IDLE')
    age = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    # define metadata here
    class Meta:
        verbose_name_plural = 'people'

    # define methods here
    def get_absolute_url(self):
        return reverse('planner:person_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def all_task_count(self):
        # return the number of tasks for this person
        self.tasks_count = self.task_set.count()
        return self.tasks_count

    def all_meeting_count(self):
        # return the number of meetings for this person
        return self.meeting_set.count()

    # return all tasks
    def all_tasks(self):
        return self.task_set.all()

    # return all expired tasks
    def expired_tasks(self):
        return self.task_set.filter(deadline__lt=date.today())

    # return all tasks due today
    def tasks_due_today(self):
        return self.task_set.filter(deadline=date.today())

    # return all pending tasks
    def pending_tasks(self):
        return self.task_set.filter(deadline__gte=date.today()).order_by('deadline', 'title')

    # return all future tasks
    def future_tasks(self):
        return self.task_set.filter(deadline__gt=date.today()).order_by('deadline', 'title')

    # return all meetings scheduled for today
    def meetings_today(self):
        return self.meeting_set.filter(participants__name=self.name).filter(date=date.today())

    # return all incoming meetings for today, including those happening now
    def incoming_meetings_today(self):
        return self.meeting_set.filter(participants__name=self.name).filter(date=date.today()).filter(time__gte=datetime.now())

    # return all future meetings beyond today
    def future_meetings(self):
        return self.meeting_set.filter(participants__name=self.name).filter(date__gt=date.today())

    # return all expired meetings
    def expired_meetings(self):
        return self.meeting_set.filter(participants__name=self.name).filter(date__lt=date.today())

    def my_status(self):
        # if I'm in a meeting right now, status='MEETING'
        # compare current time with end of meeting time
        meetings = self.meetings_today()
        for meeting in meetings:
            start_time = datetime.combine(meeting.date,meeting.time)
            end_time = timedelta(minutes=meeting.duration) + start_time
            time_now = datetime.now()
            if time_now.time() > start_time.time() and time_now.time() < end_time.time():
                self.status = 'MEETING'
                self.save()
                return self.status

        # if I've tasks due today, status='BUSY'
        if self.status != 'AWAY' and len(self.tasks_due_today()):
            self.status = 'BUSY'
            self.save()

        return self.status

# Bio has a one-to-one relationship with Person, but can be NULL
class Bio(models.Model):
    # define attributes here
    bio = models.TextField()
    image = models.URLField()
    person = models.OneToOneField(Person, on_delete=models.CASCADE)
    # define methods here
    def __str__(self):
        return self.bio

    # define methods here
    def get_absolute_url(self):
        return reverse('planner:person_detail', kwargs={'pk': self.pk})



# Email has one-to-one relationship with Person
class Email(models.Model):
    # define attributes here
    address = models.EmailField(verbose_name='Email')
    person = models.OneToOneField(Person, on_delete=models.CASCADE)

    # override the Manager attribute
    # instances = models.Manager()

    # define metadata here

    # define methods here
    def __str__(self):
        return self.address

    # define methods here
    def get_absolute_url(self):
        return reverse('planner:person_detail', kwargs={'pk': self.pk})

# Task has many-to-one relationship with Person
class Task(models.Model):
    # define attributes here
    title = models.CharField(max_length=30)
    description = models.TextField()
    deadline = models.DateField(default=timezone.now)
    person = models.ForeignKey(Person, on_delete=models.CASCADE,null=True)

    # define metadata here
    ordering = ['deadline', 'title']

    # define methods here
    def __str__(self):
        return ("%s, %s, %s, %s\n" %(self.person, self.title, self.description, self.deadline.strftime('%c')))

    # define methods here
    def get_absolute_url(self):
        return reverse('planner:person_detail', kwargs={'pk': self.person.pk})

# Meeting has many-to-many relationship with Person
# Meeting also has a meny-to-one relationship 'created_by' with Person
class Meeting(models.Model):
    # define attributes here
    title = models.CharField(max_length=30)
    purpose = models.TextField()
    date = models.DateField(default=timezone.now)
    time = models.TimeField()  #default=datetime.now()
    created_by = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='created_by')

    # duration of meeting in number of minutes
    duration = models.IntegerField(default=30)

    # the participants in the meeting
    participants = models.ManyToManyField(Person)

    # define metadata here
    class Meta:
        ordering = ['date', 'time']

    # define methods here
    def __str__(self):
        return '%s, %s, %s, %s, %s with %s' %(self.title, self.purpose, self.date.strftime('%a'), self.date, self.time, self.participants.all())

    # return participant count
    def participant_count(self):
        return self.participants.count()

