# Generated by Django 4.1 on 2022-09-10 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_date_execution_timestamp_execution_state_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='execution',
            name='timestamp',
            field=models.DateTimeField(),
        ),
    ]
