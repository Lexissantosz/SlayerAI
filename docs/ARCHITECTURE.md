# Arquitetura do SlayerAI

## Objetivo da v0.1

A v0.1 estabelece a camada visual do projeto: capturar o Idle Slayer
diretamente da janela do Windows e localizar o personagem com um
detector treinado.

## Fluxo atual

```text
Idle Slayer
    |
    v
PrintWindow / captura.py
    |
    v
frame BGR
    |
    v
DetectorPlayer / detector.py
    |
    +--> opcional: ROI
    |
    v
YOLO / ONNX
    |
    v
bounding box + confianca + latencia
    |
    v
preview / slayerai.py
```

## Componentes

- `captura.py`: captura direta da janela, inclusive quando outra janela
  esta por cima. A janela do jogo precisa continuar restaurada.
- `detector.py`: encapsula o modelo e devolve a melhor deteccao do player.
- `visao_utils.py`: ROI e suavizacao temporal das caixas.
- `slayerai.py`: ponto de entrada principal da v0.1.
- `benchmark_detector.py`: mede latencia e taxa de deteccao offline.
- `validar_dataset.py`: confere integridade dos labels YOLO.
- scripts de dataset/treino: coleta, rotulagem, revisao, split, treino e
  exportacao ONNX.

## Dados e modelo

Screenshots e dataset bruto nao sao versionados. O repositorio deve
conter o codigo, configuracoes e o modelo ONNX final.

O arquivo esperado para execucao portatil e:

```text
modelos/player_v01.onnx
```

## Proximas camadas

Depois da visao, o projeto pode evoluir para:

1. reconhecimento de outros objetos;
2. estado do jogo;
3. politica de decisoes;
4. envio de comandos ao jogo em segundo plano;
5. minigames e aprendizado a partir de demonstracoes.
