from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Agendamento
from .forms import AgendamentoForm

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


@login_required
def lista_agendamentos(request):
    agendamentos = Agendamento.objects.all().order_by('-data')
    return render(request, 'recepcao/lista.html', {'agendamentos': agendamentos})


@login_required
def enviar_para_triagem(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)
    agendamento.status = 'TRIAGEM'
    agendamento.save()
    return redirect('lista_agendamentos')


@login_required
def lista_triagem(request):
    pacientes_triagem = Agendamento.objects.filter(status='TRIAGEM')
    return render(request, 'triagem/lista_triagem.html', {'pacientes': pacientes_triagem})


from django.http import JsonResponse
from pacientes.models import Paciente

def buscar_paciente(request):
    termo = request.GET.get('q', '')
    pacientes = Paciente.objects.filter(nome__icontains=termo)[:10]

    data = [
        {
            "id": p.id,
            "nome": p.nome
        }
        for p in pacientes
    ]

    return JsonResponse(data, safe=False)

def enviar_para_triagem(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)
    agendamento.status = "Em Triagem"
    agendamento.save()
    return redirect('lista_agendamentos')
