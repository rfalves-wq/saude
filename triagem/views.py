from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncMonth

from recepcao.models import Agendamento
from .models import Triagem
from .forms import TriagemForm


# ==============================
# DASHBOARD TRIAGEM (FILA)
# ==============================
@login_required
def triagem_dashboard(request):

    fila = Agendamento.objects.filter(status="Em Triagem")

    context = {
        'fila': fila
    }

    return render(request, 'triagem/triagem_dashboard.html', context)


# ==============================
# REALIZAR TRIAGEM
# ==============================
@login_required
def realizar_triagem(request, id):

    agendamento = get_object_or_404(Agendamento, id=id)

    if request.method == 'POST':

        form = TriagemForm(request.POST)

        if form.is_valid():

            triagem = form.save(commit=False)

            triagem.agendamento = agendamento
            triagem.paciente = agendamento.paciente
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


# ==============================
# HISTÓRICO COMPLETO TRIAGENS
# ==============================
@login_required
def historico_triagens(request):

    triagens = Triagem.objects.select_related(
        'paciente', 'enfermeiro'
    ).order_by('-data_triagem')


    # ==========================
    # FILTROS
    # ==========================
    busca = request.GET.get('busca')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if busca:
        triagens = triagens.filter(
            paciente__nome__icontains=busca
        )

    if data_inicio:
        triagens = triagens.filter(
            data_triagem__date__gte=data_inicio
        )

    if data_fim:
        triagens = triagens.filter(
            data_triagem__date__lte=data_fim
        )


    # ==========================
    # PAGINAÇÃO
    # ==========================
    paginator = Paginator(triagens, 10)

    page = request.GET.get('page')

    triagens_page = paginator.get_page(page)


    # ==========================
    # RESUMO HOJE / MES / TOTAL
    # ==========================
    hoje = timezone.now().date()
    agora = timezone.now()

    total_hoje = Triagem.objects.filter(
        data_triagem__date=hoje
    ).count()

    total_mes = Triagem.objects.filter(
        data_triagem__year=agora.year,
        data_triagem__month=agora.month
    ).count()

    total_geral = Triagem.objects.count()


    # ==========================
    # AGRUPADO POR DIA
    # ==========================
    por_dia = (
        Triagem.objects
        .annotate(dia=TruncDate('data_triagem'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('-dia')
    )


    # ==========================
    # AGRUPADO POR MES
    # ==========================
    por_mes = (
        Triagem.objects
        .annotate(mes=TruncMonth('data_triagem'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('-mes')
    )


    # ==========================
    # CONTEXT
    # ==========================
    context = {

        'triagens': triagens_page,
        'page_obj': triagens_page,

        'busca': busca,
        'data_inicio': data_inicio,
        'data_fim': data_fim,

        'total_hoje': total_hoje,
        'total_mes': total_mes,
        'total_geral': total_geral,

        'por_dia': por_dia,
        'por_mes': por_mes,
    }


    return render(
        request,
        'triagem/historico_triagens.html',
        context
    )


# ==============================
# FILA JSON (TEMPO REAL)
# ==============================
@login_required
def fila_triagem_json(request):

    fila = Agendamento.objects.filter(
        status="Em Triagem"
    )

    dados = []

    for ag in fila:

        dados.append({

            "id": ag.id,
            "paciente": ag.paciente.nome,

            "data": ag.data.strftime("%d/%m/%Y"),

            "hora": ag.hora.strftime("%H:%M"),

            "classificacao":
            ag.triagem.classificacao_risco
            if hasattr(ag, 'triagem') else None
        })

    return JsonResponse({"fila": dados})


# ==============================
# RELATÓRIO POR DIA
# ==============================
from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.core.paginator import Paginator
from django.utils import timezone


def triagens_por_dia(request):

    # filtro opcional
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    triagens = Triagem.objects.all()

    if data_inicio:
        triagens = triagens.filter(data_triagem__date__gte=data_inicio)

    if data_fim:
        triagens = triagens.filter(data_triagem__date__lte=data_fim)


    # agrupamento por dia
    dados = (
        triagens
        .annotate(dia=TruncDate('data_triagem'))
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('-dia')
    )


    # paginação (10 dias por página)
    paginator = Paginator(dados, 10)
    page = request.GET.get('page')
    dados_page = paginator.get_page(page)


    # resumo
    hoje = timezone.now().date()
    agora = timezone.now()

    total_hoje = Triagem.objects.filter(data_triagem__date=hoje).count()

    total_mes = Triagem.objects.filter(
        data_triagem__year=agora.year,
        data_triagem__month=agora.month
    ).count()

    total_geral = Triagem.objects.count()


    context = {

        'dados': dados_page,
        'page_obj': dados_page,

        'total_hoje': total_hoje,
        'total_mes': total_mes,
        'total_geral': total_geral,

        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }

    return render(request, 'triagem/triagens_por_dia.html', context)