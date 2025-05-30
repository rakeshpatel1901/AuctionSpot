# Generated by Django 4.2.17 on 2025-01-07 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('host_auction', '0005_remove_auction_db_meeting_id_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_amt', models.DecimalField(decimal_places=2, max_digits=10)),
                ('team_name', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='host_auction.player_db')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='host_auction.tournament')),
            ],
        ),
    ]
