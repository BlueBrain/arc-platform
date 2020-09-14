from django.utils.translation import gettext as _
from import_export import resources
from import_export.fields import Field

from arcv2_platform.matchmaking.models import Request, Supply


class RequestResource(resources.ModelResource):
    resource__name = Field(column_name=_("Type"), attribute="resource__name")
    request = Field(column_name=_("Request"))
    requester_name = Field(column_name=_("Name"))
    affiliation = Field(column_name=_("Affiliation"))
    role = Field(column_name=_("Role"), attribute="role")
    email = Field(column_name=_("Email address"))
    comment = Field(column_name=_("Brief comment"))
    quantity = Field(column_name=_("Quantity"))
    priority = Field(column_name=_("Priority"), attribute="priority")
    status = Field(column_name=_("Status"))
    phone = Field(column_name=_("Phone"))
    creation_time = Field(column_name=_("Creation"), attribute="creation_time")
    to_attrib = Field(column_name=_("To attrib."))
    to_valid = Field(column_name=_("To valid."))

    class Meta:
        model = Request
        fields = []

    def dehydrate_request(self, request):
        return request.full_category_item

    def dehydrate_quantity(self, request):
        return request.quantity_progress

    def dehydrate_status(self, request):
        return request.get_status_display()

    def dehydrate_creation_time(self, request):
        return request.creation_time.strftime("%m/%d/%y %H:%M")

    def dehydrate_to_attrib(self, request):
        return request.quantity_to_attribute

    def dehydrate_to_valid(self, request):
        return request.quantity_to_validate

    def dehydrate_phone(self, request):
        if request.phone.startswith('+'):
            # add space before to show +
            return f' {request.phone}'
        else:
            return request.phone

    def dehydrate_affiliation(self, request):
        return request.affiliation.encode("utf8", "ignore").decode()

    def dehydrate_author_comment(self, request):
        if request.author_comment is not None:
            return request.author_comment.encode("utf8", "ignore").decode()

    def dehydrate_email(self, request):
        return request.email.encode("utf8", "ignore").decode()

    def dehydrate_requester_name(self, request):
        return request.fullname.encode("utf8", "ignore").decode()


class SupplyResource(resources.ModelResource):
    resource__name = Field(column_name=_("Type"), attribute="resource__name")
    supply = Field(column_name=_("Supply"))
    quantity = Field(column_name=_("Quantity"), attribute="quantity")
    name = Field(column_name=_("Name"), attribute="fullname")
    affiliation = Field(column_name=_("Affiliation"))
    role = Field(column_name=_("Role"), attribute="role")
    email = Field(column_name=_("Email address"))
    comment = Field(column_name=_("Brief comment"), attribute="author_comment")
    status = Field(column_name=_("Status"))
    phone = Field(column_name=_("Phone"))
    creation_time = Field(column_name=_("Creation"))

    class Meta:
        model = Supply
        fields = []

    def dehydrate_supply(self, supply):
        return supply.full_category_item

    def dehydrate_status(self, supply):
        return supply.get_status_display()

    def dehydrate_creation_time(self, supply):
        return supply.creation_time.strftime("%m/%d/%y %H:%M")

    def dehydrate_phone(self, supply):
        if supply.phone.startswith('+'):
            # add space before to show +
            return f' {supply.phone}'
        else:
            return supply.phone

    def dehydrate_affiliation(self, supply):
        return supply.affiliation.encode("utf8", "ignore").decode()

    def dehydrate_comment(self, supply):
        if supply.author_comment is not None:
            return supply.author_comment.encode("utf8", "ignore").decode()

    def dehydrate_email(self, supply):
        return supply.email.encode("utf8", "ignore").decode()

    def dehydrate_name(self, supply):
        return supply.fullname.encode("utf8", "ignore").decode()
