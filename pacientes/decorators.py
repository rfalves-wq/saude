# paciente/decorators.py
from django.core.exceptions import PermissionDenied

def grupo_requerido(grupos):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and (
                request.user.is_superuser or
                request.user.groups.filter(name__in=grupos).exists()
            ):
                return view_func(request, *args, **kwargs)

            raise PermissionDenied  # ← ISSO ativa o 403.html

        return _wrapped_view
    return decorator
