# CELERY Tutorial

* install the packages
`uv add celery django`
* create a fresh django project, create a base app
* add `celery` and `base` to INSTALLED_APPS
* setup celery config in the `settings.py` file
* We will need to import Celery and create an instance of the Celery class in the project's `__init__.py` file.
* create a `celery.py` file and set the Django settings module as an environment variable so that Celery knows how to connect to our Django project.
* Define tasks in one or more app. In each app, create a file called tasks.py. Define Celery tasks `@shared_task` decorator, but it's a good idea to create a separate app for them.

> A task is a Python function that is decorated with the @shared_task decorator from the celery package. The decorator tells Celery to treat the function as a task that can be added to the task queue. This code defines a simple task that adds two numbers together.