# Generated by Django 3.2.4 on 2021-06-17 19:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_orderitem_selected'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipientinfo',
            old_name='request',
            new_name='comment',
        ),
    ]
