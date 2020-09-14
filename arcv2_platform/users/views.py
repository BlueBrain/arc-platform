import datetime

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView, UpdateView
from django.utils.translation import gettext as _
from rest_framework.authtoken.models import Token

from arcv2_platform import settings
from arcv2_platform.app.decorators import role_required
from arcv2_platform.app.mixins import RoleRequiredMixin, ResourceDownloadMixin
from arcv2_platform.app.models import Role
from arcv2_platform.users.forms import LoginForm, ModelUserUpdateForm, ModelUserCreateForm, ModelUserForm
from arcv2_platform.users.models import User
from rest_framework.exceptions import ParseError

from arcv2_platform.users.resources import UserResource


def login_user(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            if 'username' not in form.data or 'password' not in form.data:
                raise ParseError

            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')

            try:
                user = User.objects.get(username__iexact=username)

                if not (user.check_password(raw_password)):
                    messages.error(request, 'Invalid credentials')
                    return render(request, 'users/registration/login.html', {'form': form})

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            except User.DoesNotExist:
                messages.error(request, _('Invalid credentials'))
                return render(request, 'users/registration/login.html', {'form': form})

            return HttpResponseRedirect('/')
    else:
        form = LoginForm()

    # if a GET (or any other method) we'll create a blank form
    return render(request, 'users/registration/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


def sso_login(request):
    email = request.headers.get(settings.SSO_HEADERS['email'], None)
    firstname = request.headers.get(settings.SSO_HEADERS['firstname'], None)
    lastname = request.headers.get(settings.SSO_HEADERS['lastname'], None)
    affiliation = request.headers.get(settings.SSO_HEADERS['affiliation'], None)
    phone = request.headers.get(settings.SSO_HEADERS['phone'], None)

    if email is None:
        raise PermissionDenied()

    try:
        user = User.objects.get(username=email)

        # Update user properties with SSO data
        if firstname is not None:
            user.firstname = firstname

        if lastname is not None:
            user.lastname = lastname

        user.affiliation = affiliation
        user.phone = phone
        user.is_switch_user = True

        user.save()
    except User.DoesNotExist:
        # We need at least firstname and lastname to create a user
        if firstname is None or lastname is None:
            raise PermissionDenied()

        user = User.objects.create_user(email, firstname, lastname, affiliation=affiliation, phone=phone,
                                        is_active=True, is_switch_user=True)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    return redirect('dashboard')


class UserListView(RoleRequiredMixin, ResourceDownloadMixin, ListView):
    model = User
    resource_filename = _("users")
    resource_class = UserResource
    paginate_by = 25
    ordering = ['created']
    roles = [Role.super_admin, Role.validator]

    def get_queryset(self):
        # step 1
        filters = {}

        role = self.request.GET.get('role', None)

        if role != '' and role is not None:
            if role == Role.moderator:
                filters["is_moderator"] = True
            elif role == Role.validator:
                filters["is_validator"] = True
            elif role == Role.requester:
                filters["is_requester"] = True
            elif role == Role.supplier:
                filters["is_moderator"] = False
                filters["is_validator"] = False
                filters["is_requester"] = False

        new_context = User.objects.filter(**filters)

        return new_context

    def get_context_data(self, **kwargs):
        # step 2
        context = super(UserListView, self).get_context_data(**kwargs)
        role = self.request.GET.get('role')

        context["filters"] = {
            "role": {
                "title": _("Roles"),
                "name": "role",
                "value": role,
                "options": Role.get_roles_list()
            },
        }
        return context


class UserCreate(RoleRequiredMixin, CreateView):
    model = User
    form_class = ModelUserCreateForm
    roles = [Role.super_admin, Role.validator]
    context_object_name = 'user_object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("New User")
        context['roles'] = Role.get_roles_list()
        context['roleselected'] = Role.supplier
        return context

    def form_valid(self, form):
        email = form.cleaned_data.get('email')

        user = form.save(commit=False)
        set_log_history(True, user, self.request)

        role = form.cleaned_data.get('role')
        set_role_user(role, user)

        user.password = make_password(form.cleaned_data['password'])
        user.username = email
        user.save()

        url = reverse("users-edit", kwargs={'pk': user.id})

        # flash message
        msg = _('The %(link)s user %(email)s has been added.') % {'link': f'<a href="{url}" class="old">',
                                                                  'email': f'{user.email} </a>'}

        messages.success(self.request, msg)

        return HttpResponseRedirect('/users/%d' % user.id)

    def get_success_url(self):
        return reverse('users-info', kwargs={'pk': self.object.pk})


class UserUpdate(RoleRequiredMixin, UpdateView):
    model = User
    form_class = ModelUserUpdateForm
    template_name_suffix = '_update_form'
    roles = [Role.super_admin, Role.validator]
    context_object_name = 'user_object'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Update User")
        context['roles'] = Role.get_roles_list()
        context['roleselected'] = get_role_selected(context.get('object'))
        return context

    def form_valid(self, form):
        userDB = form.save(commit=False)

        # TODO remove this when switch aai is up
        email = form.cleaned_data.get('email')
        userDB.username = email
        # encrypt plain new password
        new_password = form.cleaned_data.get('new_password')
        if new_password:
            userDB.set_password(new_password)

        # get role
        role = form.cleaned_data.get('role')
        set_role_user(role, userDB)

        set_log_history(False, userDB, self.request)

        userDB.update_time = datetime.datetime.today()
        userDB.update_by = f'{self.request.user.firstname} {self.request.user.lastname}'

        userDB.save()

        url = reverse("users-edit", kwargs={'pk': userDB.id})

        # flash message
        msg = _('The %(link)s user %(email)s has been saved.') % {'link': f'<a href="{url}" class="old">',
                                                                  'email': f'{userDB.email} </a>'}

        messages.success(self.request, msg)

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('users-info', kwargs={'pk': self.object.pk})


def get_role_selected(user):
    if user.is_moderator:
        return Role.moderator
    elif user.is_validator:
        return Role.validator
    elif user.is_requester:
        return Role.requester
    else:
        return Role.supplier


def get_role_name(user):
    if user.is_moderator:
        return Role.moderator.capitalize()
    elif user.is_validator:
        return Role.validator.capitalize()
    elif user.is_requester:
        return Role.requester.capitalize()
    else:
        return Role.supplier.capitalize()


def set_role_user(role, user):
    if role == Role.moderator:
        user.is_moderator = True
        user.is_validator = False
        user.is_requester = False
    elif role == Role.validator:
        user.is_validator = True
        user.is_moderator = False
        user.is_requester = False
    elif role == Role.supplier:
        user.is_validator = False
        user.is_moderator = False
        user.is_requester = False
    elif role == Role.requester:
        user.is_requester = True
        user.is_moderator = False
        user.is_validator = False
    elif role == Role.super_admin:
        user.is_super_admin = True


def set_log_history(is_new, user, request):
    if is_new:
        # history informations
        user.created_by = request.user.firstname + " " + request.user.lastname
    else:
        # history informations
        user.update_by = request.user.firstname + " " + request.user.lastname
        user.update_time = datetime.datetime.now()


@login_required
@role_required(roles=[Role.super_admin, Role.validator])
def user_info(request, pk=None):
    user_data = get_object_or_404(User, pk=pk)
    token, created = Token.objects.get_or_create(user=user_data)

    return render(request, 'users/user_info.html',
                  {
                      "title": _("User"),
                      "accordion_title": f'{user_data.firstname} {user_data.lastname}',
                      "role": _(get_role_name(user_data)),
                      "user_data": user_data,
                      "token": token
                  })


@login_required
def user_profile(request):
    user_data = get_object_or_404(User, pk=request.user.id)
    initial_data = {'role': get_role_name(user_data).lower()}

    if request.method == 'POST':
        form = ModelUserForm(request.POST, instance=user_data, initial=initial_data)

        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('dashboard')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = ModelUserForm(
            instance=user_data,
            initial=initial_data
        )

    return render(request, 'users/user_update_form.html', {
        "title": _("My profile"),
        'form': form,
        "user_profile": True,
        "roles": Role.get_roles_list(),
        "roleselected": _(get_role_name(user_data)),
    })


@login_required
def terms_of_service(request):
    if request.method == 'POST':
        if request.POST.get('tos_accepted', False) == 'on':
            user = request.user
            user.has_accepted_tos = True
            user.save()

            return redirect('dashboard')

    return render(request, 'users/registration/terms_of_service.html')


@login_required
def change_password(request):
    if request.user.is_switch_user:
        raise PermissionDenied()

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Your password was successfully updated!'))
            return redirect('dashboard')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {
        'form': form
    })


def unsubscribe_notification(request, user_token=None):
    token = get_object_or_404(Token, key=user_token)
    user_data = token.user
    user_data.notification_enabled = False
    user_data.save()

    return render(request, 'users/user_unsubscribe.html')
