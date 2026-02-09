from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from .models import Usuario
from .forms import UsuarioForm, LoginForm
import random

# ===== 2FA =====
tfa_codes = {}

def login_view(request):
    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST':
        token = request.POST.get('token')

        if token:
            username = request.session.get('username_temp')
            password = request.session.get('password_temp')
            if username and tfa_codes.get(username) == token:
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    tfa_codes.pop(username, None)
                    request.session.pop('username_temp')
                    request.session.pop('password_temp')
                    # redireciona por perfil
                    if user.perfil == 'administrador': return redirect('admin_dashboard')
                    elif user.perfil == 'medico': return redirect('medico_dashboard')
                    elif user.perfil == 'enfermeiro': return redirect('enfermeiro_dashboard')
                    elif user.perfil == 'tecnico': return redirect('tecnico_dashboard')
                    elif user.perfil == 'recepcao': return redirect('recepcao_dashboard')
                else:
                    error = "Usuário ou senha inválidos."
            else:
                error = "Código 2FA inválido."
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                code = str(random.randint(100000, 999999))
                tfa_codes[username] = code
                request.session['username_temp'] = username
                request.session['password_temp'] = password
                return render(request, 'usuarios/login_2fa.html', {'code': code})
            else:
                error = "Usuário ou senha inválidos."

    return render(request, 'usuarios/login.html', {'form': form, 'error': error})

# ===== DASHBOARDS =====
def admin_dashboard(request): return render(request, 'usuarios/admin_dashboard.html')
def medico_dashboard(request): return render(request, 'usuarios/medico_dashboard.html')
def enfermeiro_dashboard(request): return render(request, 'usuarios/enfermeiro_dashboard.html')
def tecnico_dashboard(request): return render(request, 'usuarios/tecnico_dashboard.html')
def recepcao_dashboard(request): return render(request, 'usuarios/recepcao_dashboard.html')

# ===== CRUD de Usuários =====
def usuario_list(request):
    busca = request.GET.get('busca', '')
    perfil_filtro = request.GET.get('perfil', 'todos')
    usuarios = Usuario.objects.all()

    if perfil_filtro != 'todos':
        usuarios = usuarios.filter(perfil=perfil_filtro)
    if busca:
        usuarios = usuarios.filter(username__icontains=busca) | usuarios.filter(email__icontains=busca)

    paginator = Paginator(usuarios, 5)  # 5 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'usuarios/usuario_list.html', {'page_obj': page_obj, 'busca': busca, 'perfil_filtro': perfil_filtro})

def usuario_create(request):
    form = UsuarioForm(request.POST or None)
    if form.is_valid():
        u = form.save(commit=False)
        if form.cleaned_data['password']:
            u.set_password(form.cleaned_data['password'])
        u.save()
        return redirect('usuario_list')
    return render(request, 'usuarios/usuario_form.html', {'form': form})

def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(request.POST or None, instance=usuario)
    if form.is_valid():
        u = form.save(commit=False)
        if form.cleaned_data['password']:
            u.set_password(form.cleaned_data['password'])
        u.save()
        return redirect('usuario_list')
    return render(request, 'usuarios/usuario_form.html', {'form': form})

def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuario_list')
    return render(request, 'usuarios/usuario_confirm_delete.html', {'usuario': usuario})
