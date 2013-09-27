from __future__ import absolute_import
from celery import Celery

celery = Celery('converter_app.celery', broker='amqp://', backend='amqp://', include=['converter_app.tasks'])

if __name__ == '__main__':
    celery.start()
