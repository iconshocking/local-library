import multiprocessing

# limit to one worker when debugging templates in preprod since you get some weird caching issues across workers
# otherwise (even though the cache loader is disabled in settings.py *shrug*)
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "/app/library/log/gunicorn-access.log"
errorlog = "/app/library/log/gunicorn-error.log"
# Whether to send Django output to the console to the error log
capture_output = True
