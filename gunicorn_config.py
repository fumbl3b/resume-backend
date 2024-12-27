import os

bind = "0.0.0.0:10000"
workers = 4
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = os.getenv("LOG_LEVEL", "debug")