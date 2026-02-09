from django.shortcuts import redirect
from django.contrib import messages

def recepcao_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.perfil != 'recepcao':
            messages.error(request, "Você não tem permissão para acessar essa página.")
            return redirect('login')  # ou dashboard geral

        return view_func(request, *args, **kwargs)

    return wrapper
