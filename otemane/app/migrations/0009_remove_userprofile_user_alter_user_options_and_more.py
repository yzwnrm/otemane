# Generated by Django 5.1.7 on 2025-04-17 03:10

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_invitation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AlterModelOptions(
            name='user',
            options={},
        ),
        migrations.RemoveField(
            model_name='user',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='user',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='user',
            name='last_name',
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='user',
            name='family_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='password_expiry',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='password_token',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='relationship',
            field=models.IntegerField(choices=[(0, '母'), (1, '父'), (2, '祖母'), (3, '祖父'), (4, '兄'), (5, '姉'), (6, 'その他')], default=6),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='update_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=100),
        ),
        migrations.DeleteModel(
            name='PasswordResetToken',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
