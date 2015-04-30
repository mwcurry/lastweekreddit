from __future__ import absolute_import

from celery import Celery

celapp = Celery('lwr',
             broker='amqp://',
             backend='amqp://',
             include=['engine'])

# Optional configuration, see the application user guide.
celapp.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    celapp.start()