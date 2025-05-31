from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_product_description_product_image2_product_image3_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shippingaddress',
            old_name='state',
            new_name='province',
        ),
    ] 