# # celery.py
# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery
#
# # Django의 settings 모듈을 Celery의 기본 설정 모듈로 설정합니다.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_backend.settings')
#
# app = Celery('django_backend')
#
# # 여기서 모든 celery 관련 설정을 settings.py에서 가져옵니다.
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# # Django app config가 등록된 모든 태스크 모듈을 로드합니다.
# app.autodiscover_tasks()
#
# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
