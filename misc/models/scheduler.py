from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta


class Scheduler:
    def __init__(self, scheduler: AsyncIOScheduler, timezone):
        self.scheduler = scheduler
        self.timezone = timezone

    async def create_task(self, task_func: object, task_args: list, task_id, **kwargs):
        if not self.scheduler.get_job(task_id):
            self.scheduler.add_job(
                func=task_func,
                args=task_args,
                id=task_id,
                trigger=DateTrigger(
                    datetime.now(tz=self.timezone) + timedelta(**kwargs),
                    timezone=self.timezone
                ),
                misfire_grace_time=None
            )

    async def pause_task(self, task_id):
        if task := self.scheduler.get_job(str(task_id)):
            task.pause()

    async def resume_task(self, task_id):
        if task := self.scheduler.get_job(str(task_id)):
            task.resume()

    async def reload_task(self, task_id, **kwargs):
        if task := self.scheduler.get_job(str(task_id)):
            task.reschedule(
                DateTrigger(
                    datetime.now(tz=self.timezone) + timedelta(**kwargs),
                    timezone=self.timezone
                ))
