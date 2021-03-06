# Generated by Django 3.0.6 on 2020-05-22 23:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sessions', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='messagemodel',
            name='recipient',
        ),
        migrations.AddField(
            model_name='messagemodel',
            name='responder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='sessions.Session', verbose_name='responder'),
        ),
        migrations.AlterField(
            model_name='messagemodel',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to='sessions.Session', verbose_name='user'),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='timestamp')),
                ('title', models.CharField(max_length=150)),
                ('tags', models.CharField(max_length=150)),
                ('body', models.CharField(max_length=500)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]
