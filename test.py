import asyncio
import random

my_list = []


def notify():
    length = len(my_list)
    print("List has changed!", length)

async def append_task(num):
    
    print(num)
    while True:
        
        await asyncio.sleep(100)
        my_list.append(random.random())
        notify()

async def pop_task():
    while True:
        await asyncio.sleep(1.8)
        my_list.pop()
        notify()




async def  run (    ):
    jobs = []
    for i in range(10):
        jobs.append (   append_task(i)                 )

    for num , job in enumerate( asyncio.as_completed(jobs) )  :
        await job
    print('12345')


loop = asyncio.get_event_loop()

loop.run_until_complete(run()  )