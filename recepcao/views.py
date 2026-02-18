from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from .models import Agendamento
from .forms import AgendamentoForm
from pacientes.models import Paciente

# =============================
# AGENDAMENTO DE PACIENTE
# =============================
@login_required
def agendar_paciente(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.criado_por = request.user
            agendamento.save()
            # Redireciona para lista para evitar POST duplicado
            return redirect('lista_agendamentos')
        else:
            # Formulário inválido: envia erros para o template
            return render(request, 'recepcao/agendar.html', {'form': form, 'errors': form.errors})
    else:
        form = AgendamentoForm()
    return render(request, 'recepcao/agendar.html', {'form': form})


# =============================
# LISTA DE AGENDAMENTOS
# =============================
@login_required
def lista_agendamentos(request):
    agendamentos = Agendamento.objects.all().order_by('-data', 'hora')

    # Filtrar por data se houver
    data_filtro = request.GET.get('data')
    if data_filtro:
        agendamentos = agendamentos.filter(data=data_filtro)
        atendimentos_dia = agendamentos.count()
    else:
        hoje = timezone.localdate()
        agendamentos_hoje = agendamentos.filter(data=hoje)
        atendimentos_dia = agendamentos_hoje.count()

    today = timezone.localdate()  # para destacar linha do dia atual no template

    context = {
        'agendamentos': agendamentos,
        'atendimentos_dia': atendimentos_dia,
        'data_filtro': data_filtro or today,
        'today': today,
    }
    return render(request, 'recepcao/lista.html', context)


# =============================
# ENVIAR PACIENTE PARA TRIAGEM
# =============================
@login_required
def enviar_para_triagem(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)
    agendamento.status = "Em Triagem"
    agendamento.save()
    return redirect('lista_agendamentos')


# =============================
# LISTA DE PACIENTES EM TRIAGEM
# =============================
@login_required
def lista_triagem(request):
    pacientes_triagem = Agendamento.objects.filter(status='Em Triagem')
    return render(request, 'triagem/lista_triagem.html', {'pacientes': pacientes_triagem})


from django.http import JsonResponse
from django.db.models import Q
from .models import Paciente
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Q
from .models import Paciente
from datetime import datetime

def buscar_paciente(request):
    termo = request.GET.get('q', '').strip()
    pacientes = Paciente.objects.none()

    if termo:
        filtros = Q(nome__icontains=termo) | Q(cpf__icontains=termo)

        # tenta interpretar como data parcial (dd/mm ou dd/mm/yyyy)
        data_nasc = None
        try:
            if "/" in termo:
                partes = termo.split("/")
                if len(partes) == 2:  # dd/mm
                    dia, mes = map(int, partes)
                    filtros |= Q(data_nascimento__day=dia, data_nascimento__month=mes)
                elif len(partes) == 3:  # dd/mm/yyyy
                    data_nasc = datetime.strptime(termo, "%d/%m/%Y").date()
                    filtros |= Q(data_nascimento=data_nasc)
            elif "-" in termo:  # yyyy-mm-dd
                data_nasc = datetime.strptime(termo, "%Y-%m-%d").date()
                filtros |= Q(data_nascimento=data_nasc)
        except ValueError:
            pass  # termo não é data, ignora

        pacientes = Paciente.objects.filter(filtros)[:10]

    data = [
        {
            "id": p.id,
            "nome": p.nome,
            "cpf": p.cpf,
            "data_nascimento": p.data_nascimento.strftime("%d/%m/%Y") if p.data_nascimento else ""
        }
        for p in pacientes
    ]
    return JsonResponse(data, safe=False)
