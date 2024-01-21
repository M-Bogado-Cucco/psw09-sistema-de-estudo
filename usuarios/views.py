from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth

# Create your views here.

def cadastro(request):
  if request.method == "GET":
    return render(request, 'cadastro.html')
  elif request.method == "POST":
    username = request.POST.get('username') # pega o nome digitado no form
    senha = request.POST.get('senha')
    confirmar_senha = request.POST.get('confirmar_senha')

    if not senha == confirmar_senha:
      messages.add_message(request, constants.ERROR, 'Senha diferente da confirmação da senha')
      return redirect('/usuarios/cadastro')
    
    user = User.objects.filter(username = username)

    if user.exists():
      messages.add_message(request, constants.ERROR, 'Este usuário já existe')
      return redirect('/usuarios/cadastro')
    
    try:
      User.objects.create_user(
        username=username,  # conforme nome da tabela do BD
        password=senha
      )
      return redirect('/usuarios/login')
    except:
      messages.add_message(request, constants.ERROR, 'Servidor com erro interno')
      return redirect('/usuarios/cadastro')
    
    
def logar(request):
  if (request.method == "GET"):
    return render(request, 'login.html')
  elif request.method == "POST":
    username = request.POST.get('username')
    senha = request.POST.get('senha')

    user = auth.authenticate(request, username=username, password=senha)

    if user:
      auth.login(request, user)
      messages.add_message(request, constants.SUCCESS, 'Usuário LOGADO!')
      return redirect('/flashcard/novo_flashcard/')
    else:
      messages.add_message(request, constants.ERROR, 'USERNAME ou SENHA inválido(s)!')
      return redirect('/usuarios/logar')


def logout(request):
  auth.logout(request)
  return redirect('/usuarios/login')


