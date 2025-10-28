# Generated manually for factures app

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fournisseurs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Facture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(help_text='Numéro de facture du fournisseur', max_length=50, unique=True, verbose_name='Numéro de facture')),
                ('objet', models.CharField(help_text='Objet de la facture', max_length=200, verbose_name='Objet')),
                ('description', models.TextField(blank=True, help_text='Description détaillée de la facture', null=True, verbose_name='Description')),
                ('date_emission', models.DateField(help_text='Date d\'émission de la facture', verbose_name="Date d'émission")),
                ('date_echeance', models.DateField(help_text='Date d\'échéance de paiement', verbose_name="Date d'échéance")),
                ('statut', models.CharField(choices=[('brouillon', 'Brouillon'), ('en_attente', 'En attente'), ('validee', 'Validée'), ('payee', 'Payée'), ('annulee', 'Annulée')], default='brouillon', help_text='Statut actuel de la facture', max_length=20, verbose_name='Statut')),
                ('montant_ht', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Montant hors taxes', max_digits=18, verbose_name='Montant HT')),
                ('taux_tva', models.DecimalField(decimal_places=2, default=Decimal('18.00'), help_text='Taux de TVA en pourcentage', max_digits=5, verbose_name='Taux TVA (%)')),
                ('montant_tva', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Montant de la TVA', max_digits=18, verbose_name='Montant TVA')),
                ('montant_ttc', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Montant toutes taxes comprises', max_digits=18, verbose_name='Montant TTC')),
                ('conditions_paiement', models.TextField(blank=True, help_text='Conditions de paiement spécifiées', null=True, verbose_name='Conditions de paiement')),
                ('notes', models.TextField(blank=True, help_text='Notes additionnelles', null=True, verbose_name='Notes')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Dernière modification')),
                ('fournisseur', models.ForeignKey(help_text='Fournisseur qui a émis la facture', on_delete=django.db.models.deletion.CASCADE, to='fournisseurs.Fournisseur', verbose_name='Fournisseur')),
            ],
            options={
                'verbose_name': 'Facture',
                'verbose_name_plural': 'Factures',
                'ordering': ['-date_emission'],
            },
        ),
        migrations.CreateModel(
            name='LigneFacture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(help_text='Description de l\'article ou service', max_length=200, verbose_name='Description')),
                ('quantite', models.DecimalField(decimal_places=2, default=Decimal('1.00'), help_text='Quantité commandée', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='Quantité')),
                ('unite', models.CharField(default='unité', help_text='Unité de mesure', max_length=20, verbose_name='Unité')),
                ('prix_unitaire_ht', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Prix unitaire hors taxes', max_digits=15, validators=[django.core.validators.MinValueValidator(Decimal('0.00'))], verbose_name='Prix unitaire HT')),
                ('montant_ht', models.DecimalField(decimal_places=2, default=Decimal('0.00'), help_text='Montant total de la ligne hors taxes', max_digits=15, verbose_name='Montant HT')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date de création')),
                ('date_modification', models.DateTimeField(auto_now=True, verbose_name='Dernière modification')),
                ('facture', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lignes', to='factures.Facture', verbose_name='Facture')),
            ],
            options={
                'verbose_name': 'Ligne de facture',
                'verbose_name_plural': 'Lignes de facture',
                'ordering': ['id'],
            },
        ),
        migrations.AddIndex(
            model_name='facture',
            index=models.Index(fields=['numero'], name='factures_fa_numero_123456_idx'),
        ),
        migrations.AddIndex(
            model_name='facture',
            index=models.Index(fields=['fournisseur'], name='factures_fa_fournis_123456_idx'),
        ),
        migrations.AddIndex(
            model_name='facture',
            index=models.Index(fields=['date_emission'], name='factures_fa_date_em_123456_idx'),
        ),
        migrations.AddIndex(
            model_name='facture',
            index=models.Index(fields=['statut'], name='factures_fa_statut_123456_idx'),
        ),
    ]
