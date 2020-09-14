from enum import Enum
import unicodecsv as csv
from io import BytesIO

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.db.models import Count, Case, When, IntegerField, Value
from django.core.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from arcv2_platform.config.config import config
from arcv2_platform.app.decorators import role_required
from arcv2_platform.app.mixins import RoleRequiredMixin, ResourceDownloadMixin
from arcv2_platform.matchmaking.forms import ModelRequestForm, ValidateAttributionForm, ConfirmationForm, \
    ModelSupplyForm, RejectRequestForm, SetRequestPriorityForm, SetRequestSensitivityForm
from django.http import HttpResponseRedirect, Http404, HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.list import ListView

from arcv2_platform.matchmaking.models import Request, RequestPriority, Supply, Match
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _

from arcv2_platform.matchmaking.permissions import AccessSupplyAPIPermission, AccessRequestAPIPermission
from arcv2_platform.matchmaking.resources import RequestResource, SupplyResource
from arcv2_platform.matchmaking.serializers import RequestSerializer, SupplySerializer
from arcv2_platform.resources.models import Resource, CategoryItem, Category, ResourceType
from arcv2_platform.app.models import Role
import arcv2_platform.matchmaking.services as services

TYPE_QUERY_PARAM = 'type'
RESOURCE_TYPE_QUERY_PARAM = 'resource_type'
STATUS_QUERY_PARAM = 'status'
PRIORITY_QUERY_PARAM = 'priority'
ACTION_QUERY_PARAM = 'action'


# TODO: Refactor to reduce complexity
@login_required  # noqa: C901
def supply_create(request, pk=None):
    is_new = pk is None
    form_object = get_object_or_404(Supply, pk=pk) if not is_new else None
    source_id = request.GET.get('source', None)

    allowed_roles = [Role.moderator, Role.validator]

    if not is_new:
        if not (Role.validate_roles(request.user, allowed_roles) or form_object.creator == request.user):
            raise PermissionDenied()

    initial_data = _get_source_data(Supply, source_id) if is_new and source_id else {}

    if is_new:
        resource_obj = None
    else:
        resource_obj = form_object.resource

    resource_types, categories, items, relations = _get_categories_items(resource_obj)

    if request.method == "POST":

        # little hack to make edit save and add new with resource disabled
        if not is_new:
            request_post = request.POST.copy()
            request_post['resource'] = form_object.resource
        else:
            request_post = request.POST

        form = ModelSupplyForm(
            resource_types,
            categories,
            items,
            request_post,
            initial=initial_data,
            instance=form_object
        )

        if form.is_valid():

            obj = form.save(commit=False)
            if is_new:
                obj.creator = request.user
                obj.resource = form.cleaned_data.get('resource')
            obj.updater = request.user
            obj.save()

            url = reverse("supplies-detail", kwargs={'pk': obj.id})

            # flash message
            _send_flash_on_save(request, obj, is_new, "supply", url)

            # redirect
            if request.POST.get('add-new', False):
                base_url = reverse("supplies-create")
                url = f"{base_url}?source={obj.id}"

            return HttpResponseRedirect(url)
    else:
        if is_new:
            user = request.user

            initial_data = dict(
                initial_data,
                fullname=f'{user.firstname} {user.lastname}',
                affiliation=user.affiliation,
                email=user.email,
                phone=user.phone,
            )
        else:
            initial_data = dict(
                initial_data,
                new_category=form_object.category.name,
                new_category_item=form_object.item.name,
            )

        form = ModelSupplyForm(
            resource_types,
            categories,
            items,
            initial=initial_data,
            instance=form_object,
        )

    return render(request,
                  'matchmaking/supply_create.html',
                  {
                      "form": form,
                      "relations": relations,
                      "title": (_("New Supply") if is_new else _("Edit %s Supply") % resource_obj.name.capitalize()),
                      'product_is_missing': _get_product_is_missing(form_object),
                  })


def _get_product_is_missing(form_object):
    return form_object is not None and (not form_object.category.is_validated or not form_object.item.is_validated)


@login_required  # noqa: C901
@role_required(roles=[Role.validator, Role.moderator, Role.requester])
def request_create(request, pk=None):
    is_new = pk is None

    form_object = get_object_or_404(Request, pk=pk) if not is_new else None
    source_id = request.GET.get('source', None)

    # requester without Validator or Moderator role can edit only own requests
    if not is_new:
        is_admin = Role.validate_roles(request.user, [Role.validator, Role.moderator])
        if not is_admin and form_object.creator != request.user:
            raise PermissionDenied

    initial_data = _get_source_data(Request, source_id) if is_new and source_id else {}

    if is_new:
        resource_obj = None
    else:
        resource_obj = form_object.resource

    resource_types, categories, items, relations = _get_categories_items(resource_obj)

    if request.method == "POST":
        # little hack to make edit save and add new with resource disabled
        if not is_new:
            request_post = request.POST.copy()
            request_post['resource'] = form_object.resource
        else:
            request_post = request.POST

        form = ModelRequestForm(
            resource_types,
            categories,
            items,
            request_post,
            initial=initial_data,
            instance=form_object
        )

        if form.is_valid():

            obj = form.save(commit=False)
            if is_new:
                obj.creator = request.user
                obj.resource = form.cleaned_data.get('resource')

            obj.updater = request.user
            obj.save()

            if is_new:
                services.notify_validators_w_submitted_request(obj)

            url = reverse("request-detail", kwargs={'pk': obj.id})

            # flash message
            _send_flash_on_save(request, obj, is_new, "request", url)

            # redirect
            if request.POST.get('add-new', False):
                base_url = reverse("requests-create")
                url = f"{base_url}?source={obj.id}"

            return HttpResponseRedirect(url)
    else:
        if is_new:
            user = request.user

            initial_data = dict(
                initial_data,
                fullname=f'{user.firstname} {user.lastname}',
                affiliation=user.affiliation,
                email=user.email,
                phone=user.phone,
            )
        else:
            initial_data = dict(
                initial_data,
                new_category=form_object.category.name,
                new_category_item=form_object.item.name,
            )

        form = ModelRequestForm(
            resource_types,
            categories,
            items,
            instance=form_object,
            initial=initial_data
        )

    return render(request,
                  'matchmaking/request_create.html',
                  {
                      "form": form,
                      "mode": request.session.get('mode', None),
                      "relations": relations,
                      "title": (_("New Request") if is_new else _("Edit %s Request") % resource_obj.name.capitalize()),
                      "product_is_missing": _get_product_is_missing(form_object),
                  })


class CommonListView(LoginRequiredMixin, RoleRequiredMixin, ResourceDownloadMixin, ListView):
    paginate_by = 100

    def create_db_filter_from_params(self, properties):
        """Creates a dict meant to be used as ORM filter argument. The properties parameter is a list of tuples
        (name, query_filter) where name is the name of the GET parameter that contains the value to match in the filter
        and query_filter the name of the model property to filter."""

        filters = dict()

        for name, query_filter in properties:
            if name == TYPE_QUERY_PARAM:
                value = self.get_int_param(name)
            else:
                value = self.request.GET.get(name, None)
            if value is not None and value != '':
                filters[query_filter] = value

        return filters

    def get_int_param(self, name):
        if self.request.GET.get(name):
            try:
                return int(self.request.GET.get(name))
            except ValueError:
                return None
        else:
            return None

    def create_filter(self, title, query_param, options, param_is_number=False):
        if param_is_number:
            selected_value = self.get_int_param(query_param)
        else:
            selected_value = self.request.GET.get(query_param, None)

        return {
            "title": title,
            "name": query_param,
            "value": selected_value,
            "options": options
        }


class RequestListView(CommonListView):
    model = Request
    resource_filename = _("requests")
    resource_class = RequestResource
    ordering = ['creation_time']
    roles = [Role.moderator, Role.validator, Role.supplier]
    template_name = 'matchmaking/request_list.html'
    mode = None

    class Mode(Enum):
        OWN = 'own'  # My Requests dashboard
        SUBMITTED = 'submitted'  # Request Submissions dashboard

    class Action(Enum):
        TO_ATTRIBUTE = ('to_attribute', _('To Attribute'))
        TO_VALIDATE = ('to_validate', _('To Validate'))
        TO_ATTRIBUTE_AND_VALIDATE = ('to_attribute_or_validate', _('To Attribute or Validate'))
        TO_CLOSE = ('to_close', _('To Close'))
        NO_ACTION = ('no_action', _('No Action'))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.mode = request.GET.get('mode', None)
        request.session['mode'] = self.mode

        return super(RequestListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):  # noqa: C901
        # TODO:
        # * create separate views and templates for request dashboards to decrease complexity
        # * optimize DB queries
        filters = self.create_db_filter_from_params([
            (PRIORITY_QUERY_PARAM, 'priority'),
            (STATUS_QUERY_PARAM, 'status'),
            (TYPE_QUERY_PARAM, 'resource__id'),
            (RESOURCE_TYPE_QUERY_PARAM, 'resourceType__id'),
        ])

        if not Role.validate_roles(self.request.user, [Role.moderator, Role.validator, Role.requester]):
            # show only open for supplier
            queryset = Request.objects.filter(**filters, status=Request.Status.OPEN)
        else:
            queryset = Request.objects.filter(**filters)

        if self.mode == self.Mode.OWN.value:
            queryset = queryset.filter(creator=self.request.user.id).annotate(status_num=Case(
                When(status=Request.Status.OPEN.value, then=Value(0)),
                When(status=Request.Status.SUBMITTED.value, then=Value(1)),
                When(status=Request.Status.REJECTED.value, then=Value(2)),
                When(status=Request.Status.ARCHIVED.value, then=Value(3)),
                When(status=Request.Status.CLOSED.value, then=Value(4)),
                output_field=IntegerField(),
            )).order_by('status_num')
        elif self.mode == self.Mode.SUBMITTED.value:
            queryset = queryset.filter(status__in=[Request.Status.SUBMITTED, Request.Status.REJECTED]).annotate(priority_num=Case(
                When(priority=RequestPriority.CRITICAL.value, then=Value(0)),
                When(priority=RequestPriority.HIGH.value, then=Value(1)),
                When(priority=RequestPriority.MEDIUM.value, then=Value(2)),
                When(priority=RequestPriority.LOW.value, then=Value(3)),
                output_field=IntegerField(),
            )).order_by('-status', 'priority_num')
        else:
            queryset = queryset.exclude(status__in=[Request.Status.SUBMITTED, Request.Status.REJECTED])

        if not self.mode and self.request.user.is_requester:
            queryset = queryset.filter(status=Request.Status.OPEN)

        expiration = self.request.GET.get('expiration', None)
        if expiration == 'expiring':
            now = timezone.now()
            expiration_time = now - timezone.timedelta(days=config.request.expiration_days)
            queryset = queryset.filter(
                status=Request.Status.OPEN,
            ).annotate(
                matches_count=Count('matches')
            ).filter(
                update_time__lt=expiration_time,
                matches_count=0
            )

        # Note on the action filter: it cannot be used as the other filters since we are filtering on properties
        # (quantity_to_attribute and quantity_to_validate) and not on model fields. An Action Enum has been created to
        # mimic the Status and Priority TextChoices, and therefore having the same behavior on the html filter.

        action = self.request.GET.get("action", None)

        if action:
            queryset = [request for request in queryset if request.status == Request.Status.OPEN]
            if action == self.Action.TO_ATTRIBUTE.value[0]:
                queryset = [request for request in queryset if request.quantity_to_attribute > 0]
            elif action == self.Action.TO_VALIDATE.value[0]:
                queryset = [request for request in queryset if request.quantity_to_validate > 0]
            elif action == self.Action.TO_ATTRIBUTE_AND_VALIDATE.value[0]:
                queryset = [request for request in queryset
                            if (request.quantity_to_attribute > 0 or request.quantity_to_validate > 0)]
            elif action == self.Action.TO_CLOSE.value[0]:
                queryset = [request for request in queryset
                            if request.quantity_to_close > 0]
            elif action == self.Action.NO_ACTION.value[0]:
                queryset = [request for request in queryset
                            if (request.quantity_to_attribute == 0 and request.quantity_to_validate == 0)]

        return queryset

    def get_context_data(self, **kwargs):
        context = super(RequestListView, self).get_context_data(**kwargs)

        resources = _all_resources()
        resource_id = self.get_int_param(TYPE_QUERY_PARAM)
        resource_types = _resource_types_for_resource(resource_id)
        context["resources"] = resources
        context['set_request_priority_form'] = SetRequestPriorityForm()

        show_extra_fields = Role.validate_roles(self.request.user, [Role.moderator, Role.validator])
        context["show_extra_fields"] = show_extra_fields
        context["mode"] = self.mode
        context["owner_mode"] = self.mode == self.Mode.OWN.value

        # Remove submitted and rejected statuses from a filter on Request Submissions dashboard
        st_to_skip = [Request.Status.SUBMITTED.value, Request.Status.REJECTED.value]
        choices = Request.Status.choices
        req_status_choices = choices if self.mode else [c for c in choices if c[0] not in st_to_skip]

        # For My requests page action filter contains only `To Close` option (along with `All`)
        action_choices = [
            action.value
            for action
            in self.Action
            if self.mode != 'own' or action.value == self.Action.TO_CLOSE.value
        ]

        context["filters"] = {
            "status": self.create_filter(_('Status'), STATUS_QUERY_PARAM, req_status_choices),
            "type": self.create_filter(_('Type'), TYPE_QUERY_PARAM, resources, param_is_number=True),
            "resource_type": self.create_filter(_('Category'), RESOURCE_TYPE_QUERY_PARAM, resource_types,
                                                param_is_number=True),
            "priority": self.create_filter(_('Priority'), PRIORITY_QUERY_PARAM, RequestPriority.choices),
            "action": self.create_filter(_('Action'), ACTION_QUERY_PARAM, action_choices),
            "expiration": self.create_filter(_('Expiration'), 'expiration', [('expiring', _('Expiring'))]),
        }

        return context


def _supply_csv_properties(supply):
    return [
        supply.resource.name,
        supply.resourceType.name,
        supply.category.name,
        supply.item.name,
        supply.fullname,
        supply.role,
        supply.affiliation,
        supply.email,
        supply.phone,
        supply.author_comment,
        supply.remaining_quantity,
    ]


def _match_csv_properties(match):
    def _status_display(status):
        if status == Match.Status.ATTRIBUTED:
            return 'ongoing attribution'
        else:
            return 'validated'

    request = match.request

    return [
        match.quantity,
        _status_display(match.status),
        request.fullname,
        request.role,
        request.affiliation,
        request.email,
        request.phone,
        request.author_comment,
        request.priority,
    ]


def _remove_commas(item):
    if not isinstance(item, str):
        item = str(item)

    return item.replace(',', '')


class SupplyListView(CommonListView):
    model = Supply
    resource_filename = _("supplies")
    resource_class = SupplyResource
    ordering = ['-creation_time']
    roles = [Role.moderator, Role.validator, Role.supplier]

    def render_to_response(self, *args, **kwargs):
        if self._download_parameter in self.request.GET:
            return self.render_to_download_response(*args, **kwargs)
        return super().render_to_response(*args, **kwargs)

    def render_to_download_response(self, *args, **kwargs):
        if self.request.method != 'GET':
            return HttpResponseNotAllowed(['GET'])

        lines = [
            [
                'Type',
                'Category',
                'Manufacturer',
                'Item',
                'Supplier fullname',
                'Supplier role',
                'Supplier affiliation',
                'Supplier email',
                'Supplier phone',
                'Supplier brief comment',
                'Remaining quantity',
                'Attributed quantity',
                'Attribution status',
                'Requester fullname',
                'Requester role',
                'Requester affiliation',
                'Requester email',
                'Requester phone',
                'Requester brief comment',
                'Request priority',
            ]
        ]

        supplies = self.get_queryset()

        for supply in supplies:
            if supply.matches.all().count() == 0:
                lines.append(_supply_csv_properties(supply) + [''] * 9)
            else:
                for match in supply.matches.all():
                    lines.append(_supply_csv_properties(supply) + _match_csv_properties(match))
        output = BytesIO()
        writer = csv.writer(output, encoding='utf-8-sig', quoting=csv.QUOTE_NONNUMERIC)
        for line in lines:
            writer.writerow(line)
        csv_text = output.getvalue()

        return HttpResponse(csv_text, content_type='text/csv')

    def get_queryset(self):
        if Role.validate_roles(self.request.user, [Role.moderator, Role.validator]):
            queryset = Supply.objects.all()
        else:
            queryset = Supply.objects.filter(creator=self.request.user)

        filters = self.create_db_filter_from_params([
            (STATUS_QUERY_PARAM, 'status'),
            (TYPE_QUERY_PARAM, 'resource__id'),
            (RESOURCE_TYPE_QUERY_PARAM, 'resourceType__id'),
        ])

        return queryset.filter(**filters)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(SupplyListView, self).get_context_data(**kwargs)

        resources = _all_resources()
        resource_id = self.get_int_param(TYPE_QUERY_PARAM)
        resource_types = _resource_types_for_resource(resource_id)
        context["resources"] = resources

        context["filters"] = {
            "status": self.create_filter(_('Status'), STATUS_QUERY_PARAM, Supply.Status.choices),
            "type": self.create_filter(_('Type'), TYPE_QUERY_PARAM, resources, param_is_number=True),
            "resource_type": self.create_filter(_('Category'), RESOURCE_TYPE_QUERY_PARAM, resource_types,
                                                param_is_number=True),
        }

        return context


def _group_by_category(state, item):
    item_id = item.id
    category_id = item.category.id
    if category_id not in state.keys():
        state[category_id] = []
    state[category_id].append(item_id)
    return state


def _get_categories_items(resource_obj=None):
    if resource_obj is not None:
        resources = resource_obj
        resource_types = resource_obj.resource_types
        categories = Category.objects.filter(resourceType__in=resource_types.values_list('id'), is_validated=True)
        category_items = CategoryItem.objects.filter(category__in=categories.values_list('id'), is_validated=True)
    else:
        resources = Resource.objects.all()
        resource_types = ResourceType.objects.all()
        categories = Category.objects.filter(is_validated=True)
        category_items = CategoryItem.objects.filter(is_validated=True)

    relations = {}
    if not isinstance(resources, Resource):
        for resource_id in list(resources.values_list('id', flat=True)):
            relations[resource_id] = {"type": resource_id, "resource": {}}
    else:
        relations[resources.id] = {"type": resources.id, "resource": {}}

    mapping_resource_type = {}
    for resource_type_id, resource_id in list(resource_types.values_list('id', 'resource')):
        relations[resource_id][resource_type_id] = {"resource": resource_type_id, "categories": {}}
        mapping_resource_type[resource_type_id] = resource_id

    mapping_category_resource = {}
    for category_id, resource_type_id in list(categories.values_list('id', 'resourceType')):
        resource_id = mapping_resource_type[resource_type_id]

        relations[resource_id][resource_type_id]["categories"][category_id] = {"category": category_id, "items": {}}
        mapping_category_resource[category_id] = resource_type_id

    for category_item_id, category_id, comment, in list(category_items.values_list('id', 'category', 'comment')):
        resource_type_id = mapping_category_resource[category_id]
        resource_id = mapping_resource_type[resource_type_id]

        relations[resource_id][resource_type_id]["categories"][category_id]["items"][category_item_id] = {
            "item": category_item_id,
            "comment": comment
        }

    return resource_types, categories, category_items, relations


def _get_source_data(model, source_id):
    source_obj = get_object_or_404(model, pk=source_id)
    source_data = {
        'fullname': source_obj.fullname,
        'role': source_obj.role,
        'affiliation': source_obj.affiliation,
        'email': source_obj.email,
        'phone': source_obj.phone,
        'author_comment': source_obj.author_comment,
    }
    return source_data


def _send_flash_on_save(request, obj, is_new, entity_type, url):
    action = "added" if is_new else "saved"
    message = f'The <a href="{url}" class="link">{entity_type} {obj.id}</a> has been {action}.'
    messages.success(request, message)


def _all_resources():
    return Resource.objects.values_list('id', 'name')


def _resource_types_for_resource(resource_id):
    qs = ResourceType.objects.values_list('id', 'name')

    if resource_id is not None:
        qs = qs.filter(resource_id=resource_id)
    else:
        qs = sorted(list(qs), key=lambda e: e[1])

    return qs


class RequestDetailView(LoginRequiredMixin, DetailView):
    model = Request
    template_name = 'matchmaking/request_detail.html'
    context_object_name = 'object'
    mode = None
    roles = [Role.moderator, Role.validator, Role.requester]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.is_admin_access = Role.validate_roles(request.user, [Role.moderator, Role.validator])
        self.is_owner_access = self.get_object().creator == request.user

        if self.is_admin_access or self.is_owner_access:
            if self.is_owner_access and request.user.is_requester:
                self.mode = 'own'
            else:
                self.mode = request.session.get('mode', None)
            return super(RequestDetailView, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        request = self.get_object()

        context['available_supplies'] = request.get_available_supplies() if self.is_admin_access else []

        filter_dict = {} if self.is_admin_access else {'status__in': [Match.Status.VALIDATED, Match.Status.COMPLETED]}
        context['attributed_matches'] = list(request.matches.filter(**filter_dict))

        context['form'] = ValidateAttributionForm()
        context['set_request_priority_form'] = SetRequestPriorityForm()

        context['resources'] = _all_resources()

        context['is_admin_access'] = self.is_admin_access

        context['mode'] = self.mode

        return context


class SupplyDetailView(LoginRequiredMixin, RoleRequiredMixin, DetailView):
    model = Supply
    template_name = 'matchmaking/supply_detail.html'
    context_object_name = 'object'
    roles = [Role.supplier, Role.moderator, Role.validator]

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.is_admin_access = Role.validate_roles(request.user, [Role.moderator, Role.validator])
        self.is_owner_access = self.get_object().creator == request.user

        if self.is_admin_access or self.is_owner_access:
            return super(SupplyDetailView, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        supply = self.get_object()

        if self.is_admin_access:
            context['attributed_requests'] = set(
                map(lambda m: m.request,
                    supply.matches.only('request'))
            )

        context['resources'] = _all_resources()

        return context


@login_required
@role_required(roles=[Role.moderator, Role.validator, Role.requester])
def close_request(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    if not request.user.is_privileged and request_object.creator != request.user:
        raise(PermissionDenied)

    if request_object.can_be_closed:
        request_object.status = Request.Status.CLOSED
        request_object.save()
        msg = _('The request has been closed.')
        messages.success(request, msg)
    else:
        msg = _('The request has on going attribution. Closing it is not possible.')
        messages.error(request, msg)

    return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.validator])
def validate_request(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    redirect_url = request.GET.get('redirect_url', None)

    request_object.status = Request.Status.OPEN
    request_object.save()

    services.notify_moderators_w_open_request(request_object)
    services.notify_requester_w_validated_request(request_object)

    msg = _('The request status has been set to Open')
    messages.success(request, msg)

    return redirect(redirect_url) if redirect_url else redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.validator])
def reject_request(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        form = RejectRequestForm(request.POST)

        if form.is_valid():
            status_reason = form.cleaned_data.get('status_reason')
            status_reason_sensitive = form.cleaned_data.get('status_reason_sensitive')

            redirect_url = form.cleaned_data.get('redirect_url', None)

            request_object.status = Request.Status.REJECTED
            request_object.status_reason = status_reason
            request_object.status_reason_sensitive = status_reason_sensitive
            request_object.save()

            services.notify_requester_w_rejected_request(request_object)

            msg = _('The request status has been set to Rejected')
            messages.success(request, msg)

            return redirect(redirect_url) if redirect_url else redirect('request-detail', pk=pk)

    msg = _('Failed to set request status to Rejected')
    messages.error(request, msg)

    return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.validator])
def set_request_priority(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        form = SetRequestPriorityForm(request.POST)

        if form.is_valid():
            priority = form.cleaned_data.get('priority')
            redirect_url = form.cleaned_data.get('redirect_url', None)

            request_object.priority = priority
            request_object.save()
            msg = _(f'The request priority has been set to {priority}')
            messages.success(request, msg)

            return redirect(redirect_url) if redirect_url else redirect('request-detail', pk=pk)

    msg = _('Failed to update request priority')
    messages.error(request, msg)

    return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.validator])
def set_request_sensitivity(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    if request.method == 'POST':
        form = SetRequestSensitivityForm(request.POST)

        if form.is_valid():
            sensitive = form.cleaned_data.get('sensitive')
            redirect_url = form.cleaned_data.get('redirect_url', None)
            print(sensitive)

            request_object.sensitive = sensitive
            request_object.save()
            msg = _(f'The request has been set to {"not " if sensitive else ""}sensitive')
            messages.success(request, msg)

            return redirect(redirect_url) if redirect_url else redirect('request-detail', pk=pk)

    msg = _('Failed to update request priority')
    messages.error(request, msg)

    return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.supplier, Role.moderator, Role.validator])
def close_supply(request, pk):
    supply_object = get_object_or_404(Supply, pk=pk)
    allowed_roles = [Role.moderator, Role.validator]

    if not (Role.validate_roles(request.user, allowed_roles) or supply_object.creator == request.user):
        raise PermissionDenied()

    if supply_object.can_be_closed:
        supply_object.status = Supply.Status.CLOSED
        supply_object.save()

        supply_object.matches.exclude(status=Match.Status.COMPLETED).delete()

        msg = _('The supply has been closed.')
        messages.success(request, msg)
    else:
        msg = _('The supply is already closed.')
        messages.error(request, msg)

    return redirect('supplies-detail', pk=pk)


@login_required
@role_required(roles=[Role.supplier, Role.moderator, Role.validator])
def archive_supply(request, pk):
    supply_object = get_object_or_404(Supply, pk=pk)
    allowed_roles = [Role.moderator, Role.validator]

    if not (Role.validate_roles(request.user, allowed_roles) or supply_object.creator == request.user):
        raise PermissionDenied()

    if supply_object.can_be_archived:
        supply_object.status = Supply.Status.ARCHIVED
        supply_object.save()
        msg = _('The supply has been archived.')
        messages.success(request, msg)
    else:
        msg = _('The supply is on going attribution. Archiving it is not possible.')
        messages.error(request, msg)

    return redirect('supplies-detail', pk=pk)


@login_required
@role_required(roles=[Role.moderator, Role.validator])
def archive_request(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    if request_object.can_be_archived:
        # when archiving a request, all matches should be deleted
        # making matched resource quantity available in supply
        request_object.matches.all().delete()

        request_object.status = Request.Status.ARCHIVED
        request_object.save()
        msg = _('The request has been archived.')
        messages.success(request, msg)
    else:
        msg = _('The request has on going attributions. Archiving it is not possible.')
        messages.error(request, msg)

    return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.moderator, Role.validator])
def resurrect_request(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    if request_object.is_archived or request_object.is_closed:
        request_object.status = Request.Status.OPEN
        request_object.save()

        services.notify_moderators_w_open_request(request_object)
    else:
        msg = _('The request is not archived nor closed. Resurrection is not possible.')
        messages.error(request, msg)

    return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.moderator, Role.validator])
def unexpire_request(request, pk):
    request_object = get_object_or_404(Request, pk=pk)

    request_object.expiry_notification_time = None
    request_object.save()
    msg = _('Expiration status has been reset.')
    messages.success(request, msg)

    return redirect('request-detail', pk=pk)


# TODO: Refactor to reduce complexity
@login_required  # noqa: C901
@role_required(roles=[Role.validator])
def reject_attribution(request, pk=None, match_id=None):
    if match_id is None or pk is None:
        raise Exception("Parameter match_id and pk is required")

    try:
        match = get_object_or_404(Match, pk=match_id)
        # check request and supply are available
        supply_obj, request_obj = check_available(pk, match.supply.id, request)

        if request.method == 'POST':
            form = ConfirmationForm(request.POST)

            if form.is_valid():
                status_reason = form.cleaned_data.get('confirm_message')

                if match is not None:
                    # change status supply
                    if match.is_validated and supply_obj.is_ongoing:
                        supply_obj.status = Supply.Status.ONGOING_ATTRIBUTION
                    elif match.is_validated and supply_obj.is_attributed:
                        supply_obj.status = Supply.Status.AVAILABLE
                    elif match.is_attributed:
                        supply_obj.status = Supply.Status.AVAILABLE
                    elif match.is_on_hold:
                        supply_obj.status = Supply.Status.AVAILABLE

                supply_obj.save()

                # set reason to reject and status for match
                match.status = Match.Status.REJECTED
                match.status_reason = status_reason
                match.save()

        return redirect('request-detail', pk=pk)

    except Http404:
        msg = _('The match has already been rejected.')
        messages.error(request, msg)
        return redirect('request-detail', pk=pk)


class ListCreateRequestAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, AccessRequestAPIPermission]
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, updater=self.request.user)


class ListCreateSupplyAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, AccessSupplyAPIPermission]
    queryset = Supply.objects.all()
    serializer_class = SupplySerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, updater=self.request.user)


@login_required
@role_required(roles=[Role.moderator, Role.validator])
def attribute_supply(request, pk, supply_id):
    if supply_id is None or pk is None:
        raise Exception("Parameter supply_id and pk is required")

    # check request and supply are available
    supply_obj, request_obj = check_available(pk, supply_id, request)
    if supply_obj.is_ongoing:
        msg = _('The supply is already on going attribution.')
        messages.error(request, msg)
        return True
    elif supply_obj.is_attributed:
        msg = _('The supply is attributed, attribution is impossible.')
        messages.error(request, msg)
        return True

    # change supply status
    supply_obj.status = Supply.Status.ONGOING_ATTRIBUTION
    supply_obj.save()

    # compute quantity tmp attributed
    quantity = supply_obj.remaining_quantity if request_obj.quantity > supply_obj.remaining_quantity \
        else supply_obj.remaining_quantity - request_obj.quantity

    # create new match
    match = Match.objects.create(request=request_obj,
                                 supply=supply_obj,
                                 status=Match.Status.ATTRIBUTED,
                                 quantity=quantity,
                                 creator_id=request.user.id)
    if match is not None:
        request_obj.matches.add(match)
        supply_obj.matches.add(match)

        services.notify_validators_w_new_match(request_obj)

    return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.validator])
def hold_attribution(request, pk=None, match_id=None):
    if match_id is None or pk is None:
        raise Exception('Parameter match_id and pk is required')

    try:
        match = get_object_or_404(Match, pk=match_id)

        if request.method == 'POST':
            form = ConfirmationForm(request.POST)

            if form.is_valid():
                confirm_message = form.cleaned_data.get('confirm_message')
                match.status = Match.Status.ON_HOLD
                match.status_reason = confirm_message
                match.save()

        return redirect('request-detail', pk=pk)

    except Http404:
        msg = _('No attribution with given id found.')
        messages.error(request, msg)
        return redirect('request-detail', pk=pk)


@login_required
@role_required(roles=[Role.validator, Role.requester])
def complete_attribution(request, pk=None, match_id=None):
    if match_id is None or pk is None:
        raise Exception('Parameter match_id and pk is required')

    try:
        match = get_object_or_404(Match, pk=match_id)

        if not (Role.validate_roles(request.user, [Role.validator]) or match.request.creator == request.user):
            raise PermissionDenied()

        if match.status != Match.Status.VALIDATED:
            msg = _('Only validated attributions can be set as completed.')
            messages.error(request, msg)
        else:
            match.status = Match.Status.COMPLETED
            match.save()
            match.supply.status = Supply.Status.AVAILABLE
            match.supply.save()

            services.notify_supplier_w_completed_match(match)

            msg = _('Attribution has been set as completed.')
            messages.success(request, msg)

        return redirect('request-detail', pk=pk)

    except Http404:
        msg = _('No attribution with given id found.')
        messages.error(request, msg)
        return redirect('request-detail', pk=pk)


@login_required()
@role_required(roles=[Role.validator])
def validate_attribution(request, pk=None, match_id=None):
    if match_id is None or pk is None:
        raise Exception("Parameter match_id and pk is required")

    try:
        match = get_object_or_404(Match, pk=match_id)
        # check request and supply are available
        supply_obj, request_obj = check_available(pk, match.supply.id, request)

        initial_data = {
            'available': supply_obj.remaining_quantity,
            'attributed': 0,
            'remaining': supply_obj.remaining_quantity,
            'requestQuantity': request_obj.remaining_quantity
        }

        if request.method == "POST":
            form = ValidateAttributionForm(request.POST, initial=initial_data)

            if form.is_valid():
                attributed = form.cleaned_data.get("attributed")

                # check match and supply can be validated
                check_match_already_validated(request, match, supply_obj, pk)

                if attributed > request_obj.remaining_quantity:
                    attributed = request_obj.remaining_quantity

                # change match status
                if match is not None:
                    match.status = Match.Status.VALIDATED
                    match.quantity = attributed
                    match.validator_id = request.user.id
                    match.save()

                    services.notify_all_w_validated_match(match)

                # change supply status + change quantiy avaliable
                supply_obj.status = Supply.Status.ATTRIBUTED
                supply_obj.save()

                msg = _('The attribution has been validated and the remaining request quantity has been updated.')
                messages.success(request, msg)

        return redirect('request-detail', pk=pk)

    except Http404:
        msg = _('The match could not be found, he has been withdrawn.')
        messages.error(request, msg)
        return redirect('request-detail', pk=pk)


def check_supply_is_unavailable(supply, request):
    if supply.is_closed:
        msg = _('The supply is closed, attribution is impossible.')
        messages.error(request, msg)
        return True
    elif supply.is_archived:
        msg = _('The supply is archived, attribution is impossible.')
        messages.error(request, msg)
        return True

    return False


def check_request_is_unavailable(request_obj, request):
    if request_obj.is_closed:
        msg = _('The request is closed, attribution is impossible.')
        messages.error(request, msg)
        return True
    elif request_obj.is_archived:
        msg = _('The request is archived, attribution is impossible.')
        messages.error(request, msg)
        return True

    return False


def check_available(request_id, supply_id, request):
    supply_obj = get_object_or_404(Supply, pk=supply_id)
    request_obj = get_object_or_404(Request, pk=request_id)

    if check_request_is_unavailable(request_obj, request):
        return redirect('request-detail', pk=request_id)

    if check_supply_is_unavailable(supply_obj, request):
        return redirect('request-detail', pk=request_id)

    return supply_obj, request_obj


def check_match_already_validated(request, match, supply_obj, request_id):
    if match.is_validated:
        msg = _('The match is already validated.')
        messages.error(request, msg)
        return redirect('request-detail', pk=request_id)

    if supply_obj.is_attributed:
        msg = _('The supply is attributed and cannot be validated.')
        messages.error(request, msg)
        return redirect('request-detail', pk=request_id)


def set_supply_status(supply):
    if supply.remaining_quantity == 0:
        supply.status = Supply.Status.ATTRIBUTED
    else:
        supply.status = Supply.Status.AVAILABLE

    return supply
