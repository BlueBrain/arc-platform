from sys import stderr

from arcv2_platform.users.models import User

MODERATOR_ROLE = 'moderator'
VALIDATOR_ROLE = 'validator'
SUPER_ADMIN_ROLE = 'super_admin'

ALL_ROLES = [MODERATOR_ROLE, VALIDATOR_ROLE, SUPER_ADMIN_ROLE]


def run(*args):
    if len(args) < 2:
        _print_usage()

    username = args[0]
    roles = args[1:]

    if any([r not in ALL_ROLES for r in roles]):
        _print_usage()

    try:
        user = User.objects.get(username=username)

        if MODERATOR_ROLE in roles:
            user.is_moderator = True

        if VALIDATOR_ROLE in roles:
            user.is_validator = True

        if SUPER_ADMIN_ROLE in roles:
            user.is_super_admin = True

        user.save()

        plural = ''
        if len(roles) > 1:
            plural = 's'
        print(f'Granted role{plural} {",".join(roles)} to {username}')

    except User.DoesNotExist:
        print(f'User with username {username} does not exist', file=stderr)
        exit(1)


def _print_usage():
    print(f'Usage: grant_role <username> <role ({MODERATOR_ROLE}|{VALIDATOR_ROLE}|{SUPER_ADMIN_ROLE})>*',
          file=stderr)
    exit(1)
