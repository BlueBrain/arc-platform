import types

CALLABLES = types.FunctionType, types.MethodType
ignore_items = ['validate_roles', 'get_roles_list', 'super_admin']


class Role(object):
    moderator = 'moderator'
    validator = 'validator'
    supplier = 'supplier'
    requester = 'requester'
    super_admin = 'super_admin'

    @staticmethod
    def validate_roles(user, roles):
        return any([getattr(user, f"is_{role}") for role in roles])

    @staticmethod
    def get_roles_list():
        roles = []

        for key, value in Role.__dict__.items():
            if not isinstance(value, CALLABLES):
                if not key.startswith('__') and key not in ignore_items:
                    roles.append(tuple((key, key.capitalize().replace("_", " "))))

        return roles
