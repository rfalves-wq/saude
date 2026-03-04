# ==================================================
# IMPORTS
# ==================================================
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from django.db import transaction

from triagem.models import Triagem
from medico.models import Atendimento, Exame
 
# ==================================================
# DASHBOARD MÉDICO
# ==================================================
@login_required
def medico_dashboard(request):
    agora = timezone.now()
    hoje = timezone.localdate()  # Data local

    # FILTRO POR DATA via GET
    data_filtro = request.GET.get("data_atendimento")
    if data_filtro:
        try:
            filtro_data = timezone.datetime.strptime(data_filtro, "%Y-%m-%d").date()
        except ValueError:
            filtro_data = hoje
    else:
        filtro_data = hoje

    # 🔴 Triagens pendentes (ordenadas por prioridade)
    triagens = Triagem.objects.filter(atendido=False).annotate(
        prioridade=Case(
            When(classificacao_risco="Vermelho", then=Value(1)),
            When(classificacao_risco="Laranja", then=Value(2)),
            When(classificacao_risco="Amarelo", then=Value(3)),
            When(classificacao_risco="Verde", then=Value(4)),
            When(classificacao_risco="Azul", then=Value(5)),
            default=Value(5),
            output_field=IntegerField(),
        )
    ).order_by("prioridade", "-data_triagem")

    # ✅ Atendimentos finalizados na data filtrada
    atendimentos_finalizados = Atendimento.objects.filter(
        medico=request.user,
        finalizado=True,
        data_atendimento__date=filtro_data
    ).order_by("-data_atendimento")

    # 🟡 Aguardando técnico aplicar medicação
    aguardando_medicacao = Atendimento.objects.filter(
        medico=request.user,
        decisao="medicacao",
        medicacao_aplicada=False,
        finalizado=False
    ).order_by("-id")

    # 🟢 Medicação aplicada
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

    # 📌 Totais
    total_pendentes = triagens.count()
    total_atendidos = atendimentos_finalizados.count()
    total_dia = Atendimento.objects.filter(
        medico=request.user,
        data_atendimento__date=filtro_data
    ).count()
    total_mes = Atendimento.objects.filter(
        medico=request.user,
        finalizado=True,
        data_atendimento__year=agora.year,
        data_atendimento__month=agora.month
    ).count()
    exames_prontos = Exame.objects.filter(
    atendimento__medico=request.user,
    status="pronto"
).select_related(
    "atendimento",
    "atendimento__paciente"
).order_by("-id")
    context = {
    "triagens": triagens,
    "atendimentos_finalizados": atendimentos_finalizados,
    "aguardando_medicacao": aguardando_medicacao,
    "medicacao_aplicada": medicacao_aplicada,
    "internacoes": internacoes,
    "total_pendentes": total_pendentes,
    "total_atendidos": total_atendidos,
    "total_dia": total_dia,
    "total_mes": total_mes,
    "data_filtro": filtro_data,
    "exames_prontos": exames_prontos,
}
    
    
    return render(request, "medico/dashboard.html", context)

# ==================================================
# INICIAR ATENDIMENTO
# ==================================================
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

# ==================================================
# EDITAR / FINALIZAR ATENDIMENTO
# ==================================================
@login_required
def editar_atendimento(request, atendimento_id):
    atendimento = get_object_or_404(Atendimento, id=atendimento_id)
    paciente = atendimento.paciente
    hoje = timezone.localdate()

    # Atendimentos do paciente hoje (para medicações já prescritas)
    atendimentos_hoje = Atendimento.objects.filter(
        paciente=paciente,
        data_atendimento__date=hoje
    ).order_by('data_atendimento')

    medicacoes_dia = [
        (a.prescricao, a.medico.get_full_name(), a.data_atendimento.time())
        for a in atendimentos_hoje
        if a.prescricao and a.prescricao.strip()
    ]

    # Exames do atendimento
    exames = atendimento.exames.all()

    if request.method == "POST":
        acao = request.POST.get("acao")

        # 1️⃣ Solicitar novo exame
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

        # 2️⃣ Salvar atendimento
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

# ==================================================
# DECIDIR ATENDIMENTO
# ==================================================
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

# ==================================================
# APLICAR MEDICAÇÃO (TÉCNICO)
# ==================================================
@login_required
def aplicar_medicacao(request, atendimento_id):
    atendimento = get_object_or_404(Atendimento, id=atendimento_id)

    if getattr(request.user, "perfil", None) != "tecnico":
        return redirect("dashboard")

    atendimento.aplicar_medicacao(request.user)
    return redirect("tecnico_dashboard")


from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Exame

# Verifica se é laboratório
def apenas_laboratorio(user):
    return user.is_authenticated and user.perfil == "laboratorio"

@login_required
@user_passes_test(apenas_laboratorio)
def laboratorio_lista(request):
    exames = Exame.objects.filter(
        tipo="laboratorio",
        status="solicitado"
    ).select_related("atendimento", "atendimento__paciente")

    return render(request, "medico/laboratorio_lista.html", {
        "exames": exames
    })


from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

@login_required
@user_passes_test(apenas_laboratorio)
def inserir_resultado(request, pk):
    exame = get_object_or_404(Exame, pk=pk)

    if request.method == "POST":
        resultado = request.POST.get("resultado")

        exame.resultado = resultado
        exame.status = "pronto"
        exame.save()

        return redirect("laboratorio_lista")

    return render(request, "medico/inserir_resultado.html", {
        "exame": exame
    })

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import Exame

@login_required
def visualizar_exame(request, exame_id):
    exame = get_object_or_404(Exame, id=exame_id)
    return render(request, 'medico/visualizar_exame.html', {'exame': exame})
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

@login_required
def gerar_pdf_exame(request, exame_id):
    exame = get_object_or_404(Exame, id=exame_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="exame_{exame.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph(f"<b>Exame:</b> {exame.nome}", styles['Normal']))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"<b>Paciente:</b> {exame.atendimento.paciente.nome}",
        styles['Normal']
    ))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"<b>Resultado:</b> {exame.resultado or 'Sem resultado'}",
        styles['Normal']
    ))

    doc.build(elements)

    return response