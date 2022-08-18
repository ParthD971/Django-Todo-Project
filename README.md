# Django Social Authentication

## General Settings



#### Update project ```settings.py``` file

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

```console
urlpatterns = [
    path('oauth/', include('social_django.urls', namespace='social')),
    ...
]
```

#### Update in ```html``` file

```console
<a href="{% url 'social:begin' 'github' %}">GitHub</a>
<a href="{% url 'social:begin' 'facebook' %}">Facebook</a>
<a href="{% url 'social:begin' 'twitter' %}">Twitter</a>
<a href="{% url 'social:begin' 'google-oauth2' %}">Google</a>
```

### Development

#### Running Server

```console
python manage.py runserver
```

#### Migrating Databases

When changing models, we have to update the database. Migrations help us track changes.

```console
python manage.py makemigrations
python manage.py migrate
```
