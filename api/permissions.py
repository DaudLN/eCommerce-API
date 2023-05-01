from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        DjangoModelPermissions)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and request.user.is_staff)


class FullDjangoModelPermissions(DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class ViewCustomerHistoryPermissions(DjangoModelPermissions):
    def has_permission(self, request, view):
        return request.user.has_perm('store.view_history')
