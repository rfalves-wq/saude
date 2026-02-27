from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, IntegerField, Value
from django.utils import timezone
from django.db import transaction

from .models import Atendimento
from triagem.models import Triagem

from .models import Atendimento, Exame
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

    # ✅ ATENDIMENTOS FINALIZADOS HOJE
    atendimentos_finalizados = Atendimento.objects.filter(
        medico=request.user,
        finalizado=True,
        data_atendimento__date=hoje
    ).order_by("-data_atendimento")

    # 🟡 Aguardando técnico aplicar medicação
    aguardando_medicacao = Atendimento.objects.filter(
        medico=request.user,
        decisao="medicacao",
        medicacao_aplicada=False,
        finalizado=False
    ).order_by("-id")

    # 🟢 Medicação já aplicada
    medicacao_aplicada = Atendimento.objects.filter(
        medico=request.user,
        decisao="medicacao",
        medicacao_aplicada=True,
        finalizado=False
    ).order_by("-id")

    # 🔴 Internações ativas
    internacoes = Atendimento.objects.filter(
        medico=request.user,
        decisao="internacao",
        finalizado=False
    ).order_by("-id")

    context = {
        "triagens": triagens,
        "atendimentos_finalizados": atendimentos_finalizados,
        "aguardando_medicacao": aguardando_medicacao,
        "medicacao_aplicada": medicacao_aplicada,
        "internacoes": internacoes,
        "total_pendentes": triagens.count(),
        "total_atendidos": atendimentos_finalizados.count(),
        "total_dia": atendimentos_finalizados.count(),
        "total_mes": Atendimento.objects.filter(
            medico=request.user,
            finalizado=True,
            data_atendimento__year=agora.year,
            data_atendimento__month=agora.month
        ).count(),
    }

    return render(request, "medico/dashboard.html", context)


# ==============================
# INICIAR ATENDIMENTO
# ==============================
@login_required
def iniciar_atendimento(request, triagem_id):
    with transaction.atomic():
        triagem = Triagem.objects.select_for_update().get(id=triagem_id)

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
    paciente = atendimento.paciente
    hoje = timezone.localdate()

    atendimentos_hoje = Atendimento.objects.filter(
        paciente=paciente,
        data_atendimento__date=hoje
    ).order_by('data_atendimento')

    medicacoes_dia = [
        (a.prescricao, a.medico.get_full_name(), a.data_atendimento.time())
        for a in atendimentos_hoje
        if a.prescricao and a.prescricao.strip()
    ]

    exames = atendimento.exames.all()

    if request.method == "POST":
        acao = request.POST.get("acao")

        # ==========================
        # 1️⃣ Solicitar novo exame
        # ==========================
        if acao == "novo_exame":
            nome_exame = request.POST.get("nome_exame")
            tipo_exame = request.POST.get("tipo_exame")

            if nome_exame and tipo_exame:
                Exame.objects.create(
                    atendimento=atendimento,
                    nome=nome_exame,
                    tipo=tipo_exame
                )

            return redirect("editar_atendimento", atendimento.id)

        # ==========================
        # 2️⃣ Salvar atendimento
        # ==========================
        elif acao == "salvar_atendimento":
            decisao = request.POST.get("decisao")
            if not decisao:
                return redirect("editar_atendimento", atendimento.id)

            atendimento.decisao = decisao
            atendimento.diagnostico = request.POST.get("diagnostico")
            atendimento.prescricao = request.POST.get("prescricao")
            atendimento.observacoes = request.POST.get("observacoes")

            if decisao == "dispensar":
                atendimento.finalizado = True
            elif decisao == "medicacao":
                atendimento.finalizado = False
                atendimento.medicacao_aplicada = False
                atendimento.tecnico_aplicou = None
                atendimento.horario_medicacao = None
            elif decisao == "internacao":
                atendimento.finalizado = False

            atendimento.save()
            return redirect("medico_dashboard")

    return render(request, "medico/atendimento.html", {
        "atendimento": atendimento,
        "medicacoes_dia": medicacoes_dia,
        "atendimentos_hoje": atendimentos_hoje,
        "exames": exames,
    })
# ==============================
# DECIDIR ATENDIMENTO
# ==============================
@login_required
def decidir_atendimento(request, atendimento_id):
    atendimento = get_object_or_404(Atendimento, id=atendimento_id)

    if request.method == "POST":
        atendimento.decisao = request.POST.get("decisao")
        atendimento.finalizado = True
        atendimento.save()
        return redirect("medico_dashboard")

    return render(request, "medico/decidir_atendimento.html", {
        "atendimento": atendimento
    })


# ==============================
# APLICAR MEDICAÇÃO (TÉCNICO)
# ==============================
@login_required
def aplicar_medicacao(request, atendimento_id):
    atendimento = get_object_or_404(Atendimento, id=atendimento_id)

    if request.user.perfil != "tecnico":
        return redirect("dashboard")

    atendimento.aplicar_medicacao(request.user)
    return redirect("tecnico_dashboard")


