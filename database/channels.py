from peewee import BigIntegerField, CharField, BooleanField
from .base import database, JSONField


def get_mailing_data(mailing_types: list):
    result = {}
    for mailing_type in mailing_types:
        result.update({
            mailing_type: {
                'text': ""
            }
        })
    return result


class Channels(database.Model):
    channel_id = BigIntegerField(null=False)
    platform_name = CharField(max_length=2, null=False)
    prod_update_mailing = BooleanField(default=False)
    prod_maintenance_mailing = BooleanField(default=False)
    youtube_mailing = BooleanField(default=False)
    funkit_mailing = BooleanField(default=False)
    mailing_data = JSONField(default=get_mailing_data(
        ['prod_update', 'prod_maintenance_start', 'prod_maintenance_end', 'youtube_new_video', 'youtube_premiere',
         'funkit']
    ))

    @classmethod
    async def get_list(cls, *args) -> list:
        print(await cls.select().where(*args))
        return list(await cls.select().where(*args))
