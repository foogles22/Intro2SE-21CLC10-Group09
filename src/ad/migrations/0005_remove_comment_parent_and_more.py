# Generated by Django 4.2.2 on 2023-08-07 06:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad', '0004_alter_loantransaction_date_expired_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='parent',
        ),
        migrations.AlterField(
            model_name='loantransaction',
            name='date_expired',
            field=models.DateField(default=datetime.datetime(2023, 8, 14, 6, 27, 3, 22942, tzinfo=datetime.timezone.utc)),
        ),
    ]