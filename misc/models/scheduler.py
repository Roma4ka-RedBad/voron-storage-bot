from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from typing import Callable, Any


class Scheduler:
    def __init__(self, scheduler: AsyncIOScheduler, timezone):
        self.scheduler = scheduler
        self.timezone = timezone
        self.scheduler.start()

    async def create_task(self, task_func: Callable[[Any], Any],
                          task_args: list,
                          task_id: tuple[int | str, int | str] | int | str,
                          **kwargs):
        task_id = self.get_task_id(task_id)
        if not self.scheduler.get_job(task_id):
            self.scheduler.add_job(
                func=task_func,
                args=task_args,
                id=task_id,
                trigger=DateTrigger(
                    datetime.now(tz=self.timezone) + timedelta(**kwargs),
                    timezone=self.timezone),
                misfire_grace_time=None)

        # просто вывод всех заданий, которые должны сработать
        for job in self.scheduler.get_jobs():
            print(self.scheduler.get_job(job.id))
        print(self.scheduler.get_jobs())

    async def pause_task(self, task_id: tuple[int | str, int | str] | int | str):
        if task := self.scheduler.get_job(self.get_task_id(task_id)):
            task.pause()

    async def resume_task(self, task_id: tuple[int | str, int | str] | int | str):
        if task := self.scheduler.get_job(self.get_task_id(task_id)):
            task.resume()

    async def reload_task(self, task_id: tuple[int | str, int | str] | int | str, **kwargs):
        if task := self.scheduler.get_job(self.get_task_id(task_id)):
            task.reschedule(
                DateTrigger(
                    datetime.now(tz=self.timezone) + timedelta(**kwargs),
                    timezone=self.timezone))

    def get_task_id(self, task_id: tuple[int | str, int | str] | int | str):
        if isinstance(task_id, (str, int)):
            return str(task_id)
        return f'{task_id[0]}_{task_id[1]}'

    async def get(self, task):
        task_id = self.get_task_id(task)
        return self.scheduler.get_job(task_id)
