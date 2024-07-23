from rest_framework.response import Response
from rest_framework import decorators
from .tasks import *


@decorators.api_view(['GET'])
def celery_test_view(request):
    do_calc_total.delay()
    return Response({"status": "Task has been started"})

@decorators.api_view(['GET'])
def celery_test_view2(request):
    for i in range(100):
        do_calc_single.delay(i)  # 개별 작업을 큐에 넣음
    return Response({"status": "Tasks have been started"})