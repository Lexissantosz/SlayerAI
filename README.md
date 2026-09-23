# SlayerAI

SlayerAI e um projeto experimental de visao computacional e automacao para o Idle Slayer.

A proposta e construir a automacao em camadas: primeiro enxergar o jogo com seguranca e de forma portatil; depois reconhecer outros elementos da tela; por fim, adicionar decisoes e comandos.

## Estado atual: v0.1

A v0.1 ja possui:

- captura direta da janela do Idle Slayer no Windows;
- captura funcionando mesmo quando outras janelas estao por cima do jogo;
- encerramento limpo quando o jogo e fechado;
- coleta automatica de frames para dataset;
- rotulagem e revisao de bounding boxes no formato YOLO;
- validacao de consistencia do dataset;
- split reproducivel em treino e validacao;
- treinamento de detector leve do personagem;
- exportacao para ONNX;
- deteccao do player em tempo real;
- suporte opcional a ROI e suavizacao da caixa;
- benchmark offline de latencia e taxa de deteccao;
- diagnostico do ambiente;
- testes automatizados de funcoes puras;
- CI no GitHub Actions.

A camada de controle do jogo ainda nao faz parte da v0.1.

## Requisitos

- Windows;
- Python 3.12+;
- Idle Slayer instalado;
- jogo aberto e restaurado para captura;
- ambiente virtual recomendado.

A captura minimizada fica para uma versao futura.

## Instalacao rapida

No Windows:

```bat
setup.bat
```

Ou manualmente:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Para verificar o ambiente:

```powershell
python src/diagnostico.py
```

## Executar

O ponto de entrada principal da v0.1 e:

```powershell
python src/slayerai.py
```

Tambem existe:

```bat
run.bat
```

O detector prefere automaticamente:

```text
modelos/player_v01.onnx
```

e usa o peso PyTorch local como fallback quando disponivel.

## Ajustes de desempenho

Teste padrao:

```powershell
python src/testar_detector.py
```

Menor resolucao e menos inferencias:

```powershell
python src/testar_detector.py --imgsz 256 --detectar-a-cada 3
```

ROI opcional, usando apenas parte da tela:

```powershell
python src/testar_detector.py --roi 0,0,0.55,1
```

A ROI usa valores normalizados:

```text
x,y,largura,altura
```

O preview mostra FPS e tempo da ultima inferencia.

## Benchmark

Para medir o detector usando frames ja coletados:

```powershell
python src/benchmark_detector.py --limite 50
```

Para comparar uma ROI:

```powershell
python src/benchmark_detector.py --limite 50 --roi 0,0,0.55,1
```

O benchmark informa taxa de deteccao, latencia media, mediana, P95 e confianca media.

## Pipeline de dataset

### 1. Coletar

```powershell
python src/coletar_dataset.py --limite 100
```

### 2. Rotular

```powershell
python src/rotular_dataset.py
```

Controles:

- mouse: desenhar ou corrigir a caixa;
- Enter ou Espaco: salvar;
- N: imagem realmente sem player;
- R: limpar a caixa;
- Q: encerrar.

### 3. Revisar

```powershell
python src/revisar_rotulos.py --limite 20
```

### 4. Validar

```powershell
python src/validar_dataset.py
```

### 5. Dividir

```powershell
python src/preparar_dataset.py
```

Por padrao, 80% vai para treino e 20% para validacao.

### 6. Treinar

```powershell
python src/treinar_detector.py --epochs 20
```

### 7. Exportar ONNX

```powershell
python src/exportar_onnx.py
```

## Dados e direitos de uso

Sprites extraidos, screenshots e o dataset bruto do jogo nao sao versionados no repositorio publico.

O repositorio prioriza:

- codigo;
- configuracoes;
- documentacao;
- testes;
- modelo ONNX final validado.

## Estrutura

```text
SlayerAI/
|-- .github/workflows/
|-- docs/
|-- modelos/
|-- src/
|   |-- captura.py
|   |-- detector.py
|   |-- slayerai.py
|   |-- testar_detector.py
|   |-- benchmark_detector.py
|   |-- diagnostico.py
|   |-- coletar_dataset.py
|   |-- rotular_dataset.py
|   |-- revisar_rotulos.py
|   |-- validar_dataset.py
|   |-- preparar_dataset.py
|   |-- treinar_detector.py
|   |-- exportar_onnx.py
|   `-- visao_utils.py
|-- tests/
|-- dataset.yaml
|-- requirements.txt
|-- requirements-dev.txt
|-- setup.bat
`-- run.bat
```

Mais detalhes tecnicos estao em [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) e o planejamento em [docs/ROADMAP.md](docs/ROADMAP.md).


## Dry-run e replay

Para exercitar o pipeline completo sem enviar nenhuma tecla:

```powershell
python src/dry_run.py
```

O comando gera uma sessao local em:

```text
sessoes/dry_run.jsonl
```

Para reproduzir a sessao depois:

```powershell
python src/replay_sessao.py sessoes/dry_run.jsonl
```

O replay recalcula as decisoes e informa se houve divergencia em relacao ao que foi registrado. Arquivos de sessao sao locais e nao sao versionados por padrao.
