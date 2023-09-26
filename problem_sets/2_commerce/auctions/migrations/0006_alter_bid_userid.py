# Generated by Django 4.2.5 on 2023-09-05 18:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0005_alter_auction_userid_alter_bid_userid_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bid",
            name="UserID",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
