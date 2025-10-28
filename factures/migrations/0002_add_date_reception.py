# Generated manually

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('factures', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='facture',
            name='date_reception',
            field=models.DateField(default=django.utils.timezone.now, verbose_name="Date de réception"),
        ),
    ]
