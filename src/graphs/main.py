from .io import ler_mapa  # Funciona diretamente se não houver 'from .io'
from .graph import Grafo
from .visualizacao import desenhar_grafo
from .estados import construir_grafo_estados, construir_grafo_posicoes

# 1. Instanciar o grafo e carregar o mapa
grafo_posicoes = Grafo()

# Certifique-se de que o caminho aponta corretamente para a pasta data
mapa = ler_mapa("data/mapas/m02_uma_chave.txt")

# Se construir_grafo_estados retorna (grafo, inicio)
grafo_estados, inicio_estado = construir_grafo_estados(mapa)

# Se construir_grafo_posicoes também retorna uma tupla
grafo_posicoes = construir_grafo_posicoes(mapa)

# Agora sim grafo_estados é um objeto Grafo que possui .adjacencia
desenhar_grafo(grafo_estados, mapa)
