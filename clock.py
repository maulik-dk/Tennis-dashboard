from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import sys
from rq import Queue
from worker import conn
from utils import security

q = Queue(connection=conn)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def execute_security():
    result = q.enqueue(security)

sched = BlockingScheduler()
sched.add_job(execute_security) #enqueue right away once
sched.start()
