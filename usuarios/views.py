from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario
from .forms import UsuarioForm, UsuarioUpdateForm
from django.core.paginator import Paginator

# Listar usuários
from django.core.paginator import Paginator
from django.db.models import Q  # necessário para busca combinada

def usuario_list(request):
    perfil_filtro = request.GET.get('perfil', 'todos')
    busca = request.GET.get('busca', '')

    usuarios = Usuario.objects.all().order_by('username')

    # filtro por perfil
    if perfil_filtro != 'todos':
        usuarios = usuarios.filter(perfil=perfil_filtro)

    # busca por username ou email
    if busca:
        usuarios = usuarios.filter(Q(username__icontains=busca) | Q(email__icontains=busca))

    # paginação
    paginator = Paginator(usuarios, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'perfil_filtro': perfil_filtro,
        'busca': busca,
    }
    return render(request, 'usuarios/usuario_list.html', context)



# Criar usuário
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuario_list')
    else:
        form = UsuarioForm()
    return render(request, 'usuarios/usuario_form.html', {'form': form})

# Editar usuário
def usuario_update(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('usuario_list')
    else:
        form = UsuarioUpdateForm(instance=usuario)
    return render(request, 'usuarios/usuario_form.html', {'form': form})

# Deletar usuário
def usuario_delete(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        usuario.delete()
        return redirect('usuario_list')
    return render(request, 'usuarios/usuario_confirm_delete.html', {'usuario': usuario})



