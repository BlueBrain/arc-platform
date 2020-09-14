from django import forms
from django.core.validators import MinValueValidator, EMPTY_VALUES

from arcv2_platform.matchmaking.models import Request, RequestPriority, Supply
from django.utils.translation import gettext as _

from arcv2_platform.app.widgets import ArcSelect
from arcv2_platform.resources.models import Category, CategoryItem


class ModelRSForm(forms.ModelForm):
    def __init__(self, resource_types, categories, items, *args, **kwargs):
        super(ModelRSForm, self).__init__(*args, **kwargs)
        self.fields['resource'].label = _("Type")
        self.fields['resourceType'].queryset = resource_types
        self.fields['resourceType'].label = _("Category")
        self.fields['category'].queryset = categories
        self.fields['category'].label = _("Manufacturer")
        self.fields['item'].queryset = items
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            self.fields['resource'].widget.attrs['readonly'] = True
            self.fields['resource'].widget.attrs['disabled'] = True

    class Meta:
        fields = [
            "fullname",
            "role",
            "affiliation",
            "email",
            "phone",
            "author_comment",
            "quantity",
            "resource",
            "resourceType",
            "category",
            "item",
        ]

        labels = {
            "author_comment": _("Brief comment"),
            "item": _("Name")
        }

        widgets = {
            'author_comment': forms.Textarea(attrs={'rows': 4}),
            'comment': forms.Textarea(attrs={'rows': 4}),
            'resource': ArcSelect(addValue=False, attrs={"v-model": "resource"}),
            'resourceType': ArcSelect(addValue=False,
                                      attrs={"v-model": "resourceType", ":allowed": "allowed_resourceType"}),
            'category': ArcSelect(addValue=False, attrs={"v-model": "category", ":allowed": "allowed_categories"}),
            'item': ArcSelect(addValue=False, attrs={"v-model": "item", ":allowed": "allowed_items"})
        }

    product_is_missing = forms.BooleanField(
        required=False,
    )

    new_category = forms.CharField(
        max_length=50,
        required=False,
        label=_('New or existing manufacturer')
    )

    new_category_item = forms.CharField(
        max_length=50,
        required=False,
        label=_('New item')
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=ArcSelect(
            addValue=False,
            attrs={
                'v-model': 'category',
                ':allowed': 'allowed_categories',
                ':required': '!product_is_missing'
            }
        )
    )

    item = forms.ModelChoiceField(
        queryset=CategoryItem.objects.all(),
        required=False,
        widget=ArcSelect(
            addValue=False,
            attrs={
                'v-model': 'item',
                ':allowed': 'allowed_items',
                ':required': '!product_is_missing'
            }
        )
    )

    def clean_sku(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk:
            return instance.sku
        else:
            return self.cleaned_data['resource']

    def clean(self):
        product_is_missing = self.cleaned_data.get('product_is_missing', False)
        new_category = self.cleaned_data.get('new_category', None)
        new_category_item = self.cleaned_data.get('new_category_item', None)
        category = self.cleaned_data.get('category', None)
        item = self.cleaned_data.get('item', None)

        if product_is_missing:
            if new_category in EMPTY_VALUES:
                self._errors['new_category'] = self.error_class(
                    [_('New or existing manufacturer is required if you ticked "My product is not in the list"')])
            if new_category_item in EMPTY_VALUES:
                self._errors['new_category_item'] = self.error_class(
                    [_('New name is required if you ticked "My product is not in the list"')])
        else:
            if category in EMPTY_VALUES:
                self._errors['category'] = self.error_class(
                    [_('Category is required unless you tick "My product is not in the list"')])
            if item in EMPTY_VALUES:
                self._errors['item'] = self.error_class(
                    [_('Name is required unless you tick "My product is not in the list"')])

        return self.cleaned_data

    def save(self, commit=True):
        product_is_missing = self.cleaned_data.get('product_is_missing', False)
        print(self._errors)

        if product_is_missing:
            resource_type = self.instance.resourceType

            new_category = self.cleaned_data.get('new_category')

            category, created = Category.objects.get_or_create(name=new_category, resourceType=resource_type)
            if created:
                category.is_validated = False
                category.save()
            self.instance.category = category

            new_category_item = self.cleaned_data.get('new_category_item')

            item, created = CategoryItem.objects.get_or_create(name=new_category_item, category=category)
            if created:
                item.is_validated = False
                item.save()
            self.instance.item = item

        return super(ModelRSForm, self).save(commit)


class ModelSupplyForm(ModelRSForm):
    class Meta(ModelRSForm.Meta):
        model = Supply
        fields = ModelRSForm.Meta.fields + ['company', 'street_name', 'street_number', 'city', 'zip',
                                            'item_catalog_number']


class ModelRequestForm(ModelRSForm):
    class Meta(ModelRSForm.Meta):
        model = Request

        fields = ModelRSForm.Meta.fields + ['sensitive', 'priority']

        help_texts = {
            'sensitive': _(
                'Sensitive request, the identity of requester will be revealed only after the attribution validation.')
        }


class ValidateAttributionForm(forms.Form):
    available = forms.IntegerField(
        disabled=True,
        label=_("Supply availability"),
        widget=forms.NumberInput(attrs={'v-model': 'available'}),
        min_value=0,
        validators=[
            MinValueValidator(0)
        ]
    )
    attributed = forms.IntegerField(
        label=_("Attributed quantity"),
        widget=forms.NumberInput(attrs={'v-model': 'attributed', ':allowed': 'hasError', 'pattern': '^[0-9]'}),
        min_value=0,
        validators=[
            MinValueValidator(0)
        ]
    )
    remaining = forms.IntegerField(
        disabled=True,
        label=_("Remaining availability"),
        widget=forms.NumberInput(attrs={'v-model': 'remaining'}),
        min_value=0,
        validators=[
            MinValueValidator(0)
        ]
    )
    requestQuantity = forms.IntegerField(
        disabled=True,
        label=_("Remaining availability"),
        widget=forms.NumberInput(attrs={'v-model': 'requestQuantity'}),
        min_value=0,
        validators=[
            MinValueValidator(0)
        ]
    )


class ConfirmationForm(forms.Form):
    confirm_message = forms.CharField(
        required=True,
        max_length=500
    )


class RejectRequestForm(forms.Form):
    status_reason = forms.CharField(
        required=True,
        max_length=500,
    )

    status_reason_sensitive = forms.BooleanField(
        initial=False,
        required=False,
    )

    redirect_url = forms.CharField(
        max_length=100,
        required=False,
    )


class SetRequestPriorityForm(forms.Form):
    priority = forms.ChoiceField(
        choices=RequestPriority.choices
    )

    redirect_url = forms.CharField(
        max_length=100,
        required=False,
    )


class SetRequestSensitivityForm(forms.Form):
    sensitive = forms.BooleanField(
        initial=False,
        required=False,
    )

    redirect_url = forms.CharField(
        max_length=100,
        required=False,
    )
