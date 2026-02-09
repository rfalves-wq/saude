from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Paciente
from .forms import PacienteForm
from django.core.paginator import Paginator
from django.db.models import Q

# 🔒 Verifica se é recepção
def apenas_recepcao(user):
    return user.is_authenticated and user.perfil == 'recepcao'


@login_required
@user_passes_test(apenas_recepcao)

def paciente_list(request):
    pacientes = Paciente.objects.all().order_by('nome')

    # ================= FILTROS =================
    nome = request.GET.get('nome')
    cpf = request.GET.get('cpf')

    if nome:
        pacientes = pacientes.filter(nome__icontains=nome)

    if cpf:
        pacientes = pacientes.filter(cpf__icontains=cpf)

    # ================= PAGINAÇÃO =================
    paginator = Paginator(pacientes, 5)  # 5 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'nome': nome,
        'cpf': cpf,
    }

    return render(request, 'pacientes/paciente_list.html', context)



@login_required
@user_passes_test(apenas_recepcao)
def paciente_create(request):
    form = PacienteForm(request.POST or None)

    if form.is_valid():
        paciente = form.save(commit=False)
        paciente.criado_por = request.user
        paciente.save()
        return redirect('paciente_list')

    return render(request, 'pacientes/paciente_form.html', {'form': form})


@login_required
@user_passes_test(apenas_recepcao)
def paciente_update(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente)

    if form.is_valid():
        form.save()
        return redirect('paciente_list')

    return render(request, 'pacientes/paciente_form.html', {'form': form})


@login_required
@user_passes_test(apenas_recepcao)
def paciente_delete(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        paciente.delete()
        return redirect('paciente_list')

    return render(request, 'pacientes/paciente_confirm_delete.html', {'paciente': paciente})
