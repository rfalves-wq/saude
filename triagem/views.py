from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from recepcao.models import Agendamento
from .models import Triagem
from .forms import TriagemForm
from django.http import JsonResponse


@login_required
def triagem_dashboard(request):
    fila = Agendamento.objects.filter(status="Em Triagem")
    return render(request, 'triagem/triagem_dashboard.html', {'fila': fila})

@login_required
def realizar_triagem(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)

    if request.method == 'POST':
        form = TriagemForm(request.POST)
        if form.is_valid():
            triagem = form.save(commit=False)

            triagem.agendamento = agendamento
            triagem.paciente = agendamento.paciente

            # ✅ SALVA O ENFERMEIRO LOGADO
            triagem.enfermeiro = request.user

            triagem.save()

            agendamento.status = "Aguardando Médico"
            agendamento.save()

            return redirect('triagem_dashboard')
    else:
        form = TriagemForm()

    return render(request, 'triagem/realizar_triagem.html', {
        'form': form,
        'agendamento': agendamento
    })


@login_required
def historico_triagens(request):
    triagens = Triagem.objects.all().order_by('-data_triagem')
    return render(request, 'triagem/historico_triagens.html', {
        'triagens': triagens
    })


def fila_triagem_json(request):
    fila = Agendamento.objects.filter(status="Em Triagem")

    dados = []
    for ag in fila:
        dados.append({
            "id": ag.id,
            "paciente": ag.paciente.nome,
            "data": ag.data.strftime("%d/%m/%Y"),
            "hora": ag.hora.strftime("%H:%M"),
            'classificacao': ag.triagem.classificacao_risco if hasattr(ag, 'triagem') else None
        })

    return JsonResponse({"fila": dados})
