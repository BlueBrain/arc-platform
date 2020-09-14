from arcv2_platform.matchmaking.models import Request, Supply, Match
from arcv2_platform.resources.models import Resource, ResourceType, Category, CategoryItem
from arcv2_platform.users.models import User
from scripts.utils import check_for_prod


def run():
    print('Dropping all data...')

    drop_all()

    print('Done')


def drop_all():
    check_for_prod()

    Match.objects.all().delete()
    Request.objects.all().delete()
    Supply.objects.all().delete()
    User.objects.all().delete()
    Resource.objects.all().delete()
    ResourceType.objects.all().delete()
    Category.objects.all().delete()
    CategoryItem.objects.all().delete()
