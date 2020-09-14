from django.db import models
from django.db.models import Case, When, Value, IntegerField, Sum
from django.db.models.functions import Coalesce
from django.utils.translation import gettext as _

from arcv2_platform.resources.models import Resource, Category, CategoryItem, ResourceType
from arcv2_platform.users.models import User


MAGIC_GENERIC_NAME = "Generic"

# TODO: move this to DB
CATEGORY_ITEM_INVISIBLE_TOKENS = ['Not applicable', 'not applicable', 'Other', '-']


class CommonData(models.Model):
    class Meta:
        abstract = True

    creation_time = models.DateTimeField(
        auto_now_add=True,
    )

    fullname = models.CharField(max_length=100)

    role = models.CharField(max_length=100)

    affiliation = models.CharField(max_length=100)

    email = models.EmailField()

    phone = models.CharField(max_length=25)

    author_comment = models.TextField(
        max_length=500,
        blank=True
    )

    update_time = models.DateTimeField(
        auto_now=True,
    )

    resource = models.ForeignKey(Resource, on_delete=models.PROTECT)

    resourceType = models.ForeignKey(ResourceType, on_delete=models.PROTECT)

    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    item = models.ForeignKey(CategoryItem, on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField()

    comment = models.TextField(
        max_length=400,
        blank=True,
    )

    @property
    def category_item(self):
        name = []

        if self.category and self.category.name not in CATEGORY_ITEM_INVISIBLE_TOKENS:
            name.append(self.category.name)
        if self.item:
            name.append(self.item.name)
        if len(name) == 0:
            name.append('-')

        return ' '.join(name)

    @property
    def full_category_item(self):
        name = []

        if self.resourceType and self.resourceType.name not in CATEGORY_ITEM_INVISIBLE_TOKENS:
            name.append(f'{self.resourceType.name}: ')

        name.append(self.category_item)

        return ' '.join(name)

    def __str__(self):
        me = self.__class__.__name__
        return f'[ {me} {self.id} ] {self.resource}: {self.category} {self.item}'


# Moved outside of Request class to be accessible inside Request.Meta subclass
# TODO: find alternative way to have Request.Priority subclass
class RequestPriority(models.TextChoices):
    CRITICAL = 'critical', _('Critical')
    HIGH = 'high', _('High')
    MEDIUM = 'medium', _('Medium')
    LOW = 'low', _('Low')


class Request(CommonData):
    class Status(models.TextChoices):
        SUBMITTED = 'submitted', _('Submitted')
        OPEN = 'open', _('Open')
        CLOSED = 'closed', _('Closed')
        ARCHIVED = 'archived', _('Archived')
        REJECTED = 'rejected', _('Rejected')

    class Meta:
        verbose_name_plural = "Requests"

        ordering = [Case(
            When(priority=RequestPriority.CRITICAL, then=Value(0)),
            When(priority=RequestPriority.HIGH, then=Value(1)),
            When(priority=RequestPriority.MEDIUM, then=Value(2)),
            When(priority=RequestPriority.LOW, then=Value(3)),
            output_field=IntegerField(),
        ), 'creation_time']

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_requests')

    updater = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_requests')

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )

    priority = models.CharField(
        max_length=10,
        choices=RequestPriority.choices,
        default=RequestPriority.MEDIUM,
    )

    sensitive = models.BooleanField(
        default=False,
    )

    expiry_notification_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    status_reason = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        default=None,
    )

    status_reason_sensitive = models.BooleanField(
        default=False
    )

    @property
    def remaining_quantity(self):
        if self.status == self.Status.CLOSED:
            return 0
        else:
            return self.quantity - self.quantity_validated

    @property
    def quantity_progress(self):
        return f'{self.quantity_validated} / {self.quantity}'

    @property
    def quantity_validated(self):
        return self.matches.filter(status__in=[Match.Status.VALIDATED, Match.Status.COMPLETED]).aggregate(sum=Coalesce(Sum('quantity'), 0))['sum']

    @property
    def quantity_to_validate(self):
        return self.matches.filter(status=Match.Status.ATTRIBUTED).count()

    @property
    def quantity_to_attribute(self):
        return self.get_available_supplies().count()

    @property
    def quantity_to_close(self):
        return self.matches.filter(status=Match.Status.VALIDATED).count()

    @property
    def has_attributed_supplies(self):
        return self.matches.filter(status=Match.Status.ATTRIBUTED).count() > 0

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    @property
    def is_expiring(self):
        if self.status != self.Status.OPEN:
            return False

        if not self.expiry_notification_time:
            return False

        return self.matches.count() == 0 and self.expiry_notification_time > self.update_time

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    @property
    def is_archived(self):
        return self.status == self.Status.ARCHIVED

    @property
    def can_be_archived(self):
        return self.matches.count() == 0 and self.status == self.Status.OPEN

    @property
    def can_be_closed(self):
        return self.matches.count() > 0 and self.quantity_to_validate == 0 and self.status == self.Status.OPEN

    @property
    def can_be_validated(self):
        return self.status == Request.Status.SUBMITTED

    @property
    def can_be_rejected(self):
        return self.status == Request.Status.SUBMITTED

    @property
    def can_be_reopened(self):
        return self.status in [Request.Status.CLOSED, Request.Status.ARCHIVED]

    @property
    def can_be_edited(self):
        return self.status not in [Request.Status.CLOSED, Request.Status.ARCHIVED, Request.Status.REJECTED]

    @property
    def priority_can_be_set(self):
        return self.status in [Request.Status.SUBMITTED, Request.Status.OPEN]

    @property
    def sensitivity_can_be_set(self):
        return self.status in [Request.Status.SUBMITTED]

    def get_available_supplies(self):
        if self.category.name == MAGIC_GENERIC_NAME:
            supplies = Supply.objects.filter(
                status=Supply.Status.AVAILABLE,
                resource=self.resource,
                resourceType=self.resourceType,
                item=self.item,
            )
        else:
            supplies = Supply.objects.filter(
                status=Supply.Status.AVAILABLE,
                resource=self.resource,
                resourceType=self.resourceType,
                category=self.category,
                item=self.item,
            )

        return supplies


class Supply(CommonData):
    class Meta:
        verbose_name_plural = "Supplies"
        ordering = ['-creation_time']

    class Status(models.TextChoices):
        AVAILABLE = 'available', _('Available')
        ONGOING_ATTRIBUTION = 'ongoing_attribution', _('Attributed but not validated')
        ATTRIBUTED = 'attributed', _('Validated')
        ARCHIVED = 'archived', _('Archived')
        CLOSED = 'closed', _('Closed')

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_supplies')

    updater = models.ForeignKey(User, on_delete=models.PROTECT, related_name='updated_supplies')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    company = models.CharField(
        max_length=100,
        blank=True,
    )

    street_name = models.CharField(
        max_length=100,
        blank=True,
    )

    street_number = models.CharField(
        max_length=20,
        blank=True,
    )

    city = models.CharField(
        max_length=50,
        blank=True,
    )

    zip = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    item_catalog_number = models.CharField(
        max_length=50,
        blank=True,
    )

    @property
    def remaining_quantity(self):
        if self.status == self.Status.ATTRIBUTED:
            return 0
        else:
            return self.quantity - self.quantity_validated

    @property
    def quantity_validated(self):
        return self.matches.filter(status__in=[Match.Status.VALIDATED, Match.Status.COMPLETED]).aggregate(sum=Coalesce(Sum('quantity'), 0))['sum']

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE

    @property
    def is_ongoing(self):
        return self.status == self.Status.ONGOING_ATTRIBUTION

    @property
    def is_attributed(self):
        return self.status == self.Status.ATTRIBUTED

    @property
    def is_archived(self):
        return self.status == self.Status.ARCHIVED

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    @property
    def can_be_archived(self):
        return self.matches.count() == 0 and self.status == self.Status.AVAILABLE

    @property
    def can_be_closed(self):
        return self.status != self.Status.CLOSED

    @property
    def can_be_edited(self):
        return self.status != self.Status.CLOSED

    @property
    def has_address(self):
        return self.company or self.street_name or self.city


class Match(models.Model):
    class Status(models.TextChoices):
        ATTRIBUTED = 'attributed', _('Attributed')
        ON_HOLD = 'on_hold', _('On hold')
        REJECTED = 'rejected', _('Rejected')
        VALIDATED = 'validated', _('Validated')
        COMPLETED = 'completed', _('Completed')

    creation_time = models.DateTimeField(
        auto_now_add=True,
    )

    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_matches')

    validator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='validated_matches',
        blank=True,
        null=True,
        default=None,
    )

    quantity = models.PositiveIntegerField()

    request = models.ForeignKey(Request, on_delete=models.PROTECT, related_name='matches')

    supply = models.ForeignKey(Supply, on_delete=models.PROTECT, related_name='matches')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ATTRIBUTED,
    )

    status_reason = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        default=None,
    )

    @property
    def is_attributed(self):
        return self.status == self.Status.ATTRIBUTED

    @property
    def is_on_hold(self):
        return self.status == self.Status.ON_HOLD

    @property
    def is_rejected(self):
        return self.status == self.Status.REJECTED

    @property
    def is_validated(self):
        return self.status == self.Status.VALIDATED

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED
