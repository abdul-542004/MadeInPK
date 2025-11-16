# Generated migration for adding shipping status to OrderItem

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_sellerprofile_business_address_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='is_shipped',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='shipped_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
