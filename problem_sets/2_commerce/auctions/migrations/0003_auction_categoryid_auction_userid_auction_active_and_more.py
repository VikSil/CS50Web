# Generated by Django 4.2.5 on 2023-09-04 23:30

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("auctions", "0002_auction_bid_category_comment_watchlist"),
    ]

    operations = [
        migrations.AddField(
            model_name="auction",
            name="CategoryID",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="auctions.category",
            ),
        ),
        migrations.AddField(
            model_name="auction",
            name="UserID",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="auction",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="auction",
            name="description",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="auction",
            name="imageURL",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="auction",
            name="title",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="bid",
            name="AuctionID",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="auctions.auction",
            ),
        ),
        migrations.AddField(
            model_name="bid",
            name="UserID",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="bid",
            name="when",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="name",
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name="comment",
            name="AuctionID",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="auctions.auction",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="UserID",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="comment",
            name="text",
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="comment",
            name="when",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="watchlist",
            name="AuctionID",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="auctions.auction",
            ),
        ),
        migrations.AddField(
            model_name="watchlist",
            name="UserID",
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="bid",
            name="amount",
            field=models.DecimalField(decimal_places=2, default=0.01, max_digits=12),
        ),
    ]
