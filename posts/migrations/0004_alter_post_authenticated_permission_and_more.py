# Generated by Django 5.1.6 on 2025-03-12 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_post_group_name_alter_post_authenticated_permission_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='authenticated_permission',
            field=models.IntegerField(choices=[(0, 'none'), (1, 'read_only'), (2, 'read_and_write')], default='1'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group_permission',
            field=models.IntegerField(choices=[(0, 'none'), (1, 'read_only'), (2, 'read_and_write')], default='1'),
        ),
    ]
