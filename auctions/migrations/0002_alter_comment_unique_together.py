# Generated by Django 4.0.4 on 2022-04-20 20:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='comment',
            unique_together={('publisher', 'message')},
        ),
    ]
