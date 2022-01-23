# Cal
Calendar app for garbage collection etc. with ical api 

Although i created this django app to manage the local garbage collection any kind of events can be managed.


# Run
To run the app create a virtual environent and install dependencies from requirements.txt

```
pip install -U -r requirements.txt
```

Create a localsettings.py in the cal directory right next to the settings.py file. It should include a 
new generated secret key in the "SECRET_KEY setting , the "ALLOWED_HOSTS", "DEBUG" and "DATABASE" setting.

You can copy from the following template:

```
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'your-new-generated-secret-key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'cal.db'),
    }
}
```

Create the database schemas with

```
python manage.py migrate
```

Start the development server with

```
python manage.py runserver
```
