# SlayerAI

Projeto experimental de visao computacional e IA para reconhecer elementos do Idle Slayer e executar acoes como pular, atacar, coletar itens e interagir com minigames.

## v0.1 - visao computacional

Estado atual:

- captura direta da janela do Idle Slayer no Windows;
- coleta automatica de frames para dataset;
- rotulagem semiautomatica do personagem no formato YOLO;
- dataset bruto mantido fora do repositorio;
- objetivo seguinte: treinar e integrar um detector leve e portatil.

## Ambiente

Python 3.14+ no Windows, ambiente virtual recomendado.

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Coletar frames

Com o Idle Slayer aberto e restaurado:

```powershell
python src/coletar_dataset.py --limite 100
```

Os frames ficam em `dataset/raw/` e nao sao versionados.

## Rotular o personagem

Se existir `assets/personagem_template.png`, o rotulador usa o template apenas para sugerir uma caixa inicial. O usuario pode corrigir com o mouse.

```powershell
python src/rotular_dataset.py --limite 20
```

Controles:

- mouse: desenhar/corrigir a caixa do personagem;
- Enter ou Espaco: salvar;
- N: marcar imagem sem personagem;
- R: limpar a caixa;
- Q: encerrar a sessao.

As imagens aprovadas vao para `dataset/images/` e os rotulos YOLO para `dataset/labels/`.

> Observacao: sprites, screenshots e dataset do jogo ficam fora do repositorio publico. O objetivo e versionar codigo, configuracoes e o modelo treinado.
