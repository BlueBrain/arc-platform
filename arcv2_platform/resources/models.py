from django.db import models


class Resource(models.Model):
    name = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return self.name


class ResourceType(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    name = models.CharField(
        max_length=100,
    )

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='resource_types')

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = "Manufacturer"

    name = models.CharField(
        max_length=100,
    )

    resourceType = models.ForeignKey(
        ResourceType,
        on_delete=models.CASCADE,
        related_name='categories'
    )

    is_validated = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name


class CategoryItem(models.Model):
    name = models.CharField(
        max_length=200
    )

    comment = models.CharField(
        max_length=500,
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items'
    )

    is_validated = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return self.name
