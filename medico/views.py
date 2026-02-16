from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Atendimento
from triagem.models import Triagem

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Atendimento
from triagem.models import Triagem

@login_required
def medico_dashboard(request):
    triagens = Triagem.objects.filter(atendido=False).order_by('-data_triagem')
    atendimentos_hoje = Atendimento.objects.filter(
        medico=request.user,
        finalizado=True
    )

    context = {
        'triagens': triagens,
        'total_pendentes': triagens.count(),
        'total_atendidos': atendimentos_hoje.count(),
    }

    return render(request, 'medico/dashboard.html', context)



@login_required
def iniciar_atendimento(request, triagem_id):
    triagem = get_object_or_404(Triagem, id=triagem_id)

    atendimento = Atendimento.objects.create(
        paciente=triagem.paciente,
        medico=request.user,
        triagem=triagem
    )

    triagem.atendido = True
    triagem.save()

    return redirect('editar_atendimento', atendimento.id)



@login_required
def editar_atendimento(request, atendimento_id):
    atendimento = get_object_or_404(Atendimento, id=atendimento_id)

    if request.method == 'POST':
        atendimento.diagnostico = request.POST.get('diagnostico')
        atendimento.prescricao = request.POST.get('prescricao')
        atendimento.observacoes = request.POST.get('observacoes')
        atendimento.finalizado = True
        atendimento.save()
        return redirect('medico_dashboard')

    return render(request, 'medico/atendimento.html', {'atendimento': atendimento})
