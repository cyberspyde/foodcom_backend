# Generated by Django 4.2.3 on 2023-11-07 01:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_remove_customer_event_duration_customer_user_note_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customer',
            old_name='user_note',
            new_name='message',
        ),
    ]
