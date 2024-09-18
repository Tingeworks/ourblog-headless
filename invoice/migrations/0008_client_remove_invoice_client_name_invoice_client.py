# Generated by Django 5.1.1 on 2024-09-18 11:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0007_remove_invoice_is_paid_invoice_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(default="Unknown", max_length=100)),
                (
                    "email",
                    models.EmailField(default="someone@example.com", max_length=100),
                ),
                ("address", models.TextField(blank=True)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name="invoice",
            name="client_name",
        ),
        migrations.AddField(
            model_name="invoice",
            name="client",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="invoice.client",
            ),
        ),
    ]