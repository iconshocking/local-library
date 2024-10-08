"""
Django settings for library project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

from corsheaders.defaults import default_headers, default_methods

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ENV = os.environ.get("DJANGO_ENV", "dev")
DEBUG = os.environ.get("DJANGO_DEBUG", "") == "True"
PROD = os.environ.get("DJANGO_ENV", "") == "prod"


SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-^*68rdzx%42l%eoyoaf!1oa=emro+b7*i&6%^%ba3!0d_i62w5",
)

HTTPS_REQUIRED = os.environ.get("NGINX_LISTEN_PORT", "80") == "443"

# defines the IP addresses or domain names that can be used to access the Django web application
ALLOWED_HOSTS = [
    "127.0.0.1",
    "django",
    "cshock-library-nginx.fly.dev",
    "playground.fly-io.cshock.tech",
]
# only set this if you need to allow forms submitted from other sub/domains (like an API) - it is
# safest by default because it requires that 'Origin' header matches the 'Host' header on
# POST/unsafe requests (which is only true on same-origin requests)
# - NOTE: if 'Origin' is not present, checks that the 'Referer' header matches the 'Host' header
# - NOTE: non-browser requests are not a security risk for this because they have no cookies and so
# can't perform CSRF attacks
CSRF_TRUSTED_ORIGINS = []

# used by the 'django-cors-headers' package to automate CORS headers
CORS_ALLOWED_ORIGINS = []
# same as not defining it at all
CORS_ALLOW_METHODS = [
    *default_methods,
]
# must define any headers you want to allow (purpose of this header is to make sure server is aware
# of any special headers that are being sent, so it can decide whether to allow them or not)
CORS_ALLOW_HEADERS = [
    *default_headers,
]
# purpose of this is to default preserve behavior from pre-CORS days where the server would not
# expose any of the response headers
CORS_EXPOSE_HEADERS = []  # default
# whether cookies are included
CORS_ALLOW_CREDENTIALS = False  # default

if DEBUG:
    # hack to allow debug toolbar to work with Docker since the IP calculation seems to fail every
    # few months - year (and the current solution in the library is not working)
    DEBUG_TOOLBAR_CONFIG = {"SHOW_TOOLBAR_CALLBACK": lambda request: True}

# only send over HTTPS
CSRF_COOKIE_SECURE = HTTPS_REQUIRED
SESSION_COOKIE_SECURE = HTTPS_REQUIRED

# something low to make sure it doesn't break anything
SECURE_HSTS_SECONDS = 600 if HTTPS_REQUIRED else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = HTTPS_REQUIRED
# ONLY enable this if you are ABSOLUTELY sure that your site will only be served over HTTPS (the
# minimum requirement is 1 year, so this is a very strong commitment)
SECURE_HSTS_PRELOAD = False

# should have this on in production
SECURE_SSL_REDIRECT = HTTPS_REQUIRED
# only use if behind a reverse proxy that strips any client-set header and sets
# 'X-Forwarded-Proto' manually when connection is HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# used for prometheus scraping
SECURE_REDIRECT_EXEMPT = ["^metrics/$"]

# this is the same order that templates/statics are searched for
INSTALLED_APPS = [
    "core.apps.AllAuthCompatibleAdminConfig",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "allauth",
    "allauth.account",
    # if you want to use social authentication
    # "allauth.socialaccount",
    # "allauth.socialaccount.provicers.xxx",
    # required to support permissions associated with models and generic relation fields
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "catalog.apps.CatalogConfig",
    "core.apps.CoreConfig",
    "crispy_forms",
    "crispy_bootstrap5",
    # required to serve statics when using 'runserver' command and run 'collectstatic' command
    "django.contrib.staticfiles",
    # deletes old file when a new file name is uploaded for a model field (probably avoid using
    # this, or at least heavily configure, if you are performing more complex or persistent media
    # storage)
    "django_cleanup.apps.CleanupConfig",
    "django_prometheus",
] + (
    [
        "debug_toolbar",
        "django_browser_reload",
    ]
    if DEBUG
    else []
)


USING_WHITENOISE = os.environ.get("USE_WHITENOISE", "False") == "True"


def middleware_list():
    middleware = []

    middleware.append("django_prometheus.middleware.PrometheusBeforeMiddleware")

    # debug_toolbar must come as soon as possible in the middleware list, but behind any encoding
    # middleware (like gzip)
    if DEBUG:
        middleware.append("debug_toolbar.middleware.DebugToolbarMiddleware")

    middleware.append("django.middleware.security.SecurityMiddleware")

    if USING_WHITENOISE:
        middleware.append("whitenoise.middleware.WhiteNoiseMiddleware")

    middleware.extend(
        [
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            "django.contrib.admindocs.middleware.XViewMiddleware",
            "allauth.account.middleware.AccountMiddleware",
            "django_browser_reload.middleware.BrowserReloadMiddleware",
        ]
    )

    middleware.append("django_prometheus.middleware.PrometheusAfterMiddleware")

    return middleware


MIDDLEWARE = middleware_list()

# Set this BEFORE initial DB migrations because it is very hard to switch to a different user model
AUTH_USER_MODEL = "core.User"
AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of allauth
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
# for social accounts in'allauth
SOCIALACCOUNT_PROVIDERS = []
# ACCOUNT_RATE_LIMITS allows configuring allauth rate limits for auth-related actions, which already
# has reasonable defaults. This uses the cache, so if using per-process cache, the limits will be
# higher than expected since the user gets hopped between processes

# can also be set to "email" or "username_email"
ACCOUNT_AUTHENTICATION_METHOD = "username"  # default
# ACCOUNT_ADAPTER allows customizing the behavior of allauth with a custom adapter

# used for generating URLs related to allauth, like password reset
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http" if not HTTPS_REQUIRED else "https"
# whether authed users should be redirected to LOGIN_REDIRECT_URL
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = True  # default
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/core/accounts/login/"
# prevents users from having more than one email associated with their account (other than a
# temporary one that must be verified when requesting to change the email)
ACCOUNT_CHANGE_EMAIL = True
# ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL defaults to LOGIN_URL and
# ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL defaults to LOGIN_REDIRECT_URL
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3  # default
# email links are confirmed via HMAC key validation, so no DB state required

# sends an email when account changes are made; defaults to false
ACCOUNT_EMAIL_NOTIFICATIONS = True
ACCOUNT_EMAIL_REQUIRED = True  # defauls to false
ACCOUNT_EMAIL_VERIFICATION = (
    "none"  # default is "optional"; can also be "none" or "mandatory"
)
ACCOUNT_EMAIL_SUBJECT_PREFIX = "cshock.tech Library: "
# whether emails are sent when reset password is requested for an email that doesn't have a matching
# account; make sure this doesn't return an error, so as to avoid an email enumeration attack
ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False
# leave this as None since setting to 1 prevents users from being able to change their email address
ACCOUNT_MAX_EMAIL_ADDRESSES = None  # default
# ACCOUNT_FORMS allows customizing the forms used by allauth

# allows for one-time use of an emailed code to login
ACCOUNT_LOGIN_BY_CODE_ENABLED = False  # default
# can customize ACCOUNT_LOGIN_BY_CODE_MAX_ATTEMPTS (default 3) and ACCOUNT_LOGIN_BY_CODE_TIMEOUT
# (default 180 sec)

# only works when confirming email immediately after signing up and tab is in the same browser
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True  # default false

# don't need to set this since Django sessions include an HMAC of the user's hashed password, so
# changing a user's password invalidates all sessions anyway, but that is rectified by the current
# reset view updating the hash within its session so logging back in is not required
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = False  # default
# defaults to password reset done page instead of loginng in the user automatically
ACCOUNT_LOGIN_ON_PASSWORD_RESET = False  # default
ACCOUNT_LOGOUT_REDIRECT_URL = "/"  # default; defaults to LOGOUT_REDIRECT_URL if set
# allows for not clearing the password field on form error (could be less safe)
ACCOUNT_PASSWORD_INPUT_RENDER_VALUE = False  # default
# makes username lookup more expensive when filtering if preserved
ACCOUNT_PRESERVE_USERNAME_CASING = False  # default
# will prioritize email uniqueness over preventing enumeration, so set to "strict" if you want to
# allow multiple accounts to have the same email for max prevention (only one will be able to
# verify); make sure this doesn't return a clear error to avoid enumeration
ACCOUNT_PREVENT_ENUMERATION = True  # default
# whether reauthentication is required for sensitive actions (like changing email or password)
ACCOUNT_REAUTHENTICATION_REQUIRED = False  # default
# ACCOUNT_REAUTHENTICATION_TIMEOUT prevents having to double authenticate in a short period of time

# can be explicitly set; None shows a box the user can click
ACCOUNT_SESSION_REMEMBER = None  # default
# can be useful for avoiding typos
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = False  # default
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True  # default
# allows for base signup form that will be extended and which provides additional fields
ACCOUNT_SIGNUP_FORM_CLASS = None  # default
# honeypot fields are hidden visually and via tab navigation, but are often accidentally filled in
# by bots, and an account won't be made if the field is filled out
ACCOUNT_SIGNUP_FORM_HONEYPOT_FIELD = None  # not using for now since requires some styling to make hidden when used with crispyforms
# only works if the flow doesn't require side steps like email verification
ACCOUNT_SIGNUP_REDIRECT_URL = LOGIN_REDIRECT_URL  # default
# be careful disabling this
ACCOUNT_UNIQUE_EMAIL = True  # default

# ACCOUNT_USER_DISPLAY lets you customize the string representation of the user model via a callable

ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"  # default
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"  # default
ACCOUNT_USERNAME_MIN_LENGTH = 1  # default
# requires username even if email is used for login
ACCOUNT_USERNAME_REQUIRED = True  # default
# path to a list of validators
ACCOUNT_USERNAME_VALIDATORS = None  # default

EMAIL_BACKEND = (
    # can use console for development if don't want to use up email allowance
    # "django.core.mail.backends.console.EmailBackend"
    "django.core.mail.backends.smtp.EmailBackend"
)

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = os.environ.get("SENDGRID_API_KEY")
EMAIL_PORT = 587  # TLS port
EMAIL_USE_TLS = True
# has to match configured domain in SendGrid
DEFAULT_FROM_EMAIL = "Local Library Assistant <email@cshock.tech>"

# entry point to URLConf construction
ROOT_URLCONF = "library.urls"

TEMPLATES = [
    {
        # engine for template rendering
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # look in the project dir for anything app-agnostic
        "DIRS": [BASE_DIR / "templates"],
        # do not set APP_DIRS when providing OPTIONS.loaders
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.nav_menu_state",
            ],
        },
    },
]


WSGI_APPLICATION = "library.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB_NAME"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
        # defaults to 0; set to something or None if you want connection reuse (not needed for our low traffic site)
        "CONN_MAX_AGE": 0,
        # usually set this to True if you want to use persistent connections, but check for performance penalties
        "CONN_HEALTH_CHECKS": False,
        "OPTIONS": {
            "sslmode": "disable",
        },
    }
}

USE_REDIS_CACHE = os.environ.get("USE_REDIS_CACHE", "") == "True"

if USE_REDIS_CACHE:
    CACHES = {
        "default": {
            # don't generate prometheus metrics from redis cache because it requires using 3rd party
            # backend IN ADDITION to django-prometheus (which is not necessary right now since we
            # are lacking redis on prod atm)
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            # 'redis://' is TCP connection w/o SSL while 'rediss://' has SSL
            "LOCATION": "redis://"
            + os.environ.get(
                "DJANGO_REDIS_USERNAME",
                "",
            )
            + ":"
            + os.environ.get(
                "DJANGO_REDIS_PASSWORD",
                "",
            )
            + "@"
            + os.environ.get("REDIS_HOST", "")
            + ":"
            + os.environ.get("REDIS_PORT", ""),
            # can pass an array to 'LOCATION' of a lead server for writes, followed by replicas for
            # reads
        }
    }


def static_files_storage():
    if USING_WHITENOISE:
        return "whitenoise.storage.CompressedManifestStaticFilesStorage"

    storage: str
    if ENV == "dev":
        storage = "django.contrib.staticfiles.storage.StaticFilesStorage"
    # can't use hash-only on debug because debug-toolbar doesn't properly use static template tags
    elif ENV == "preprod" and DEBUG:
        # this avoids having to configure some annoying cache headers with nginx
        storage = "core.storage.UseHashUrlManifestStaticFilesStorage"
    else:
        return "core.storage.KeepHashOnlyManifestStaticFilesStorage"
    return storage


def media_files_storage():
    if PROD:
        return {
            # custom storage from 'django-storages' package (actually using Cloudflare R2, which is S3 API compatible)
            "BACKEND": "core.storage.UuidNameStorage",
            "OPTIONS": {
                "class_name": "storages.backends.s3.S3Storage",
                "access_key": os.environ.get("CLOUDFLARE_R2_S3_ACCESS_KEY_ID"),
                "secret_key": os.environ.get("CLOUDFLARE_R2_S3_ACCESS_KEY_SECRET"),
                # "security_token": os.environ.get("CLOUDFLARE_R2_API_TOKEN"),
                "bucket_name": os.environ.get("CLOUDFLARE_R2_BUCKET_NAME"),
                # bucket is public, so no need for this
                "querystring_auth": False,
                # max size of file that can be held in memory without being written to a temp-file
                "max_memory_size": 20 * 1024 * 1024,
                "endpoint_url": os.environ.get("CLOUDFLARE_R2_API_URL"),
                "custom_domain": os.environ.get("CLOUDFLARE_R2_CUSTOM_DOMAIN"),
            },
        }
    else:
        return {
            "BACKEND": "core.storage.UuidNameStorage",
            "OPTIONS": {
                "class_name": "django.core.files.storage.FileSystemStorage",
            },
        }


STORAGES = {
    # storage for uploaded files from models
    "default": media_files_storage(),
    # cache busts statics
    "staticfiles": {
        "BACKEND": static_files_storage(),
    },
}

# write-through cache to the db, but cache-only for reads
SESSION_ENGINE = (
    "django.contrib.sessions.backends.cached_db"
    if USE_REDIS_CACHE
    # do not use cache when not using redis as the cache because the default cache is local memory
    # per-process, which breaks session data consistency
    else "django.contrib.sessions.backends.db"
)

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "America/Los_Angeles"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

# for any top-level static files
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
# where static files will be collected for deployment (more convenient if kept out of directory)
STATIC_ROOT = BASE_DIR / "../nginx/statics"
STATIC_URL = os.environ.get("STATICS_URL", "statics/")

# absolute file path root for uploaded files (only relevant for local storage)
MEDIA_ROOT = BASE_DIR / "user-media"
# should be served from a different domain to avoid subdomain-based attacks
# - NOTE: this is only relevant if the Storage class used references it (though it can be used to
#   manually construct URLs by using 'settings.MEDIA_URL + File/ImageField.name')
MEDIA_URL = os.environ.get("MEDIA_URL", "user-media/")

# crispy forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_FAIL_SILENTLY = not DEBUG

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# set to None to set up your own logging solution (equivalent to LOGGING.disable_existing_loggers, I think)
#
# LOGGING_CONFIG = None

LOGGING = {
    "version": 1,
    # usually don't want to disable since the loggers still exist and ingest logs but ONLY discard
    # them and can prevent propagation
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} process:{process:d} {message}",
            # f-string formatting
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_true": {
            # "()" refers to the callable
            "()": "django.utils.log.RequireDebugTrue",
            # any other key would refer to a parameter argument for the callable
        },
        # custom filter example
        #
        # "special": {
        #     "()": "project.logging.SpecialFilter",
        #     "foo": "bar",
        # },
    },
    "handlers": {
        "console": {
            # anything that meets OR exceeds the level will be handled
            "level": "INFO",
            "filters": ["require_debug_true"],
            # StreamHandler prints to stderr by default
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "level": "WARNING",
            # technically shouldn't log to a file like this when using gunicon due to the multiple
            # processes, but leaving it for simplicity
            "class": "logging.FileHandler",
            # note that this is relative to the directory where the Django project start script is
            # called, NOT the settings file
            "filename": "./log/django-errors.log",
            "formatter": "verbose",
        },
        # "mail_admins": {
        #     "level": "ERROR",
        #     "class": "django.utils.log.AdminEmailHandler",
        # },
    },
    # top-level logging object (name does not have any relation to module, so make sure to propagate
    # any log you don't consider completely "handled")
    "loggers": {
        # this is the name of the logger you need to provide when calling 'logger.getLogger([name])'
        "django": {
            "handlers": ["console", "file"],
        },
        # BEWARE: failing email logging appears to prevent propagation??? (DON'T USE EMAIL LOGGING)
        #
        # "django.request": {
        #     "handlers": ["mail_admins"],
        #     "level": "ERROR",
        #     "propagate": True,
        # },
        # custom logger example
        #
        # "myproject.custom": {
        #     "handlers": ["console", "mail_admins"],
        #     "level": "INFO",
        #     "filters": ["special"],
        # },
    },
}

# NOTE: not recommended to use these unless you really don't need a better alerting system (which
# you almost ALWAYS do)
#
# email list for receiving reports of 500 errors
ADMINS = [("Conrad", "shockconrad@gmail.com")]
# email list for receiving reports of 404 errors
MANAGERS = [("Conrad", "shockconrad@gmail.com")]
