# v0.2 - Detector multiclasse

A v0.2 amplia a visao do SlayerAI para reconhecer mais de um tipo de objeto
na mesma tela.

## Escopo atual

Classes treinadas nesta etapa:

- `0: player`;
- `1: inimigo`.

A classe `inimigo` e propositalmente generica nesta primeira iteracao.
Inimigos de outros portais e mundos devem ser adicionados ao mesmo dataset
quando houver oportunidade de coleta. Se algum grupo exigir uma acao
mecanicamente diferente no futuro, a taxonomia pode ser refinada por
comportamento.

## Dataset atual

O dataset local nao e versionado.

Estado validado desta iteracao:

- 120 imagens rotuladas;
- 120 labels;
- 65 imagens de treino;
- 55 imagens de validacao;
- split por sessao, sem misturar a sessao de validacao no treino;
- coleta manual focada usada para aumentar a presenca de inimigos.

A validacao foi reservada pela sessao com prefixo `frame`.

## Pipeline

### 1. Validar dataset

```powershell
python src/validar_dataset_v02.py
```

### 2. Dividir por sessao

```powershell
python src/preparar_dataset_v02.py --val-prefixo frame
```

Para manter validacao em mais de um mundo, use varios prefixos:

```powershell
python src/preparar_dataset_v02.py --val-prefixo frame --val-prefixo mundo2_val
```

Isso permite treinar com exemplos de varios mundos sem misturar, na validacao,
frames temporalmente proximos das sessoes de treino.

### 3. Treinar

Configuracao inicial pensada para CPU antiga:

```powershell
python src/treinar_detector_v02.py
```

Padroes:

- YOLO11n;
- 30 epocas;
- imgsz 320;
- batch 4;
- device CPU;
- early stopping com patience 8.

O melhor peso e copiado para:

```text
modelos/multiclasse_v02_best.pt
```

### 4. Avaliar

```powershell
python src/avaliar_detector_v02.py
```

O script executa a validacao do YOLO na sessao reservada e mostra mAP global
e por classe.

### 5. Testar ao vivo

```powershell
python src/testar_detector_v02.py
```

Cores do preview:

- verde: player;
- vermelho: inimigo;
- amarelo: classe desconhecida.

O teste ao vivo ainda e uma etapa de observacao. Nao envia comandos para o
jogo.

### 6. Exportar ONNX

Somente depois de validar o peso PyTorch:

```powershell
python src/exportar_onnx_v02.py
```

Saida local:

```text
modelos/multiclasse_v02.onnx
```

O ONNX nao deve substituir `player_v01.onnx` ate a v0.2 ser comparada e
validada.

## Regras de seguranca do desenvolvimento

- preservar o detector v0.1 como rollback;
- nao usar split aleatorio de frames consecutivos;
- adicionar inimigos de outros mundos antes de considerar a classe
  `inimigo` generalizada;
- validar primeiro em dry-run;
- manter ascensao e progresso estrategico sob controle do usuario.


## Baseline 0.2 inicial

A primeira avaliacao do baseline, treinado antes da coleta do segundo mundo,
obteve:

- precisao global: 0.895;
- recall global: 0.796;
- mAP50 global: 0.867;
- mAP50-95 global: 0.405;
- player: precisao 0.975, recall 1.000, mAP50 0.995, mAP50-95 0.569;
- inimigo: precisao 0.814, recall 0.593, mAP50 0.740, mAP50-95 0.241.

O player ficou forte no conjunto de validacao do mundo conhecido, enquanto a
classe inimigo ainda perde deteccoes e tem localizacao menos precisa. Em teste
ao vivo num mundo nao presente no treino, o baseline nao gerou deteccoes, o que
confirma que a validacao atual ainda nao mede generalizacao entre mundos.

Proxima iteracao: coletar duas sessoes independentes no novo mundo, usando uma
para treino e outra para validacao.
