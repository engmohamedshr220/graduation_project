from django.db import models
from django.contrib.auth.models import AbstractUser ,BaseUserManager
from django.contrib.auth.hashers import make_password
import uuid
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator







class City(models.Model):
    class CityChoices(models.TextChoices):
        # Menofia
        SHEBIN_EL_KOM = 'Shebin El-Kom', 'Shebin El-Kom'
        MENOUF = 'Menouf', 'Menouf'
        TOOKH_TANBESHA = 'Tookh Tanbesha', 'Tookh Tanbesha'
        QUESNA = 'Quesna', 'Quesna'
        BERKET_EL_SABAA = 'Berket El-Sabaa', 'Berket El-Sabaa'
        ASHAN = 'Ashan', 'Ashan'
        SHIBRA_BALLOULA = 'Shibra Balloula', 'Shibra Balloula'
        SADAT_CITY = 'Sadat City', 'Sadat City'

        # Cairo
        NASR_CITY = 'Nasr City', 'Nasr City'
        HELIOPOLIS = 'Heliopolis', 'Heliopolis'
        MAADI = 'Maadi', 'Maadi'
        ZAMALEK = 'Zamalek', 'Zamalek'
        DOWNTOWN = 'Downtown', 'Downtown'
        NEW_CAIRO = 'New Cairo', 'New Cairo'
        MOKATTAM = 'Mokattam', 'Mokattam'
        SHERATON = 'Sheraton', 'Sheraton'
        GARDEN_CITY = 'Garden City', 'Garden City'
        ABBASIA = 'Abbasia', 'Abbasia'

        # Alexandria
        SMOUHA = 'Smouha', 'Smouha'
        MIAMI = 'Miami', 'Miami'
        RUSHEDY = 'Roushdy', 'Roushdy'
        GLEEM = 'Gleem', 'Gleem'
        STANLEY = 'Stanley', 'Stanley'
        LOURAN = 'Louran', 'Louran'
        AL_MANSHEYA = 'Al Mansheya', 'Al Mansheya'
        BOLKLY = 'Bolkly', 'Bolkly'

        # Giza
        DOKKI = 'Dokki', 'Dokki'
        MOHANDSEEN = 'Mohandeseen', 'Mohandeseen'
        AGOUZA = 'Agouza', 'Agouza'
        HARAM = 'Haram', 'Haram'
        FAYSAL = 'Faysal', 'Faysal'
        OCTOBER = 'October', 'October'
        SHEIKH_ZAYED = 'Sheikh Zayed', 'Sheikh Zayed'
        IMBABA = 'Imbaba', 'Imbaba'
        
        NOT_SPECIFIED = 'Not Specified', 'Not Specified'
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    name = models.CharField(max_length=50, choices=CityChoices.choices)

    def __str__(self):
        return self.name
    


class MyUserManager(BaseUserManager):
    
    def _create_user(self,email,password=None, **extraFields):
        if not email :
            raise ValueError('email or password is missing')
        
        email =self.normalize_email(email)
        
        user =  self.model(email=email , **extraFields)
        user.password = make_password(password)
        user.save(using = self._db)
        return user
    
    def create_user(self, email, password=None,**extraFields):
        extraFields.setdefault('is_staff',False)
        extraFields.setdefault('is_superuser',False)
        return self._create_user(email,password,**extraFields)
    
    def create_superuser(self, email, password,**extraFields):
        extraFields.setdefault('is_staff',True)
        extraFields.setdefault('is_superuser',True)
        if extraFields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extraFields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email,password,**extraFields)


class User(AbstractBaseUser,PermissionsMixin):
    class Gender(models.TextChoices):
        MALE = 'male', 'male'
        FEMALE = 'female', 'female'
        NOT_SPECIFIED = 'not_specified', 'not_specified'
    class Role(models.TextChoices):
        ADMIN = 'admin','admin'
        PATIENT = 'patient','patient'
        DOCTOR = 'doctor','doctor'
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    name = models.CharField(max_length=254,null=True ,blank=True)
    username = models.CharField(verbose_name="username",max_length=254,unique=True,validators=[UnicodeUsernameValidator()],null=True,blank=True)
    email = models.EmailField(verbose_name="email",unique=True, max_length=254)
    phone = models.CharField(max_length=254 , unique=True,null=True , blank=True,verbose_name="phone")
    gender = models.CharField(max_length=50, choices=Gender.choices,default=Gender.NOT_SPECIFIED)
    city = models.ForeignKey(City , on_delete=models.SET_NULL , default=None , null=True , blank=True)
    role  =  models.CharField(max_length=50, choices=Role.choices , default=Role.PATIENT)
    
    is_staff = models.BooleanField(
        ("staff status"),
        default=False,
        help_text=("Designates whether the user can log into this admin site."),
    )
    is_superuser = models.BooleanField(
        ("super status"),
        default=False,
        help_text=("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        ("active"),
        default=True,
        help_text=(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(("date joined"), default=timezone.now)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','phone']

    objects =MyUserManager()



class PasswordResetCode(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_codes')
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return self.created_at < timezone.now() - timezone.timedelta(minutes=15)
    
    def __str__(self):
        return f'{self.user.email} - {self.code}'

class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True , unique=True , verbose_name="id", default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return self.created_at < timezone.now() - timezone.timedelta(minutes=15)
    
    def __str__(self):
        return f'{self.user.email} - {self.token}'

