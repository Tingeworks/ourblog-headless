# Generated by Django 5.1.1 on 2024-09-18 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0005_alter_invoice_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="is_paid",
            field=models.BooleanField(default=False),
        ),
    ]