from django import forms

from arcv2_platform.users.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Username here'
            }
        )
    )
    password = forms.CharField(
        max_length=50,
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Password'
            }
        )
    )


class ModelUserForm(forms.ModelForm):

    class Meta:
        model = User

        fields = [
            'email',
            'firstname',
            'lastname',
            'affiliation',
            'phone',
            'is_super_admin',
            'notification_enabled'
        ]

        widgets = {
            'username': forms.HiddenInput(),
        }

    role = forms.CharField(
        max_length=50,
        widget=forms.TextInput(),
        required=False
    )


class ModelUserCreateForm(ModelUserForm):
    class Meta(ModelUserForm.Meta):
        model = User
        fields = ModelUserForm.Meta.fields

    password = forms.CharField(widget=forms.widgets.PasswordInput)


class ModelUserUpdateForm(ModelUserForm):
    class Meta(ModelUserForm.Meta):
        model = User
        fields = ModelUserForm.Meta.fields

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.user.is_super_admin:
            self.fields.pop('is_super_admin')

    new_password = forms.CharField(required=False, widget=forms.widgets.PasswordInput)
