from celery import Celery

celery = Celery('converter_app.celery', broker='amqp://', backend='amqp://', include=['converter_app.tasks'])

celery.conf.update(
    CELERYBEAT_SCHEDULER="djcelery.schedulers.DatabaseScheduler"
)

if __name__ == '__main__':
    celery.start()
