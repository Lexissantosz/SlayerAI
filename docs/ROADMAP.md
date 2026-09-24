# Roadmap

## v0.1 - Enxergar o personagem

- [x] localizar a janela do Idle Slayer;
- [x] capturar a janela em segundo plano;
- [x] coletar e rotular dataset;
- [x] treinar detector do player;
- [x] exportar ONNX;
- [x] executar deteccao ao vivo;
- [x] validar estabilidade em corrida, pulo e ataque;
- [x] registrar benchmark final;
- [x] versionar o modelo ONNX final;
- [ ] integrar na main.

### Benchmark final da v0.1

Configuracao validada no PC de referencia:

- modelo: `modelos/player_v01.onnx`;
- imgsz: 320;
- confianca minima: 0.30;
- ROI: `0,0,0.30,1`;
- 100/100 frames detectados (100.0%);
- inferencia media: 175.3 ms;
- mediana: 90.6 ms;
- P95: 148.0 ms;
- confianca media: 0.822.

Observacao: o detector ainda pode perder o player por instantes em algumas
animacoes, tratado por memoria curta. A ROI e a ancora horizontal reduzem
falsas deteccoes em inimigos e moedas.

## v0.2 - Entender a tela

Preparacao ja iniciada:

- [x] Estado visual desacoplado do detector;
- [x] Tipos de objetos previstos no dominio;
- [x] Motor inicial de decisoes explicaveis;
- [x] Simulador offline das regras;
- [x] conectar deteccoes reais ao EstadoJogo;
- [ ] treinar classes alem do player;

Classes candidatas:

- player;
- inimigo;
- moeda/gema;
- caixa;
- chave;
- obstaculo ou plataforma quando relevante.

Objetivo: transformar deteccoes em um estado simples e consultavel.

## v0.3 - Agir

Preparacao ja iniciada:

- [x] dry-run seguro sem envio de teclas;
- [x] registro de sessoes em JSONL;
- [x] replay offline das decisoes;
- [x] executor por teclas desacoplado;
- [x] cooldown contra spam de acoes;
- [x] validar entrada real com o jogo;

- entrada em segundo plano;
- pulo;
- ataque;
- arco/flecha;
- regras de prioridade;
- mecanismos de seguranca para pausar a automacao.

## v0.4 - Jogar melhor

- coleta orientada a objetivos;
- Chest Hunt;
- Bonus Stage;
- registro de episodios;
- aprendizado a partir de demonstracoes e correcoes do usuario.

Ascensoes, compras e progresso estrategico continuam sob controle do
usuario ate existir uma camada separada e explicitamente testada.
