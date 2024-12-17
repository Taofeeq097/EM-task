from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def role_position_required(allowed_roles=None, allowed_positions=None):
    """
    Decorator to check if the user has the required role or position.
    :param allowed_roles: List of roles that are allowed to access the view
    :param allowed_positions: List of positions that are allowed to access the view
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            user = request.user
            if user.is_authenticated:
                if (allowed_roles and user.role and user.role.name not in allowed_roles) and \
                   (allowed_positions and user.position not in allowed_positions):
                    return Response(
                        {"detail": "You do not have permission to perform this action."},
                        status=status.HTTP_403_FORBIDDEN
                    )
                return view_func(self, request, *args, **kwargs)

            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        return _wrapped_view

    return decorator
