# Generated by Django 4.2.16 on 2024-12-02 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='tournament',
            fields=[
                ('tournament_id', models.AutoField(primary_key=True, serialize=False)),
                ('tournament_name', models.CharField(max_length=100)),
                ('tournament_description', models.TextField(max_length=500)),
                ('tournament_category', models.CharField(max_length=40)),
            ],
        ),
    ]
