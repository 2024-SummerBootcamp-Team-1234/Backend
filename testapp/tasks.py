import time

from django_backend.celery import app


@app.task(bind=True)
def do_calc_total(self):
    total = 0
    for i in range(100):
        time.sleep(1)
        total += i
    return total

@app.task(bind=True)
def do_calc_single(self, i):
    time.sleep(1)
    return i