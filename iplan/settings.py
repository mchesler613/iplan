"""
Django settings for tmp project.

Generated by 'django-admin startproject' using Django 3.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from pathlib import Path
from dotenv import dotenv_values
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
#print ("BASE_DIR", BASE_DIR)

ENV_FILE=str(Path(BASE_DIR)) + '/iplan.env'
myvars = dotenv_values(ENV_FILE)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = myvars['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False #True

#ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
ALLOWED_HOSTS = ['54.156.224.175', 'aws.djangodemo.com']


# Application definition

#'django_registration',
INSTALLED_APPS = [
    'captcha',
    'django_extensions',
    'planner.apps.PlannerConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'iplan.urls'

#'DIRS': [str(BASE_DIR.joinpath('iplan/templates'))],
# DIRS': [],
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(BASE_DIR.joinpath('iplan/templates'))],  # <==
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'iplan.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/opt/bitnami/projects/static'
'''
The following checks verify that django.contrib.staticfiles is correctly configured:
staticfiles.E001: The STATICFILES_DIRS setting is not a tuple or list.
staticfiles.E002: The STATICFILES_DIRS setting should not contain the STATIC_ROOT setting.
staticfiles.E003: The prefix <prefix> in the STATICFILES_DIRS setting must not end with a slash.
'''
STATICFILES_DIRS = [
    str(BASE_DIR.joinpath('static')),
]

# Redirect to URL after login (defaults to /accounts/profile)
LOGIN_REDIRECT_URL = '/iplan/'

# Redirect to URL for login (defaults to /accounts/login)
LOGIN_URL = '/planner/login'

# Django-registration settings
ACCOUNT_ACTIVATION_DAYS = 1

# send_mail settings
SITE_URL = 'aws.djangodemo.com'
'''
To export EMAIL_HOST_PASSWORD, type at the terminal
$ export EMAIL_HOST_PASSWORD='Your password here'
Restart the Django server from the terminal
$ python manage.py runserver
'''
# Settings for Django send_mail()
EMAIL_HOST = myvars['EMAIL_HOST'] 
EMAIL_PORT = 587
EMAIL_HOST_USER = myvars['EMAIL_HOST_USER'] 
EMAIL_USE_SSL = False
EMAIL_USE_TSL = True
EMAIL_HOST_PASSWORD = myvars['EMAIL_HOST_PASSWORD']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SSL
SECURE_SSL_REDIRECT = True
#SECURE_SSL_HOST = SITE_URL
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True

TIME_INPUT_FORMATS = ('%I:%M %p',)

# OAuth Settings
GITHUB_OAUTH_CLIENT_ID = myvars['GITHUB_OAUTH_CLIENT_ID']
GITHUB_OAUTH_SECRET = myvars['GITHUB_OAUTH_SECRET']
GITHUB_OAUTH_CALLBACK_URL = myvars['GITHUB_OAUTH_CALLBACK_URL']
GITHUB_OAUTH_SCOPES = myvars['GITHUB_OAUTH_SCOPES']

# To comply with warnings for 3.2.3+
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
