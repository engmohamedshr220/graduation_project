from .base import *

DEBUG = env.bool("DEBUG")


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # Allow all hosts for development purposes
