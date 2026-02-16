from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Value
from django.utils import timezone

from .models import Atendimento
from triagem.models import Triagem
from django.db import transaction


# ==============================
# DASHBOARD MÉDICO
# ==============================
@login_required
def medico_dashboard(request):

    agora = timezone.now()
    hoje = agora.date()

    # 🔴 TRIAGENS PENDENTES (ordenadas por prioridade)
    triagens = (
        Triagem.objects
        .filter(atendido=False)
        .annotate(
            prioridade=Case(
                When(classificacao_risco="Vermelho", then=Value(1)),
                When(classificacao_risco="Laranja", then=Value(2)),
                When(classificacao_risco="Amarelo", then=Value(3)),
                When(classificacao_risco="Verde", then=Value(4)),
                When(classificacao_risco="Azul", then=Value(5)),
                default=Value(5),
                output_field=IntegerField(),
            )
        )
        .order_by("prioridade", "-data_triagem")
    )

    # ✅ ATENDIMENTOS FINALIZADOS DO MÉDICO LOGADO
    atendimentos_finalizados = (
        Atendimento.objects
        .filter(medico=request.user, finalizado=True)
        .order_by("-id")
    )

    # 📊 TOTAIS
    total_pendentes = triagens.count()
    total_atendidos = atendimentos_finalizados.count()

    total_dia = atendimentos_finalizados.filter(
        data_atendimento__date=hoje
    ).count()

    total_mes = atendimentos_finalizados.filter(
        data_atendimento__year=agora.year,
        data_atendimento__month=agora.month
    ).count()

    context = {
        "triagens": triagens,
        "atendimentos_finalizados": atendimentos_finalizados,
        "total_pendentes": total_pendentes,
        "total_atendidos": total_atendidos,
        "total_dia": total_dia,
        "total_mes": total_mes,
    }

    return render(request, "medico/dashboard.html", context)

# ==============================
# INICIAR ATENDIMENTO (PROTEGIDO)
# ==============================
@login_required
def iniciar_atendimento(request, triagem_id):

    with transaction.atomic():

        # 🔒 trava a triagem no banco
        triagem = (
            Triagem.objects
            .select_for_update()
            .get(id=triagem_id)
        )

        # 🚫 se já foi atendida, não deixa criar outro atendimento
        if triagem.atendido:
            return redirect("medico_dashboard")

        atendimento = Atendimento.objects.create(
            paciente=triagem.paciente,
            medico=request.user,
            triagem=triagem
        )

        triagem.atendido = True
        triagem.save()

    return redirect("editar_atendimento", atendimento.id)



# ==============================
# EDITAR / FINALIZAR ATENDIMENTO
# ==============================
@login_required
def editar_atendimento(request, atendimento_id):

    atendimento = get_object_or_404(Atendimento, id=atendimento_id)

    if request.method == "POST":
        atendimento.diagnostico = request.POST.get("diagnostico")
        atendimento.prescricao = request.POST.get("prescricao")
        atendimento.observacoes = request.POST.get("observacoes")
        atendimento.decisao = request.POST.get("decisao")  # ✅ Salva a decisão do médico
        atendimento.finalizado = True
        atendimento.save()

        return redirect("medico_dashboard")

    return render(request, "medico/atendimento.html", {
        "atendimento": atendimento
    })
