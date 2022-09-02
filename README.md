# Django Social Authentication

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/) 

## Install social-auth-app-django social authentication module
```console
pip install social-auth-app-django
```

## General Settings

#### Update project ```settings.py``` file
Here, `accounts` is my django app for authentication. 

Also, `accounts.middleware.CustomSocialAuthExceptionMiddleware` is for scenario: if user is already logged in through one social auth and tries to logg-in again then this middleware will catch `AuthAlreadyAssociated` this error and redirects to LOGIN_URL page. 

```console
INSTALLED_APPS = [
    ...
    'accounts',
    'social_django',
    ....
]

...

MIDDLEWARE = [
    ...
    'accounts.middleware.CustomSocialAuthExceptionMiddleware',
    ...
]

...

TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

...

AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

...

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

...

SOCIAL_AUTH_RAISE_EXCEPTIONS = False

SOCIAL_AUTH_GITHUB_KEY = os.environ.get('SOCIAL_AUTH_GITHUB_KEY')
SOCIAL_AUTH_GITHUB_SECRET = os.environ.get('SOCIAL_AUTH_GITHUB_SECRET')
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']

SOCIAL_AUTH_TWITTER_KEY = os.environ.get('SOCIAL_AUTH_TWITTER_KEY')
SOCIAL_AUTH_TWITTER_SECRET = os.environ.get('SOCIAL_AUTH_TWITTER_SECRET')

SOCIAL_AUTH_FACEBOOK_KEY = os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
  'fields': 'id, name, email, age_range'
}

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

```

This KEY and SECRET is obtained from respective social auth's developer console.
For more information about [how to get credentials?](https://creativeminds.helpscoutdocs.com/article/551-social-login-how-to-create-google-api-client-id-and-client-secret)

[Optional]
```console
AUTH_USER_MODEL = 'accounts.User'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)
```


### Update project ```urls.py``` file
This is path for integrating social authentication.

```console
urlpatterns = [
    path('oauth/', include('social_django.urls', namespace='social')),
    ...
]
```

#### Update in ```html``` file
Paste this link in any of html page for authenticating through social auth.

```console
<a href="{% url 'social:begin' 'github' %}">GitHub</a>
<a href="{% url 'social:begin' 'facebook' %}">Facebook</a>
<a href="{% url 'social:begin' 'twitter' %}">Twitter</a>
<a href="{% url 'social:begin' 'google-oauth2' %}">Google</a>
```

## Development

### Migrating Databases

When changing models, we have to update the database. Migrations help us track changes.

```console
python manage.py makemigrations
python manage.py migrate
```

### Running Server

```console
python manage.py runserver
```


# Todo Project- Django Rest Framework

## Clone Project
```console
git clone https://gitlab.com/inexture-python/pythonlearning/todo_social_auth_parth.git

OR 

git clone https://github.com/ParthD971/Django-Todo-Project.git

```
Current updated code is in `dev` branch. To change branch `git checkout dev`.

## Install requirements.txt
```console
pip install -r requirements.txt
```

## Setup Redis
See full installation and commands [here.](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04)
### Install Redis
```console
sudo apt install redis-server
```

### Start Redis
```console
redis-server
```

## Development

### Migrating Databases

When changing models, we have to update the database. Migrations help us track changes.

```console
python manage.py makemigrations
python manage.py migrate
```

### Running Server

```console
python manage.py runserver
```

### Running Celary

```console
celery -A core worker --pool=solo -l info
```

### Running Celary-Beat

```console
celery -A core beat -l INFO
```

## Swagger Documentation

```console
http://localhost:8000/api/doc/
```

[Postman Api Documentation](https://documenter.getpostman.com/view/20754219/VUxRPSH4)

## Add Configurations to `.env` file in root directory.
```console
PASSWORD_RESET_TIMEOUT=3600
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_emails_password

SOCIAL_AUTH_GITHUB_KEY=your_key
SOCIAL_AUTH_GITHUB_SECRET=your_secret_key

SOCIAL_AUTH_FACEBOOK_KEY=your_key
SOCIAL_AUTH_FACEBOOK_SECRET=your_secret_key

SOCIAL_AUTH_TWITTER_KEY=your_key
SOCIAL_AUTH_TWITTER_SECRET=your_secret_key

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your_key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your_secret_key


REMINDER_SCHEDULE_DURATION=3600

CACHE_TTL=120
BUFFER_TIME=3600
```


