"""
Django settings for sample_site project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')k@ykqs^15v(sfl7vumv4uyf^em#p_9t5-hphqrk)1cg@xr81w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'uploads', 'public'))
MEDIA_URL = '/media/'

# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'app',
    'awl',
    'yacon',
    'treebeard',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'yacon.pagination.middleware.PaginationMiddleware',
)

TEMPLATES = [{
    'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[
        os.path.abspath(os.path.join(BASE_DIR, 'templates')),
    ],
    'APP_DIRS':True,
    'OPTIONS':{
        'debug':DEBUG,
        'context_processors':[
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
            'yacon.context_processors.processor',
        ],
    },
}]


STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.abspath(os.path.join(BASE_DIR, 'static')),
)

ROOT_URLCONF = 'sample_site.urls'

WSGI_APPLICATION = 'sample_site.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Logging
#LOGGING = {
#    'version': 1,
#    'disable_existing_loggers': True,
#    'formatters': {
#        'escaped': {
#            'format':'\033[1m%(funcName)s\033[0m: %(message)s',
#        },
#    },
#    'handlers': {
#        'default': {
#            'level':'DEBUG',
#            'class':'logging.StreamHandler',
#            'formatter':'escaped',
#        },
#    },
#    'loggers': {
#        '': {
#            'handlers':['default'],
#            'propagate': False,
#            'level':'DEBUG',
#        },
#    },
#}

# YACON Specific Config

YACON = {
    'site':{
        'private_upload':os.path.abspath(os.path.join(BASE_DIR, 'uploads', 
            'private')),
        'private_upload_url':'/pmedia/',
    },
    'custom': {
        'page_context':'app.dynamic.page_context',
    },
}
