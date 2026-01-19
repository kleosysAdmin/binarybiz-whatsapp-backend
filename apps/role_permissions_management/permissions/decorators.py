from functools import wraps
from django.http import JsonResponse
from apps.role_permissions_management.permissions.utils import PermissionChecker

def feature_permission_required(feature_key, action_key=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            try:
                user_role = (
                    request.headers.get('X-User-Role') or
                    request.META.get('HTTP_X_USER_ROLE')
                )
                
                branch_key = (
                    request.headers.get('X-Branch-Key') or
                    request.META.get('HTTP_X_BRANCH_KEY')
                )

                if not all([user_role, branch_key]):
                    return JsonResponse({
                        "status": False,
                        "message": "Missing required headers",
                        "code": "MISSING_HEADERS"
                    }, status=403)

                checker = PermissionChecker(str(user_role), str(branch_key))
                if not checker.has_permission(feature_key, action_key):
                    return JsonResponse({
                        "status": False,
                        "message": "Permission denied",
                        "error": "Permission Denied"
                    }, status=403)

                return view_func(self, request, *args, **kwargs)

            except Exception as e:
                return JsonResponse({
                    "status": False,
                    "message": "Internal server error",
                    "error": str(e),
                    "code": "INTERNAL_ERROR"
                }, status=500)
        return wrapped_view
    return decorator