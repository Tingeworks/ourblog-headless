# Generated by Django 5.1.1 on 2024-09-26 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Tags",
            new_name="Tag",
        ),
    ]