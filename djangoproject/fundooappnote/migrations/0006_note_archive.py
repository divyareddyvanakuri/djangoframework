# Generated by Django 3.0.4 on 2020-03-09 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fundooappnote', '0005_auto_20200306_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='archive',
            field=models.BooleanField(default=False),
        ),
    ]
