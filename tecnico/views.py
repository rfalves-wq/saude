from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from medico.models import Atendimento
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from medico.models import Atendimento

@login_required
def lista_medicacao(request):
    atendimentos = Atendimento.objects.filter(
        decisao="medicacao",
        medicacao_aplicada=False,
        finalizado=False
    )

    return render(request, "tecnico/lista_medicacao.html", {
        "atendimentos": atendimentos
    })


from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from medico.models import Atendimento
@login_required
def administrar_medicacao(request, atendimento_id):
    atendimento = get_object_or_404(Atendimento, id=atendimento_id)

    if request.method == "POST":
        # Captura os novos campos do formulário
        observacao = request.POST.get("observacao", "")
        crm = request.POST.get("crm", "")

        # Atualiza o atendimento
        atendimento.medicacao_aplicada = True
        atendimento.tecnico_aplicou = request.user
        atendimento.horario_medicacao = timezone.now()
        atendimento.observacao = observacao  # precisa existir no modelo
        atendimento.crm = crm                # precisa existir no modelo
        atendimento.save()

        # Redireciona para a lista do técnico
        return redirect('lista_medicacao')  

    return render(request, 'tecnico/administrar_medicacao.html', {
        'atendimento': atendimento
    })


from medico.models import Atendimento

@login_required
def tecnico_dashboard(request):

    medicacoes_pendentes = Atendimento.objects.filter(
        decisao="medicacao",
        medicacao_aplicada=False,
        finalizado=False
    )

    return render(request, "tecnico/dashboard.html", {
        "medicacoes_pendentes": medicacoes_pendentes
    })
