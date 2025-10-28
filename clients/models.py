from django.db import models
from django.core.validators import EmailValidator
from django.utils import timezone
import re


class Client(models.Model):
	TYPE_CHOICES = [
		('particulier', 'Particulier'),
		('entreprise', 'Entreprise'),
	]
	
	# Informations de base
	nom_complet = models.CharField(
		max_length=200, 
		verbose_name="Nom complet ou raison sociale",
		help_text="Nom complet pour un particulier ou raison sociale pour une entreprise"
	)
	type_client = models.CharField(
		max_length=20,
		choices=TYPE_CHOICES,
		default='particulier',
		verbose_name="Type de client"
	)
	
	# Coordonnées
	telephone = models.CharField(
		max_length=32,
		default="+224 ",
		verbose_name="Numéro de téléphone",
		help_text="Ex.: +224 626402000"
	)
	telephone_normalise = models.CharField(
		max_length=32,
		editable=False,
		blank=True,
		default='',
		help_text="Chiffres uniquement pour recherche",
		db_index=True,
	)
	email = models.EmailField(
		verbose_name="Adresse e-mail",
		blank=True,
		null=True,
		validators=[EmailValidator()]
	)
	adresse = models.TextField(
		verbose_name="Adresse complète",
		blank=True,
		null=True
	)
	pays = models.CharField(
		max_length=100,
		default="Guinée",
		verbose_name="Pays"
	)
	
	# Métadonnées
	date_creation = models.DateTimeField(
		auto_now_add=True,
		verbose_name="Date de création"
	)
	date_modification = models.DateTimeField(
		auto_now=True,
		verbose_name="Dernière modification"
	)
	actif = models.BooleanField(
		default=True,
		verbose_name="Client actif"
	)
	
	class Meta:
		verbose_name = "Client"
		verbose_name_plural = "Clients"
		ordering = ['-date_creation']
		indexes = [
			models.Index(fields=['nom_complet']),
			models.Index(fields=['telephone']),
			models.Index(fields=['telephone_normalise']),
			models.Index(fields=['email']),
			models.Index(fields=['type_client']),
			models.Index(fields=['actif']),
		]
	
	def __str__(self):
		return self.nom_complet
	
	@staticmethod
	def _normalize_digits(value: str) -> str:
		if not value:
			return ''
		return re.sub(r'[^\d]', '', value)
	
	@staticmethod
	def _format_with_country(value: str) -> str:
		"""Formate un numéro stocké pour affichage: +CCC groups."""
		if not value:
			return ''
		m = re.match(r'^(\+\d{1,3})\s*(.*)$', value.strip())
		if m:
			country = m.group(1)
			rest_digits = re.sub(r'[^\d]', '', m.group(2))
		else:
			# Pas d'indicatif stocké
			digits = re.sub(r'[^\d]', '', value)
			if len(digits) > 3:
				country = f"+{digits[:3]}"
				rest_digits = digits[3:]
			else:
				country = ''
				rest_digits = digits
		# Grouping: 3-2-2-2... if odd, else pairs
		def group_digits(d: str) -> str:
			if not d:
				return ''
			if len(d) <= 3:
				return d
			res = []
			if len(d) % 2 == 1:
				res.append(d[:3])
				d = d[3:]
			for i in range(0, len(d), 2):
				res.append(d[i:i+2])
			return ' '.join(res)
		local_fmt = group_digits(rest_digits)
		return f"{country} {local_fmt}".strip()
	
	def save(self, *args, **kwargs):
		# Met à jour le champ normalisé
		self.telephone_normalise = self._normalize_digits(self.telephone)
		super().save(*args, **kwargs)
	
	def get_telephone_formatted(self):
		"""Retourne le numéro de téléphone formaté universellement."""
		return self._format_with_country(self.telephone)
	
	def get_type_display_short(self):
		"""Retourne le type de client en format court"""
		return "Particulier" if self.type_client == 'particulier' else "Entreprise"
	
	def get_icone_type(self):
		"""Retourne l'icône FontAwesome selon le type de client"""
		return "fas fa-user" if self.type_client == 'particulier' else "fas fa-building"
	
	def get_statut_badge(self):
		"""Retourne le badge de statut HTML"""
		if self.actif:
			return '<span class="badge bg-success">Actif</span>'
		else:
			return '<span class="badge bg-secondary">Inactif</span>'
	
	def get_nombre_devis(self):
		"""Retourne le nombre de devis pour ce client"""
		return self.devis_set.count()
	
	def get_nombre_factures(self):
		"""Retourne le nombre de factures pour ce client"""
		# Les factures sont liées aux fournisseurs, pas aux clients
		# Pour l'instant, retourner 0 car il n'y a pas de relation directe
		# TODO: Implémenter une logique métier si nécessaire
		return 0
	
	def get_total_factures(self):
		"""Retourne le montant total des factures"""
		# Les factures sont liées aux fournisseurs, pas aux clients
		# Pour l'instant, retourner 0 car il n'y a pas de relation directe
		# TODO: Implémenter une logique métier si nécessaire
		return 0
	
	def get_derniere_activite(self):
		"""Retourne la date de la dernière activité (devis ou facture)"""
		from devis.models import Devis
		
		dernier_devis = self.devis_set.order_by('-date_creation').first()
		
		if dernier_devis:
			return dernier_devis.date_creation
		
		return self.date_creation
