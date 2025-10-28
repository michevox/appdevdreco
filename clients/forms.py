from django import forms
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from .models import Client
import re


# Ancien découpage par pays supprimé: on accepte désormais n'importe quel format de téléphone


class ClientForm(forms.ModelForm):
	"""Formulaire pour l'ajout et la modification des clients avec téléphone international"""

	# Rendre le champ model "telephone" non requis au niveau du formulaire,
	# car il sera alimenté dans clean() à partir de phone_number
	telephone = forms.CharField(
		required=False,
		widget=forms.HiddenInput()
	)

	PHONE_COUNTRY_CHOICES = (
		# Afrique (30 pays)
		('+224', 'Guinée (+224)'),
		('+225', "Côte d'Ivoire (+225)"),
		('+223', 'Mali (+223)'),
		('+221', 'Sénégal (+221)'),
		('+228', 'Togo (+228)'),
		('+229', 'Bénin (+229)'),
		('+226', 'Burkina Faso (+226)'),
		('+227', 'Niger (+227)'),
		('+220', 'Gambie (+220)'),
		('+222', 'Mauritanie (+222)'),
		('+230', 'Maurice (+230)'),
		('+231', 'Liberia (+231)'),
		('+232', 'Sierra Leone (+232)'),
		('+233', 'Ghana (+233)'),
		('+234', 'Nigeria (+234)'),
		('+235', 'Tchad (+235)'),
		('+236', 'République centrafricaine (+236)'),
		('+237', 'Cameroun (+237)'),
		('+238', 'Cap-Vert (+238)'),
		('+239', 'São Tomé-et-Príncipe (+239)'),
		('+240', 'Guinée équatoriale (+240)'),
		('+241', 'Gabon (+241)'),
		('+242', 'République du Congo (+242)'),
		('+243', 'République démocratique du Congo (+243)'),
		('+244', 'Angola (+244)'),
		('+245', 'Guinée-Bissau (+245)'),
		('+246', 'Territoire britannique de l\'océan Indien (+246)'),
		('+247', 'Ascension (+247)'),
		('+248', 'Seychelles (+248)'),
		('+249', 'Soudan (+249)'),
		('+250', 'Rwanda (+250)'),
		('+251', 'Éthiopie (+251)'),
		('+252', 'Somalie (+252)'),
		('+253', 'Djibouti (+253)'),
		('+254', 'Kenya (+254)'),
		('+255', 'Tanzanie (+255)'),
		('+256', 'Ouganda (+256)'),
		('+257', 'Burundi (+257)'),
		('+258', 'Mozambique (+258)'),
		('+260', 'Zambie (+260)'),
		('+261', 'Madagascar (+261)'),
		('+262', 'Réunion (+262)'),
		('+263', 'Zimbabwe (+263)'),
		('+264', 'Namibie (+264)'),
		('+265', 'Malawi (+265)'),
		('+266', 'Lesotho (+266)'),
		('+267', 'Botswana (+267)'),
		('+268', 'Eswatini (+268)'),
		('+269', 'Comores (+269)'),
		('+290', 'Sainte-Hélène (+290)'),
		('+291', 'Érythrée (+291)'),
		('+297', 'Aruba (+297)'),
		('+298', 'Îles Féroé (+298)'),
		('+299', 'Groenland (+299)'),
		
		# Europe (10 pays)
		('+33', 'France (+33)'),
		('+44', 'Royaume-Uni (+44)'),
		('+49', 'Allemagne (+49)'),
		('+39', 'Italie (+39)'),
		('+34', 'Espagne (+34)'),
		('+31', 'Pays-Bas (+31)'),
		('+32', 'Belgique (+32)'),
		('+41', 'Suisse (+41)'),
		('+43', 'Autriche (+43)'),
		('+46', 'Suède (+46)'),
		
		# Amérique (10 pays)
		('+1', 'États-Unis/Canada (+1)'),
		('+55', 'Brésil (+55)'),
		('+52', 'Mexique (+52)'),
		('+54', 'Argentine (+54)'),
		('+56', 'Chili (+56)'),
		('+57', 'Colombie (+57)'),
		('+58', 'Venezuela (+58)'),
		('+51', 'Pérou (+51)'),
		('+593', 'Équateur (+593)'),
		('+598', 'Uruguay (+598)'),
		
		# Asie (10 pays)
		('+86', 'Chine (+86)'),
		('+81', 'Japon (+81)'),
		('+82', 'Corée du Sud (+82)'),
		('+91', 'Inde (+91)'),
		('+66', 'Thaïlande (+66)'),
		('+65', 'Singapour (+65)'),
		('+60', 'Malaisie (+60)'),
		('+63', 'Philippines (+63)'),
		('+62', 'Indonésie (+62)'),
		('+84', 'Vietnam (+84)'),
	)

	phone_country_code = forms.ChoiceField(
		choices=PHONE_COUNTRY_CHOICES,
		initial='+224',
		label="Indicatif pays",
		widget=forms.Select(
			attrs={'class': 'form-select form-select-sm', 'style': 'max-width: 200px;'}
		)
	)

	phone_number = forms.CharField(
		label='Numéro',
		widget=forms.TextInput(attrs={
			'class': 'form-control',
			'placeholder': 'Numéro de téléphone',
			'autocomplete': 'off'
		})
	)

	class Meta:
		model = Client
		fields = ['nom_complet', 'type_client', 'telephone', 'email', 'adresse', 'actif']
		widgets = {
			'nom_complet': forms.TextInput(attrs={
				'class': 'form-control',
				'placeholder': 'Nom complet ou raison sociale',
				'autocomplete': 'off'
			}),
			'type_client': forms.Select(attrs={
				'class': 'form-select'
			}),
			'telephone': forms.HiddenInput(),
			'email': forms.EmailInput(attrs={
				'class': 'form-control',
				'placeholder': 'exemple@email.com',
				'autocomplete': 'off'
			}),
			'adresse': forms.Textarea(attrs={
				'class': 'form-control',
				'rows': 3,
				'placeholder': 'Adresse complète du client',
				'autocomplete': 'off'
			}),
			'actif': forms.CheckboxInput(attrs={
				'class': 'form-check-input'
			})
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Pré-remplir indicatif et numéro à partir de "telephone"
		telephone_value = self.instance.telephone if self.instance and self.instance.pk else (self.data.get('telephone') or '')
		telephone_value = (telephone_value or '').strip()
		country = ''
		number = telephone_value
		if telephone_value.startswith('+'):
			# extraire indicatif au début
			m = re.match(r"^(\+\d{1,3})\s*(.*)$", telephone_value)
			if m:
				country = m.group(1)
				number = m.group(2)
		self.fields['phone_country_code'].initial = country or '+224'
		self.fields['phone_number'].initial = number

	def clean_phone_number(self):
		value = (self.cleaned_data.get('phone_number') or '').strip()
		if not value:
			raise ValidationError("Le numéro de téléphone est obligatoire.")
		# Pas de validation de format: on accepte ce que l'utilisateur saisit
		return value

	def clean(self):
		cleaned = super().clean()
		number_value = cleaned.get('phone_number') or ''
		# Vérifier que le numéro de téléphone est fourni
		if not number_value:
			# Ajouter l'erreur au champ phone_number pour l'affichage
			self.add_error('phone_number', "Le numéro de téléphone est obligatoire.")
			return cleaned
		# Construit la valeur stockée "telephone": indicatif + numéro (format libre)
		country = cleaned.get('phone_country_code') or ''
		country = country.strip()
		if country and not country.startswith('+'):
			country = f'+{country}'
		cleaned['telephone'] = f"{country} {number_value}".strip()
		
		return cleaned

	def save(self, commit=True):
		# S'assure que le champ telephone est correctement rempli avant save
		self.instance.telephone = self.cleaned_data.get('telephone', self.instance.telephone)
		return super().save(commit=commit)

	def clean_email(self):
		"""Validation de l'email"""
		email = self.cleaned_data.get('email')
		if email:
			# Vérifier si l'email existe déjà
			if self.instance.pk:
				# Mode édition
				if Client.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
					raise ValidationError("Cette adresse email est déjà utilisée par un autre client.")
			else:
				# Mode création
				if Client.objects.filter(email=email).exists():
					raise ValidationError("Cette adresse email est déjà utilisée par un autre client.")
		return email

	def clean_nom_complet(self):
		"""Validation du nom complet"""
		nom_complet = self.cleaned_data.get('nom_complet')
		if not nom_complet:
			raise ValidationError("Le nom complet ou la raison sociale est obligatoire.")
		# Vérifier si le nom existe déjà
		if self.instance.pk:
			# Mode édition
			if Client.objects.filter(nom_complet=nom_complet).exclude(pk=self.instance.pk).exists():
				raise ValidationError("Un client avec ce nom existe déjà.")
		else:
			# Mode création
			if Client.objects.filter(nom_complet=nom_complet).exists():
				raise ValidationError("Un client avec ce nom existe déjà.")
		return nom_complet.strip()


class ClientSearchForm(forms.Form):
	"""Formulaire de recherche de clients"""

	SEARCH_CHOICES = [
		('nom', 'Nom/Raison sociale'),
		('telephone', 'Téléphone'),
		('email', 'Email'),
		('type', 'Type de client'),
		('statut', 'Statut'),
	]

	search_term = forms.CharField(
		required=False,
		widget=forms.TextInput(attrs={
			'class': 'form-control',
			'placeholder': 'Rechercher par nom, téléphone (+224626402000 ou 626402000)...',
			'autocomplete': 'off'
		})
	)

	search_by = forms.ChoiceField(
		choices=SEARCH_CHOICES,
		initial='nom',
		widget=forms.Select(attrs={
			'class': 'form-select'
		})
	)

	type_client = forms.ChoiceField(
		choices=[('', 'Tous les types')] + Client.TYPE_CHOICES,
		required=False,
		widget=forms.Select(attrs={
			'class': 'form-select'
		})
	)

	statut = forms.ChoiceField(
		choices=[
			('', 'Tous les statuts'),
			('actif', 'Actif'),
			('inactif', 'Inactif')
		],
		required=False,
		widget=forms.Select(attrs={
			'class': 'form-select'
		})
	)

	date_debut = forms.DateField(
		required=False,
		widget=forms.DateInput(attrs={
			'class': 'form-control',
			'type': 'date'
		})
	)

	date_fin = forms.DateField(
		required=False,
		widget=forms.DateInput(attrs={
			'class': 'form-control',
			'type': 'date'
		})
	)
