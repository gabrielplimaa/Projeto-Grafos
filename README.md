# Projeto Grafos

Projeto integrador de **Teoria dos Grafos** e **Análise e Visualização de Dados (AVD)**, semestre 2026.2. Na primeira parte, modelamos labirintos com chaves, portas, esteiras e bônus. Na segunda, analisamos a rede de avaliações [Bitcoin OTC](https://snap.stanford.edu/data/soc-sign-bitcoin-otc.html), publicada pelo SNAP.

## Relatório do projeto

- [Relatório técnico e manual de uso (PDF)](docs/RELATORIO_TECNICO.pdf)

## Instalação

Use **Python 3.13**. Os comandos abaixo partem da raiz do repositório.

```bash
git clone https://github.com/gabrielplimaa/Projeto-Grafos.git
cd Projeto-Grafos
python -m venv .venv
```

Ative o ambiente virtual no seu terminal.

**Windows (PowerShell)**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux ou macOS**

```bash
source .venv/bin/activate
```

Instale as dependências e execute os testes.

```bash
python -m pip install -r requirements.txt
python -m pytest -q
```

## Parte 1 — Labirintos

O grafo de posições representa as casas do mapa. O grafo de estados também guarda as chaves e os bônus já consumidos. Assim, o jogador pode voltar à mesma casa em outro estado e atravessar uma porta depois de pegar a chave certa.

A BFS encontra a rota com menos passos. O Dijkstra encontra a de menor custo quando os pesos são não negativos. No m01, a BFS atravessa a água em uma rota de **10 passos e custo 30**, enquanto o Dijkstra encontra uma rota de **14 passos e custo 20**. A DFS ajuda a explorar o grafo e classificar seus arcos. O Bellman-Ford permite trabalhar com pesos negativos e detectar ciclos negativos alcançáveis.

### Consultar um mapa

```bash
python -m src.cli --mapa data/mapas/m01_terreno.txt --alg BFS
python -m src.cli --mapa data/mapas/m01_terreno.txt --alg DIJKSTRA
python -m src.cli --mapa data/mapas/m04_esteiras.txt --armadilhas
```

Para comparar a regra original da fonte de energia do m06 com a versão em que o desconto vale uma vez:

```bash
python -m src.cli --mapa data/mapas/m06_fonte.txt --alg BELLMAN_FORD
python -m src.cli --mapa data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel
```

### Gerar os arquivos da Parte 1

```bash
python -m src.cli --relatorios --out out/parte1
python -m src.cli --figuras --out out/parte1
python -m src.cli --interactive --out out/parte1
```

Abra [`labirinto_interativo.html`](out/parte1/labirinto_interativo.html) no navegador a partir da sua cópia local. Os relatórios incluem as [soluções por mapa](out/parte1/solucoes.csv), a [comparação das modelagens](out/parte1/comparacao_modelagem.csv), as [métricas globais](out/parte1/metricas_global.json) e as [camadas de chaves](out/parte1/camadas.json).

## Parte 2 — Rede Bitcoin OTC

Cada vértice representa um usuário, e cada arco vai de quem deu a nota para quem a recebeu. A rede tem **5.881 usuários** e **35.592 avaliações**. No Dijkstra, o custo de cada arco é `rating + 10`, o que deixa os pesos entre 0 e 20. O Bellman-Ford usa as notas originais. Somar 10 a cada arco pode alterar qual percurso tem o menor custo, pois o acréscimo depende da quantidade de passos.

O CSV já está em `data/dataset_parte2/`. Se precisar baixá-lo novamente, execute `python data/dataset_parte2/baixar_dataset.py`.

### Executar os experimentos

```bash
python -m src.cli --dataset data/dataset_parte2 --alg DIJKSTRA --source 35 --target 2642
python -m src.cli --dataset data/dataset_parte2 --benchmark --out out/parte2
python -m src.parte2.exploracao_avd
python -m src.parte2.figuras_parte2
```

O benchmark gera [`parte2_report.json`](out/parte2/parte2_report.json), com as consultas e os tempos nos recortes de 10%, 50% e 100%. O script de figuras usa esse relatório e o CSV da rede.

### Concentração das avaliações

Comparamos quanto das avaliações **+1** e **−10** foi emitido pelos 10% de usuários mais ativos para cada nota. As duas notas apresentaram concentração parecida, embora +1 tenha sido dada por mais usuários.

| Nota | Usuários que emitiram a nota | Parcela emitida pelos 10% mais ativos naquela nota |
| --- | ---: | ---: |
| +1 | 3.791 | 57,8% |
| −10 | 558 | 58,6% |

A [curva de Lorenz](out/parte2/05_curva_lorenz_gini_emissao.png) mostra a concentração geral. O [gráfico dos maiores emissores](out/parte2/06_top_emissores_vs_volume.png) separa as avaliações positivas e negativas dos 15 usuários mais ativos. A [comparação dos tempos](out/parte2/07_comparacao_algoritmos_parte2.png) mostra o desempenho dos algoritmos nos recortes testados.

## Organização do repositório

| Pasta | Conteúdo |
| --- | --- |
| `data/mapas/` e `data/mapas_grupo/` | Mapas do enunciado e mapas criados pelo grupo |
| `data/dataset_parte2/` | CSV da rede Bitcoin OTC e script de download |
| `src/graphs/` | Estruturas de grafo, modelagem do labirinto e algoritmos |
| `src/parte2/` | Experimentos, análise exploratória e figuras |
| `out/parte1/` e `out/parte2/` | Resultados publicados |
| `tests/` | Testes automatizados |
| `docs/` | [Declaração de uso de IA](docs/DECLARACAO_USO_IA_2026-2.pdf) |
