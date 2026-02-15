from django.shortcuts import render, get_object_or_404, redirect
from recepcao.models import Agendamento
from .models import Triagem
from .forms import TriagemForm


def triagem_dashboard(request):
    fila = Agendamento.objects.filter(status="Em Triagem")
    return render(request, 'triagem/triagem_dashboard.html', {'fila': fila})


def realizar_triagem(request, id):
    agendamento = get_object_or_404(Agendamento, id=id)

    if request.method == 'POST':
        form = TriagemForm(request.POST)
        if form.is_valid():
            triagem = form.save(commit=False)
            triagem.agendamento = agendamento
            triagem.paciente = agendamento.paciente
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


def historico_triagens(request):
    triagens = Triagem.objects.all().order_by('-data_triagem')
    return render(request, 'triagem/historico_triagens.html', {
        'triagens': triagens
    })
