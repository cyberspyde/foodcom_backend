# Generated by Django 4.2.3 on 2023-07-14 07:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_tool_remove_customer_tool'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='tool',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.tool'),
        ),
    ]
