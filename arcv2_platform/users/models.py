from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from rest_framework.authtoken.models import Token

from arcv2_platform import settings


class UserManager(BaseUserManager):

    def create_user(self, email, firstname, lastname, affiliation=None, phone=None, is_active=False,
                    is_super_admin=False, is_moderator=False, is_validator=False,
                    is_requester=False, password=None, is_switch_user=False):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=self.normalize_email(email),
            email=self.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            affiliation=affiliation,
            phone=phone,
            is_moderator=is_moderator,
            is_validator=is_validator,
            is_requester=is_requester,
            is_active=is_active,
            is_super_admin=is_super_admin,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=self.normalize_email(email),
            email=self.normalize_email(email),
            firstname='Super',
            lastname='Admin',
            affiliation='super admin',
            created_by='Admin',
            phone=None,
        )

        user.is_active = True
        user.is_super_admin = True
        user.is_moderator = True
        user.is_validator = False
        user.is_requester = False
        user.set_password(password)
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    @classmethod
    def validators(cls):
        return cls.objects.filter(is_validator=True)

    @classmethod
    def moderators(cls):
        return cls.objects.filter(is_moderator=True)

    username = models.CharField(
        max_length=50,
        unique=True
    )

    firstname = models.CharField(
        max_length=50
    )

    lastname = models.CharField(
        max_length=50
    )

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True
    )

    affiliation = models.CharField(
        max_length=50,
        default=None,
        blank=True,
        null=True
    )

    phone = models.CharField(
        max_length=50,
        default=None,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_super_admin = models.BooleanField(
        default=False
    )

    is_moderator = models.BooleanField(
        default=False
    )

    is_validator = models.BooleanField(
        default=False
    )

    is_requester = models.BooleanField(
        default=False
    )

    created_by = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    creation_time = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )

    update_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    update_by = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )

    has_accepted_tos = models.BooleanField(
        default=False,
    )

    is_switch_user = models.BooleanField(
        default=False,
    )

    notification_enabled = models.BooleanField(
        default=True,
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]

    @property
    def is_supplier(self):
        return True

    @property
    def is_staff(self):
        return self.is_moderator or self.is_validator or self.is_super_admin

    @property
    def is_privileged(self):
        return self.is_moderator or self.is_validator

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_super_admin or self.is_validator or self.is_moderator

    def has_module_perms(self, app_label):
        return self.is_super_admin or self.is_validator or self.is_moderator

    @property
    def role_display(self):
        if self.is_moderator:
            return _("Moderator")
        if self.is_validator:
            return _("Validator")
        if self.is_requester:
            return _("Requester")
        return _("Supplier")


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
