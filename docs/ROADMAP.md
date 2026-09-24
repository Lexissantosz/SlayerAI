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
- Bonus Stage como modo separado;
- registro de episodios;
- aprendizado a partir de demonstracoes e correcoes do usuario.

### Bonus Stage

A fase bonus muda o objetivo do agente e deve ser tratada como um estado
separado do jogo normal.

Fluxo planejado:

1. detectar a caixa roxa no modo normal;
2. reconhecer a transicao para a fase bonus;
3. alternar o modo global de NORMAL para BONUS;
4. detectar plataformas, buracos e orbs azuis;
5. acompanhar quantidade restante de orbs e limite de tempo;
6. executar uma politica de salto especifica para evitar quedas e coletar
   orbs;
7. detectar sucesso, falha ou saida e retornar ao modo NORMAL;
8. registrar o episodio completo para analise posterior.

A primeira implementacao sera explicita e baseada em regras/maquina de
estados. Como a fase bonus e relativamente rara, aprendizado por tentativa
e erro desde o inicio teria poucas oportunidades de treinamento e desperdicaria
eventos valiosos. Demonstracoes do usuario podem ser registradas depois para
melhorar timing, rota e decisoes sem substituir a politica segura inicial.

Ascensoes, compras e progresso estrategico continuam sob controle do
usuario ate existir uma camada separada e explicitamente testada.
