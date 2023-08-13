# Generated by Django 4.2.4 on 2023-08-13 13:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad', '0004_bookrequest_date_added_readerrequest_date_added_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loantransaction',
            name='date_expired',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 20, 13, 13, 52, 840891, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='sourcetype',
            name='description',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
    ]
