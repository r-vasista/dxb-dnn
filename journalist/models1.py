from django.db import models
import random
import string
import pycountry
from django_countries.fields import CountryField
from cities_light.models import Country, Region, City 
import phonenumbers
from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Qualification(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CountryCode(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dial_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.dial_code})"
    
    @classmethod
    def populate_country_codes(cls):
        """Fetch and store all country codes in the database with correct names."""
        existing_codes = set(cls.objects.values_list("dial_code", flat=True))  # Fetch existing dial codes

        for code, regions in _COUNTRY_CODE_TO_REGION_CODE.items():
            dial_code = f"+{code}"

            if dial_code in existing_codes:
                continue  # Skip duplicate country codes
            
            for region in regions:
                country = pycountry.countries.get(alpha_2=region)  # Get country by ISO code
                if country:
                    cls.objects.create(name=country.name, dial_code=dial_code)  # Direct insert
                    existing_codes.add(dial_code)  # Mark as inserted
                    break  # Only insert one country per dial code

    
class Journalist(models.Model):
    username = models.CharField(max_length=50, unique=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    alternative_phone_number = models.CharField(max_length=20, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    nationality = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.ForeignKey(Region, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)

    languages = models.ManyToManyField(Language, blank=True)  
    higher_education = models.ForeignKey(Qualification, on_delete=models.SET_NULL, blank=True, null=True)
    social_media_links = models.JSONField(default=dict, blank=True, null=True)
    selected_equipment = models.ManyToManyField(Equipment, blank=True)   
    passport_document = models.FileField(upload_to='documents/passport', blank=True, null=True)
    government_document = models.FileField(upload_to='documents/government/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    biography = models.TextField(blank=True, null=True, verbose_name="biography (max 120 characters)")
    terms_accepted = models.BooleanField(default=False)
    password = models.CharField(max_length=128, default="defaultpassword")
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        """Generate username automatically before saving."""
        if not self.username:
            self.username = self.generate_unique_username().upper() 
        super().save(*args, **kwargs)

    def generate_unique_username(self):
        """Generate a username using the first 4 characters of first_name + 4 random digits."""
        first_part = (self.first_name[:4].lower() if self.first_name else "user")
        random_part = "".join(random.choices(string.digits, k=4))
        username = first_part + random_part

        while Journalist.objects.filter(username=username).exists():
            random_part = "".join(random.choices(string.digits, k=4))
            username = first_part + random_part

        return username

    def __str__(self):
        return self.username