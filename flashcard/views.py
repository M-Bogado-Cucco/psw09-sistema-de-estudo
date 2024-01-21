from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.contrib.messages import constants
from django.contrib import messages
from django.http import HttpResponse, Http404

# Create your views here.

def novo_flashcard(request):
  if not request.user.is_authenticated:
    return redirect('/usuarios/logar')
  
  if request.method == "GET":
    categorias = Categoria.objects.all()
    dificuldades = Flashcard.DIFICULDADE_CHOICES

    # fazendo aparecer os flashcards do próprio usuário  53' aula 2
    flashcards = Flashcard.objects.filter(user=request.user)

    categoriaFiltrada = request.GET.get('categoria')
    dificuldadeFiltrada = request.GET.get('dificuldade')

    if categoriaFiltrada:
      flashcards = flashcards.filter(categoria__id = categoriaFiltrada)

    if dificuldadeFiltrada:
      flashcards = flashcards.filter(dificuldade = dificuldadeFiltrada)

    return render(request, 'novo_flashcard.html', 
      {'categorias': categorias, 
      'dificuldades': dificuldades,
      'flashcards': flashcards}
    )

  elif request.method == 'POST':
    pergunta = request.POST.get('pergunta')
    resposta = request.POST.get('resposta')
    categoria = request.POST.get('categoria')
    dificuldade = request.POST.get('dificuldade')
# strip, não deixa espaço em branco no input
    if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
      messages.add_message(request, constants.ERROR, "Preencha os campos de pergunta e resposta")
      return redirect('/flashcard/novo_flashcard/')
    
    flashcard = Flashcard(
      user = request.user,
      pergunta = pergunta,
      resposta = resposta,
      categoria_id = categoria,
      dificuldade = dificuldade,
    )

    flashcard.save()

    messages.add_message(request, constants.SUCCESS, "Flashcard cadastrado com sucesso!")
    return redirect('/flashcard/novo_flashcard')
  
def deletar_flashcard(request, id):
  # fazer a validação de segurança
  flashcard = Flashcard.objects.get(id=id)
  # print(type(flashcard))

  if not flashcard.user == request.user:
    messages.add_message(request, constants.ERROR, 'Somente o dono deste flashcard pode removê-lo!')
    return redirect('/flashcard/novo_flashcard/')
  
  flashcard.delete()
  messages.add_message(request, constants.INFO, 'Flashcard deletado com sucesso!')
  return redirect('/flashcard/novo_flashcard/')


def iniciar_desafio(request):
  if request.method == 'GET':
    categorias = Categoria.objects.all()
    dificuldades = Flashcard.DIFICULDADE_CHOICES
    return render(request, 'iniciar_desafio.html', 
      {'categorias': categorias, 'dificuldades': dificuldades})
  elif request.method == "POST":
    titulo = request.POST.get('titulo')
    categorias = request.POST.getlist('categoria')
    dificuldade = request.POST.get('dificuldade')
    qtd_perguntas = request.POST.get('qtd_perguntas')

    desafio = Desafio(
      user=request.user,
      titulo=titulo,
      quantidade_perguntas = qtd_perguntas,
      dificuldade=dificuldade
    )

    desafio.save()

    for categoria in categorias:
      desafio.categoria.add(categoria)

    flashcards = (
      Flashcard.objects.filter(user=request.user)
      .filter(dificuldade=dificuldade)
      .filter(categoria_id__in=categorias)
      .order_by('?')
    )

    if flashcards.count() < int(qtd_perguntas):
      # tratar erro
      return redirect('/flashcard/iniciar_desafio/')
    
    flashcards = flashcards[: int(qtd_perguntas)]

    for f in flashcards:
      flashcard_desafio = FlashcardDesafio(
        flashcard=f
      )
      flashcard_desafio.save()
      desafio.flashcards.add(flashcard_desafio)

    desafio.save()
    # return HttpResponse("Teste")
    return redirect('/flashcard/listar_desafio')
  

def listar_desafio(request):
  desafios = Desafio.objects.filter(user=request.user)
  return render(request, 'listar_desafio.html', {'desafios': desafios})

  if request.method == "GET":
    categorias = Categoria.objects.all()
    dificuldades = Flashcard.DIFICULDADE_CHOICES

    # fazendo aparecer os flashcards do próprio usuário  53' aula 2
    flashcards = Flashcard.objects.filter(user=request.user)

    categoriaFiltrada = request.GET.get('categoria')
    dificuldadeFiltrada = request.GET.get('dificuldade')

    if categoriaFiltrada:
      flashcards = flashcards.filter(categoria__id = categoriaFiltrada)

    if dificuldadeFiltrada:
      flashcards = flashcards.filter(dificuldade = dificuldadeFiltrada)

    return render(request, 'novo_flashcard.html', 
      {'categorias': categorias, 
      'dificuldades': dificuldades,
      'flashcards': flashcards}
    )


def desafio(request, id):
  desafio = Desafio.objects.get(id=id)
  if not desafio.user == request.user:
    raise Http404()
  if request.method == "GET":
    acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
    erros = desafio.flashcards.filter(respondido=False).filter(acertou=False).count()
    faltantes = desafio.flashcards.filter(respondido=False).count()
    return render(request, 'desafio.html', 
        {'desafio': desafio, 
        'acertos': acertos, 
        'erros': erros, 
        'faltantes': faltantes})
  

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
      raise Http404()

    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()
    return redirect(f'/flashcard/desafio/{desafio_id}/')

def relatorio(request, id):
  desafio = Desafio.objects.get(id=id)

  acertos = desafio.flashcards.filter(acertou=True).count()
  erros = desafio.flashcards.filter(acertou=False).count()

  dados = [acertos, erros]

  categorias = desafio.categoria.all()

  name_categoria = []

  for i in categorias:
    name_categoria.append(i.nome)

  qtd_acertos = []
  for categoria in categorias:
    qtd_acertos.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count()) # acessa a categoria de flashcard

  # fazer o ranking

  return render(request, 'relatorio.html', 
    {'desafio': desafio, 'dados': dados,
    'categorias': name_categoria, 'qtd_acertos': qtd_acertos})