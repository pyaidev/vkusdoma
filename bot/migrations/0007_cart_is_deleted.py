# Generated by Django 4.2.7 on 2023-11-30 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0006_order_adress_order_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
