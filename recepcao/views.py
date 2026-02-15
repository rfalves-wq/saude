from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Agendamento
from .forms import AgendamentoForm
from pacientes.models import Paciente
from django.http import JsonResponse

@login_required
def agendar_paciente(request):
    if request.method == 'POST':
        form = AgendamentoForm(request.POST)
        if form.is_valid():
            agendamento = form.save(commit=False)
            agendamento.criado_por = request.user
            agendamento.save()
            return redirect('lista_agendamentos')
    else:
        form = AgendamentoForm()
    return render(request, 'recepcao/agendar.html', {'form': form})
from django.utils import timezone

@login_required
def lista_agendamentos(request):
    # pega todos os agendamentos
    agendamentos = Agendamento.objects.all().order_by('-data', 'hora')

    # filtrar por data
    data_filtro = request.GET.get('data')
    if data_filtro:
        agendamentos = agendamentos.filter(data=data_filtro)
        atendimentos_dia = agendamentos.count()
    else:
        # se não selecionar data, mostrar agendamentos do dia atual
        hoje = timezone.now().date()
        agendamentos_hoje = agendamentos.filter(data=hoje)
        atendimentos_dia = agendamentos_hoje.count()

    context = {
        'agendamentos': agendamentos,
        'request': request,
        'atendimentos_dia': atendimentos_dia,
        'data_filtro': data_filtro or timezone.now().date()
    }
    return render(request, 'recepcao/lista.html', context)


@login_required
def enviar_para_triagem(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)
    agendamento.status = "Em Triagem"
    agendamento.save()
    return redirect('lista_agendamentos')


@login_required
def lista_triagem(request):
    pacientes_triagem = Agendamento.objects.filter(status='Em Triagem')
    return render(request, 'triagem/lista_triagem.html', {'pacientes': pacientes_triagem})

def buscar_paciente(request):
    termo = request.GET.get('q', '')
    pacientes = Paciente.objects.filter(nome__icontains=termo)[:10]
    data = [
        {"id": p.id, "nome": p.nome}
        for p in pacientes
    ]
    return JsonResponse(data, safe=False)
