"""
Database models.
"""
from django.conf import settings
from django.db import models
from django.contrib import auth
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email, URLValidator
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """Custom manager for users."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        if not email:
            raise ValueError("The given email must be set.")

        email = self.normalize_email(email)

        # TODO: probably redundant bc the model already has that validation!
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Email is not in correct format.")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """create a regular user"""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """create a superuser"""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)

    # i dont use this functionality so i could errase this method,
    # it is used to check user permissions based on a specific permission
    # string (perm)
    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None # noqa
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend # noqa
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractBaseUser, PermissionsMixin):
    """Custom deffined User in the system"""

    email = models.EmailField(
        _("email address"),
        max_length=255,
        unique=True,
        blank=False,
        help_text=_(
            "Required. It has to be a valid email, max 255 characters."
        ),
        error_messages={
            "unique": _("This email address already exists."),
        },
    )
    name = models.CharField(_("name"), max_length=255, blank=True)
    # only staff users can login to django admin
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."
            ),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    class Meta(AbstractBaseUser.Meta):
        verbose_name = _("user")
        verbose_name_plural = _("users")


class Recipe(models.Model):
    """Recipe object."""

    # this is relationship one to many,
    # one user, can have many recipe models
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
    )
    title = models.CharField(_("title"), max_length=255,)
    description = models.TextField(_("description"), blank=True,)
    time_minutes = models.IntegerField(_("time in minutes"))
    price = models.DecimalField(
        _("price"),
        max_digits=5,
        decimal_places=2,
    )
    link = models.CharField(
        _('link'),
        max_length=255,
        blank=True,
        validators=[URLValidator()],
    )

    def __str__(self) -> str:
        return self.title
