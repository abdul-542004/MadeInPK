# Generated migration to add business_address_id to SellerProfile

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_add_business_phone_to_seller_profile'),
    ]

    operations = [
        # Add new business_address_id field
        migrations.AddField(
            model_name='sellerprofile',
            name='business_address_id',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='seller_profiles',
                to='api.address',
                help_text='Business address for the seller'
            ),
        ),
        # Rename old field for backward compatibility
        migrations.RenameField(
            model_name='sellerprofile',
            old_name='business_address',
            new_name='business_address_text',
        ),
    ]
