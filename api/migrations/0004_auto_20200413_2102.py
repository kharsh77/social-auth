# Generated by Django 2.2.12 on 2020-04-13 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_userpasswordsalt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpasswordsalt',
            name='salt',
            field=models.BinaryField(),
        ),
    ]
