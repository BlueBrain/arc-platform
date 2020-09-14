from django.utils.translation import gettext as _
from import_export import resources
from import_export.fields import Field
from arcv2_platform.users.models import User


class UserResource(resources.ModelResource):
    id = Field(column_name=_("ID"), attribute="id")
    email = Field(column_name=_("Email"))
    firstname = Field(column_name=_("First name"))
    lastname = Field(column_name=_("Last name"))
    affiliation = Field(column_name=_("Affiliation"))
    role_display = Field(column_name=_("Roles"), attribute="role_display")

    class Meta:
        model = User
        fields = []

    def dehydrate_role_display(self, request):
        return request.role_display

    def dehydrate_email(self, request):
        return request.email.encode("utf8", "ignore").decode()

    def dehydrate_firstname(self, request):
        if request.firstname is not None:
            return request.firstname.encode("utf8", "ignore").decode()

    def dehydrate_lastname(self, request):
        if request.lastname is not None:
            return request.lastname.encode("utf8", "ignore").decode()

    def dehydrate_affiliation(self, request):
        if request.affiliation is not None:
            return request.affiliation.encode("utf8", "ignore").decode()
