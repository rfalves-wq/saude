from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
import random

from .models import Usuario
from .forms import UsuarioForm, LoginForm
from pacientes.models import Paciente

# =========================
# 2FA TEMPORÁRIO (teste)
# =========================
tfa_codes = {}

# =========================
# LOGIN COM 2FA
# =========================
def login_view(request):
    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST':
        token = request.POST.get('token')

        # ===== SEGUNDA ETAPA (2FA) =====
        if token:
            username = request.session.get('username_temp')
            password = request.session.get('password_temp')

            if username and tfa_codes.get(username) == token:
                user = authenticate(request, username=username, password=password)
                if user:
                    login(request, user)
                    tfa_codes.pop(username, None)
                    request.session.pop('username_temp', None)
                    request.session.pop('password_temp', None)

                    # Redirecionamento por perfil
                    if user.perfil == 'administrador':
                        return redirect('admin_dashboard')
                    elif user.perfil == 'medico':
                        return redirect('medico_dashboard')
                    elif user.perfil == 'enfermeiro':
                        return redirect('enfermeiro_dashboard')
                    elif user.perfil == 'tecnico':
                        return redirect('tecnico_dashboard')
                    elif user.perfil == 'recepcao':
                        return redirect('recepcao_dashboard')
                else:
                    error = "Usuário ou senha inválidos."
            else:
                error = "Código 2FA inválido."

        # ===== PRIMEIRA ETAPA =====
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

# =========================
# VERIFICA PERFIS
# =========================
def apenas_recepcao(user):
    return user.is_authenticated and user.perfil == 'recepcao'

def apenas_admin(user):
    return user.is_authenticated and user.perfil == 'administrador'

# =========================
# DASHBOARDS
# =========================
@login_required
@user_passes_test(apenas_admin)
def admin_dashboard(request):
    return render(request, 'usuarios/admin_dashboard.html')

@login_required
def medico_dashboard(request):
    return render(request, 'usuarios/medico_dashboard.html')

@login_required
def enfermeiro_dashboard(request):
    return render(request, 'usuarios/enfermeiro_dashboard.html')

@login_required
def tecnico_dashboard(request):
    return render(request, 'usuarios/tecnico_dashboard.html')

# =========================
# DASHBOARD RECEPÇÃO
# =========================
@login_required
@user_passes_test(apenas_recepcao)
def recepcao_dashboard(request):
    total_pacientes = Paciente.objects.count()
    total_masculino = Paciente.objects.filter(sexo_biologico='M').count()
    total_feminino = Paciente.objects.filter(sexo_biologico='F').count()
    total_intersexo = Paciente.objects.filter(sexo_biologico='I').count()

    hoje = timezone.now().date()
    pacientes_hoje = Paciente.objects.filter(data_criacao__date=hoje).count()

    if total_pacientes > 0:
        porcent_m = round((total_masculino / total_pacientes) * 100, 1)
        porcent_f = round((total_feminino / total_pacientes) * 100, 1)
        porcent_i = round((total_intersexo / total_pacientes) * 100, 1)
    else:
        porcent_m = porcent_f = porcent_i = 0

    context = {
        'total_pacientes': total_pacientes,
        'pacientes_hoje': pacientes_hoje,
        'total_masculino': total_masculino,
        'total_feminino': total_feminino,
        'total_intersexo': total_intersexo,
        'porcent_m': porcent_m,
        'porcent_f': porcent_f,
        'porcent_i': porcent_i,
    }
    return render(request, 'usuarios/recepcao_dashboard.html', context)

# =========================
# CRUD USUÁRIOS
# =========================
#@login_required
#@user_passes_test(apenas_admin)
from django.db.models import Q, Value
from django.db.models.functions import Concat

def usuario_list(request):
    busca = request.GET.get('busca', '').strip()
    perfil_filtro = request.GET.get('perfil', 'todos')

    usuarios = Usuario.objects.all()

    # Filtra por perfil
    if perfil_filtro != 'todos':
        usuarios = usuarios.filter(perfil=perfil_filtro)

    # Busca por username, email, cpf ou nome completo
    if busca:
        usuarios = usuarios.annotate(
            nome_completo=Concat('first_name', Value(' '), 'last_name')
        ).filter(
            Q(username__icontains=busca) |
            Q(email__icontains=busca) |
            Q(cpf__icontains=busca) |
            Q(nome_completo__icontains=busca)
        )

    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'usuarios/usuario_list.html', {
        'page_obj': page_obj,
        'busca': busca,
        'perfil_filtro': perfil_filtro
    })


#@login_required
#@user_passes_test(apenas_admin)
def usuario_create(request):
    form = UsuarioForm(request.POST or None)
    if form.is_valid():
        usuario = form.save(commit=False)
        if form.cleaned_data.get('password'):
            usuario.set_password(form.cleaned_data['password'])
        usuario.save()
        return redirect('usuario_list')
    return render(request, 'usuarios/usuario_form.html', {'form': form})

#@login_required
#@user_passes_test(apenas_admin)
def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form = UsuarioForm(request.POST or None, instance=usuario)
    if form.is_valid():
        usuario = form.save(commit=False)
        if form.cleaned_data.get('password'):
            usuario.set_password(form.cleaned_data['password'])
        usuario.save()
        return redirect('usuario_list')
    return render(request, 'usuarios/usuario_form.html', {'form': form})

#@login_required
#@user_passes_test(apenas_admin)
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuario_list')
    return render(request, 'usuarios/usuario_confirm_delete.html', {'usuario': usuario})
