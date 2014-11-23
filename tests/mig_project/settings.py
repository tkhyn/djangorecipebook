SECRET_KEY = 'mig_project_secret_key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

MIDDLEWARE_CLASSES = ()

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tests.mig_project.migrated_with_dj17',
    'tests.mig_project.migrated_with_south',
    'tests.mig_project.migrated_with_both',
    'tests.mig_project.unmigrated',
)
