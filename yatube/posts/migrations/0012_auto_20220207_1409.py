# Generated by Django 2.2.16 on 2022-02-07 11:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20220207_1354'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-created',), 'verbose_name': 'Post', 'verbose_name_plural': 'Posts'},
        ),
    ]
