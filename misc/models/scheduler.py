from datetime import datetime, timedelta
from typing import Callable, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger


class Scheduler:
    def __init__(self, scheduler: AsyncIOScheduler, timezone):
        self.scheduler = scheduler
        self.timezone = timezone

    def create_task(self, task_func: Callable[[Any], Any],
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

    def resume_task(self, task_id: tuple[int | str, int | str] | int | str):
        if task := self.scheduler.get_job(self.get_task_id(task_id)):
            task.resume()

    def reload_task(self, task_id: tuple[int | str, int | str] | int | str, **kwargs):
        if task := self.scheduler.get_job(self.get_task_id(task_id)):
            task.reschedule(DateTrigger(
                datetime.now(tz=self.timezone) + timedelta(**kwargs),
                timezone=self.timezone))

    def get_task_id(self, task_id: tuple[int | str, int | str] | int | str):
        if isinstance(task_id, (str, int)):
            return str(task_id)
        return f'{task_id[0]}_{task_id[1]}'

    def get(self, task):
        task_id = self.get_task_id(task)
        return self.scheduler.get_job(task_id)

    def pause_task(self, task_id: tuple[int | str, int | str] | int | str):
        if task := self.scheduler.get_job(self.get_task_id(task_id)):
            task.pause()
            return Job(task, self.timezone)


class Job:
    def __init__(self, task, timezone):
        self.timezone = timezone
        self.task = task
        self.paused_for = None

        self.on = self._for
        self.second = self.seconds
        self.minute = self.minutes
        self.hour = self.hours
        self.day = self.days

    def _for(self, arg: int):
        self.paused_for = arg
        return self

    def seconds(self):
        self.task.reschedule(DateTrigger(
            datetime.now(tz=self.timezone) + timedelta(seconds=self.paused_for),
            timezone=self.timezone))

    def minutes(self):
        self.task.reschedule(DateTrigger(
            datetime.now(tz=self.timezone) + timedelta(minutes=self.paused_for),
            timezone=self.timezone))

    def hours(self):
        self.task.reschedule(DateTrigger(
            datetime.now(tz=self.timezone) + timedelta(hours=self.paused_for * 60),
            timezone=self.timezone))

    def days(self):
        self.task.reschedule(DateTrigger(
            datetime.now(tz=self.timezone) + timedelta(days=self.paused_for * 60 * 24),
            timezone=self.timezone))
