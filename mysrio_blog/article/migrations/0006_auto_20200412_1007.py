# Generated by Django 2.2 on 2020-04-12 02:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0005_articlepost_heading_image'),
    ]

    operations = [
        migrations.RenameField(
            model_name='articlepost',
            old_name='heading_image',
            new_name='heading_img',
        ),
    ]
