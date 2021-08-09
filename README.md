# iplan
## Dependencies
```
$ pip install python-dotenv
$ pip install django-simple-captcha
$ pip install django-extensions
$ pip install python-dateutil
$ pip install requests
$ pip install requests_oauthlib
```
## Define the environment file for python-dotenv in project settings
In **iplan/settings.py** file, define the variable `ENV_FILE` which is the location of the environment file settings for your `dotenv` package:
```
ENV_FILE = str(Path(BASE_DIR)) + 'environment_file_name'
```

## Migrate the database
```
$ python manage.py makemigrations planner
$ python manage.py migrate planner
```

## Populate the database
```
$ python manage.py runscript populate
```

## Run the server
```
$ python manage.py runserver
```

# Deploy on AWS
1. Clone project at **/opt/bitnami/projects** with `git clone https://github.com/mchesler613/iplan.git`
2. `cd` to the `iplan` directory. 
3. Install the dependencies above with `sudo`.
4. Edit the project, **iplan/wsgi.py** file:
```
import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append('/opt/bitnami/projects/iplan')
os.environ['PYTHON_EGG_CACHE'] = '/opt/bitnami/projects/iplan/egg_cache'
os.environ['DJANGO_SETTINGS_MODULE'] = 'iplan.settings'

application = get_wsgi_application() 
```

5. Make a `conf` directory at the root project.
```
$ mkdir conf
```
6. Edit the **conf/httpd-app.conf** file.
```
<IfDefine !DJANGOSTACK_LOADED>
  Define IS_DJANGOSTACK_LOADED
WSGIDaemonProcess wsgi-djangostack   processes=2 threads=15    display-name=%{GROUP}
</IfDefine>

<Directory "/opt/bitnami/projects/iplan/iplan">
    Options +MultiViews
    AllowOverride All
    <IfVersion >= 2.3>
Require all granted
    </IfVersion>

WSGIProcessGroup wsgi-djangostack

WSGIApplicationGroup %{GLOBAL}
</Directory>

Alias /iplan/static "/opt/bitnami/python/lib/python3.8/site-packages/django/contrib/admin/s
tatic/"

WSGIScriptAlias /iplan '/opt/bitnami/projects/iplan/iplan/wsgi.py'
```

7. Edit the **conf/httpd-prefix.conf** file.
```
Include '/opt/bitnami/projects/iplan/conf/httpd-app.conf'
```

8. Edit **/opt/bitnami/apache2/conf/bitnami/bitnami.conf** as `sudo`.
```
<VirtualHost _default_:80>
    WSGIScriptAlias /iplan /opt/bitnami/projects/iplan/iplan/wsgi.py
    Alias /static /opt/bitnami/projects/iplan/static
    
    <Directory /opt/bitnami/projects/iplan/static>ration not p
        Require all granted
    </Directory>
    
    <Directory /opt/bitnami/projects/iplan>
        AllowOverride all
        Require all granted
        Options FollowSymlinks
    </Directory>
 
    DocumentRoot /opt/bitnami/projects/iplan
</VirtualHost>
 
Include "/opt/bitnami/apache/conf/bitnami/bitnami-ssl.conf"
```

9. Edit the **iplan/prod_settings.py** file for production.
```
# Static File settings
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/bitnami/projects/iplan/static'

# Redirect to URL after login (defaults to /accounts/profile)
LOGIN_REDIRECT_URL = '/iplan/planner/'

# Redirect to URL for login (defaults to /accounts/login)
LOGIN_URL = '/planner/login'

# WSGI settings
ALLOWED_HOSTS = ['yourdjangosite.com']

# Settings for Django send_mail()
SITE_URL = 'yourdjangosite.com'
ENV_FILE=str(Path(BASE_DIR)) + 'your_environment_file_name'
from dotenv import dotenv_values
myvars = dotenv_values(ENV_FILE)
EMAIL_HOST = myvars['EMAIL_HOST'] 
EMAIL_PORT = 587
EMAIL_HOST_USER = myvars['EMAIL_HOST_USER'] 
EMAIL_USE_SSL = False
EMAIL_USE_TSL = True
EMAIL_HOST_PASSWORD = myvars['EMAIL_HOST_PASSWORD']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```
10. Add the sensitive variables in the file defined in the variable `ENV_FILE` in **settings.py**.
```
EMAIL_HOST='your_email_host'
EMAIL_HOST_USER='your_email_host_user'
EMAIL_HOST_PASSWORD='your_email_host_user_password'
```
12. Change permissions on database file, **iplan/db.sqlite3**
```
sudo chmod g+w . ./db.sqlite3
sudo chgrp daemon . ./db.sqlite3
```

11. Start the Apache server
```
sudo /opt/bitnami/ctlscript.sh restart apache
```

12. Point browser to `yourdjangosite.com/iplan/planner`
13. Create a superuser 
```
$ python manage.py createsuperuser
```
15. Test the admin login at `http://yourdangosite.com/iplan/planner/admin` and login as superuser

## Server Timezone
This version of iPlan assumes everyone is on the same timezone. To set the timezone for your server, visit this [link](https://it.playswellwithflavors.com/2020/03/25/bitnami-set-timezone/) for instructions.

## Cron jobs
+ Setting cronjobs. The file to edit is **/etc/cron.d/your_file_name**. See this [source](https://forums.aws.amazon.com/thread.jspa?threadID=126088).
+ Use the absolute path for the commands inside your script and crontab entry. Instead of 
```
python manage.py [command]
```
use 
```
/opt/bitnami/python/bin/python manage.py [command]
``` 
For example:
```
30 0 * * * bitnami /opt/bitnami/projects/iplan/check.sh
```

## Static Files
+ Add a definition for `STATIC_URL` and `STATIC_ROOT` in **iplan/settings.py**. For example:
```py
# Static File settings
STATIC_URL = '/static/'
STATIC_ROOT = '/opt/bitnami/projects/iplan/static'
```
The run `python manage.py collectstatic` to copy the Admin and other static files to the defined `STATIC_ROOT` directory.

+ Add an `alias` in **/opt/bitnami/apache2/conf/bitnami/bitnami.conf** to set the path to the static files. For example:
```
    Alias /static /opt/bitnami/projects/iplan/static
    
    <Directory /opt/bitnami/projects/iplan/static>
        Require all granted
    </Directory>
```


