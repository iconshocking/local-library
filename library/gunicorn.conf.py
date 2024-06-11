import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "/app/library/log/gunicorn-access.log"
errorlog = "/app/library/log/gunicorn-error.log"
# Whether to send Django output to the console to the error log
capture_output = True