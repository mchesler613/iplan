from django.urls import path
from planner.views import github_login, login_request, github_callback, IndexView, PersonDetailView, PersonListView, TaskListView, MeetingListView, PersonUpdateView, BioUpdateView, EmailUpdateView, PersonDetailUpdateView, TaskUpdateView, MeetingUpdateView, TaskDeleteView, TaskCreateView, MeetingDeleteView, MeetingCreateView, logout_request, ContactView, ThanksView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

# used for namespacing URL names
# https://docs.djangoproject.com/en/3.1/intro/tutorial03/#namespacing-url-names
app_name = 'planner'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('person/<int:pk>/', PersonDetailView.as_view(), name='person_detail'),
    path('people/', PersonListView.as_view(), name='people_list'),
    path('person/tasks/<int:pk>/', TaskListView.as_view(), name='task_list'),
    path('person/meetings/<int:pk>/', MeetingListView.as_view(), name='meeting_list'),
    path('person/edit/<int:pk>/', PersonUpdateView.as_view(), name='person_update_form'),
    path('bio/edit/<int:pk>/', BioUpdateView.as_view(), name='bio_update_form'),
    path('email/edit/<int:pk>/', EmailUpdateView.as_view(), name='email_update_form'),
    path('person/<int:pk>/edit', login_required(PersonDetailUpdateView.as_view()), name='person_detail_update_form'),
    path('task/<int:pk>/edit', TaskUpdateView.as_view(), name='task_update_form'),
    path('meeting/<int:pk1>/person/<int:pk2>/edit', MeetingUpdateView.as_view(), name='meeting_update_form'),
    path('task/<int:pk>/delete', TaskDeleteView.as_view(), name='task_confirm_delete'),
    path('task/<int:pk>/create', TaskCreateView.as_view(), name='task_create_form'),
    path('meeting/<int:pk1>/person/<int:pk2>/delete', MeetingDeleteView.as_view(), name='meeting_confirm_delete'),
    path('meeting/<int:pk>/create', MeetingCreateView.as_view(), name='meeting_create_form'),
    path('logout/', logout_request, name='logout'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('thanks/<str:visitor>/<int:success>', ThanksView.as_view(), name='thanks'),
    path('login_request/', login_request, name='login_request'),
    path('github_login/', github_login, name='github_login'),
    path('github_callback/', github_callback, name='github_callback'),
]
