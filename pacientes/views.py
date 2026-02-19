from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Paciente
from .forms import PacienteForm
from django.core.paginator import Paginator
from django.db.models import Q

# 🔒 Verifica se é recepção
def apenas_recepcao(user):
    return user.is_authenticated and user.perfil == 'recepcao'


@login_required
@user_passes_test(apenas_recepcao)

def paciente_list(request):
    pacientes = Paciente.objects.all().order_by('nome')

    # ================= FILTROS =================
    nome = request.GET.get('nome')
    cpf = request.GET.get('cpf')

    if nome:
        pacientes = pacientes.filter(nome__icontains=nome)

    if cpf:
        pacientes = pacientes.filter(cpf__icontains=cpf)

    # ================= PAGINAÇÃO =================
    paginator = Paginator(pacientes, 5)  # 5 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'nome': nome,
        'cpf': cpf,
    }

    return render(request, 'pacientes/paciente_list.html', context)



@login_required
@user_passes_test(apenas_recepcao)
def paciente_create(request):
    form = PacienteForm(request.POST or None)

    if form.is_valid():
        paciente = form.save(commit=False)
        paciente.criado_por = request.user
        paciente.save()
        return redirect('paciente_list')

    return render(request, 'pacientes/paciente_form.html', {'form': form})


@login_required
@user_passes_test(apenas_recepcao)
def paciente_update(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)
    form = PacienteForm(request.POST or None, instance=paciente)

    if form.is_valid():
        form.save()
        return redirect('paciente_list')

    return render(request, 'pacientes/paciente_form.html', {'form': form})


@login_required
@user_passes_test(apenas_recepcao)
def paciente_delete(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk)

    if request.method == 'POST':
        paciente.delete()
        return redirect('paciente_list')

    return render(request, 'pacientes/paciente_confirm_delete.html', {'paciente': paciente})


from django.shortcuts import render, get_object_or_404
from .models import Paciente
from triagem.models import Triagem
from medico.models import Atendimento
from itertools import chain
from operator import attrgetter

@login_required
def historico_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    triagens = Triagem.objects.filter(
        paciente=paciente
    )

    atendimentos = Atendimento.objects.filter(
        paciente=paciente
    )

    # 🔹 Criando lista unificada
    historico = []

    for t in triagens:
        historico.append({
            'tipo': 'triagem',
            'data': t.data_triagem,
            'obj': t
        })

    for a in atendimentos:
        historico.append({
            'tipo': 'atendimento',
            'data': a.data_atendimento,  # ajuste se o nome for diferente
            'obj': a
        })

    # 🔹 Ordena por data (mais recente primeiro)
    historico.sort(key=lambda x: x['data'], reverse=True)

    return render(request, 'pacientes/historico.html', {
        'paciente': paciente,
        'historico': historico,
    })
from django.shortcuts import render, get_object_or_404
from triagem.models import Triagem
from medico.models import Atendimento
from pacientes.models import Paciente
from django.shortcuts import render, get_object_or_404
from pacientes.models import Paciente
from triagem.models import Triagem

from django.shortcuts import render, get_object_or_404
from pacientes.models import Paciente
from triagem.models import Triagem
from medico.models import Atendimento

def imprimir_historico(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)

    historico = []

    # ===== Triagens =====
    triagens = Triagem.objects.filter(paciente=paciente).order_by('-data_triagem')
    for t in triagens:
        historico.append({
            'tipo': 'triagem',
            'data': t.data_triagem,
            'obj': t
        })

    # ===== Atendimentos =====
    atendimentos = Atendimento.objects.filter(paciente=paciente).order_by('-data_atendimento')
    for a in atendimentos:
        historico.append({
            'tipo': 'atendimento',
            'data': a.data_atendimento,
            'obj': a
        })

    # ===== Ordena tudo por data decrescente =====
    historico.sort(key=lambda x: x['data'], reverse=True)

    context = {
        'paciente': paciente,
        'historico': historico,
    }

    return render(request, 'pacientes/historico_imprimir.html', context)


from django.utils import timezone
from django.db.models import Q

def imprimir_historico_do_dia(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    hoje = timezone.localdate()  # pega a data de hoje (sem hora)

    historico = []

    # ===== Triagens do dia =====
    triagens = Triagem.objects.filter(
        paciente=paciente,
        data_triagem__date=hoje
    ).order_by('-data_triagem')
    for t in triagens:
        historico.append({
            'tipo': 'triagem',
            'data': t.data_triagem,
            'obj': t
        })

    # ===== Atendimentos do dia =====
    atendimentos = Atendimento.objects.filter(
        paciente=paciente,
        data_atendimento__date=hoje
    ).order_by('-data_atendimento')
    for a in atendimentos:
        historico.append({
            'tipo': 'atendimento',
            'data': a.data_atendimento,
            'obj': a
        })

    # Ordena tudo por hora decrescente
    historico.sort(key=lambda x: x['data'], reverse=True)

    context = {
        'paciente': paciente,
        'historico': historico,
        'data_filtro': hoje,
    }

    return render(request, 'pacientes/historico_imprimir.html', context)

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from xhtml2pdf import pisa

from pacientes.models import Paciente
from triagem.models import Triagem
from medico.models import Atendimento

# ===== PDF Histórico Completo =====
def imprimir_historico_pdf(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    agora = timezone.localtime()

    historico = []

    triagens = Triagem.objects.filter(paciente=paciente).order_by('-data_triagem')
    for t in triagens:
        historico.append({'tipo': 'triagem', 'data': t.data_triagem, 'obj': t})

    atendimentos = Atendimento.objects.filter(paciente=paciente).order_by('-data_atendimento')
    for a in atendimentos:
        historico.append({'tipo': 'atendimento', 'data': a.data_atendimento, 'obj': a})

    historico.sort(key=lambda x: x['data'], reverse=True)

    context = {'paciente': paciente, 'historico': historico, 'now': agora}
    template_path = 'pacientes/historico_imprimir.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Historico_{paciente.nome}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF")
    return response

# ===== PDF Histórico do Dia =====
def imprimir_historico_dia_pdf(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    agora = timezone.localtime()
    hoje = agora.date()

    historico = []

    triagens = Triagem.objects.filter(paciente=paciente, data_triagem__date=hoje).order_by('-data_triagem')
    for t in triagens:
        historico.append({'tipo': 'triagem', 'data': t.data_triagem, 'obj': t})

    atendimentos = Atendimento.objects.filter(paciente=paciente, data_atendimento__date=hoje).order_by('-data_atendimento')
    for a in atendimentos:
        historico.append({'tipo': 'atendimento', 'data': a.data_atendimento, 'obj': a})

    historico.sort(key=lambda x: x['data'], reverse=True)

    context = {'paciente': paciente, 'historico': historico, 'now': agora}
    template_path = 'pacientes/historico_imprimir.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Historico_{paciente.nome}_Dia.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF")
    return response
