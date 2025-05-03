from .base import *

DEBUG = env.bool("DEBUG")


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])  # Allow all hosts for development purposes
