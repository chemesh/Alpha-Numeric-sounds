# Generated by Django 4.1 on 2022-09-09 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Execution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=100)),
                ('date', models.DateField()),
                ('song_1', models.FilePathField()),
                ('song_2', models.FilePathField()),
                ('result', models.FilePathField()),
            ],
        ),
    ]
