# Roadmap

## v0.1 - Enxergar o personagem

- [x] localizar a janela do Idle Slayer;
- [x] capturar a janela em segundo plano;
- [x] coletar e rotular dataset;
- [x] treinar detector do player;
- [x] exportar ONNX;
- [x] executar deteccao ao vivo;
- [ ] validar estabilidade em corrida, pulo e ataque;
- [ ] registrar benchmark final;
- [ ] versionar o modelo ONNX final;
- [ ] integrar na main.

## v0.2 - Entender a tela

Classes candidatas:

- player;
- inimigo;
- moeda/gema;
- caixa;
- chave;
- obstaculo ou plataforma quando relevante.

Objetivo: transformar deteccoes em um estado simples e consultavel.

## v0.3 - Agir

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
