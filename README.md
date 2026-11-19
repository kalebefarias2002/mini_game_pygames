# Corrida

Um jogo de corrida em 3D feito em Python com Pygame e NumPy. O jogador desvia dos obstáculos e atira nos robôs que aparecem na pista.

## Requisitos

- Python 3
- Pygame
- NumPy

Instale as dependências com:

```bash
python -m pip install pygame numpy
```

## Como executar

No terminal, entre na pasta que contém `corrida.py` e a pasta de modelos `corrida/`, depois execute:

```bash
python corrida.py
```

O programa abre em tela cheia. Toque ou clique na metade esquerda da tela para mover o carro para a esquerda; use a metade direita para mover para a direita. O disparo acontece automaticamente. A tecla Esc encerra o jogo.

## Arquivos

- `corrida.py`: lógica do jogo, renderização, movimentação e combate.
- `corrida/*.obj`: modelos 3D usados pelo jogo, como jogador, robôs, árvores, balas e faixas da pista.

Mantenha a pasta `corrida/` no mesmo diretório de `corrida.py`, pois o programa carrega os modelos usando esse caminho relativo.

## Controles e objetivo

- Clique/toque na metade esquerda ou direita da tela para trocar de faixa.
- Acerte os robôs azuis para ganhar pontos; eles precisam de vários acertos.
- Evite os robôs vermelhos e os demais robôs que se aproximam: colisões reduzem as vidas.
- A partida começa com três vidas.

## Observação

O código está configurado para tela cheia. A opção `MEDIR` no início de `corrida.py` ativa um modo de medição de desempenho, que encerra após 600 quadros e grava resultados em `corrida/resultado.txt`.
