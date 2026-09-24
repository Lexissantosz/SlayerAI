# Modelo semantico e ciclo de feedback

O objetivo de longo prazo do SlayerAI nao e apenas detectar caixas na tela,
mas manter uma representacao simples do que esta acontecendo no jogo e usar
o resultado das proprias acoes como feedback.

## Ideia central

O fluxo desejado e:

```text
frame
  |
  v
percepcao visual
  |
  v
entidades + HUD + eventos
  |
  v
EstadoJogo semantico
  |
  v
decisao
  |
  v
acao
  |
  v
mudanca observada na tela
  |
  v
resultado / recompensa / falha
  |
  +----------> memoria do episodio
```

A IA nao precisa inferir tudo de forma livre desde o inicio. O primeiro
modelo semantico deve usar categorias e relacoes explicitas, para que cada
decisao continue observavel e depuravel.

## Entidades

Exemplos de entidades que podem aparecer na cena:

- player;
- inimigo;
- moeda;
- gema;
- chave;
- portal;
- caixa bonus;
- plataforma;
- chao;
- buraco;
- outros objetos especiais.

Cada entidade pode receber propriedades funcionais, por exemplo:

```text
inimigo -> atacar / atirar -> pode gerar almas e dinheiro
moeda   -> coletar
gema    -> coletar
chave   -> coletar -> pode ativar evento especial
portal  -> atravessar -> muda mundo/estado
buraco  -> evitar / pular
orb     -> coletar durante Bonus Stage
```

Essas propriedades representam "afordancias": o que o agente pode ou deve
fazer em relacao ao objeto.

## Eventos e causa/efeito

O SlayerAI deve observar sequencias, nao apenas frames isolados.

Exemplos:

```text
inimigo visivel
-> acao ATACAR
-> inimigo desaparece
-> contador de almas/dinheiro aumenta
-> evento: inimigo derrotado com recompensa
```

```text
moeda visivel
-> player cruza a moeda
-> moeda desaparece
-> valor no HUD aumenta
-> evento: moeda coletada
```

```text
buraco a frente
-> salto
-> player permanece em plataforma segura
-> evento: obstaculo evitado
```

Uma correlacao isolada nao prova causalidade. O sistema deve acumular
episodios repetidos antes de promover uma associacao para uma regra confiavel.

## Feedback visual

A interface do jogo tambem e uma fonte de estado. O sistema deve conseguir
observar regioes fixas ou dinamicas da UI para detectar:

- almas e dinheiro;
- contadores de itens;
- quantidade restante de orbs;
- tempo restante;
- mensagens de recompensa;
- telas de sucesso;
- telas de falha;
- conclusao de fase;
- mudanca de mundo;
- entrada e saida de minigames.

Nao e necessario ler a tela inteira com OCR em todo frame. O ideal e usar
regioes de interesse do HUD, deteccao de mudanca e leitura/classificacao
somente quando houver motivo.

## Estado semantico

Um estado futuro pode representar algo semelhante a:

```text
modo: NORMAL
player: localizado
ameaca_mais_proxima: inimigo
coletaveis: [moeda, gema]
portal_visivel: false
buraco_a_frente: false
almas: valor observado
dinheiro: valor observado
ultimo_evento: inimigo_derrotado
ultima_recompensa: almas aumentaram
```

No Bonus Stage:

```text
modo: BONUS
player: localizado
orbs_visiveis: [...]
orbs_restantes: 8
tempo_restante: estimado
buraco_a_frente: true
objetivo: coletar_orbs_sem_cair
```

## Aprendizado

A ordem recomendada e hibrida:

1. detectar entidades;
2. definir significados e regras basicas explicitamente;
3. observar resultados das acoes;
4. registrar episodios;
5. aprender associacoes e timing a partir dos episodios;
6. usar demonstracoes do usuario em situacoes raras;
7. considerar aprendizado por reforco apenas onde houver dados e tentativas
   suficientes.

Eventos raros como Bonus Stage nao devem depender inicialmente de tentativa
e erro. Uma politica segura baseada em regras pode ser refinada depois por
demonstracoes e historico real.

## Principio de seguranca

O sistema nunca deve concluir que uma acao e boa apenas porque ocorreu uma
vez antes de uma recompensa. Regras aprendidas precisam de repeticao,
consistencia e possibilidade de serem inspecionadas.

A estrategia e evoluir de "detectar objetos" para "entender estado, executar
acao e confirmar resultado" sem transformar o comportamento em uma caixa
preta impossivel de diagnosticar.


## Modo professor

Antes de exigir mais rotulagem manual, o projeto pode aprender com a forma
como o usuario joga. O script `src/gravar_demonstracao.py` observa as teclas
fisicas configuradas e salva automaticamente uma pequena janela visual antes,
durante e depois de cada acao.

Exemplo:

```powershell
python src/gravar_demonstracao.py
```

O modo professor nao envia comandos ao jogo. Ele apenas registra contexto
visual para eventos como pular, atacar e atirar. Esses episodios servem para:

- aprender quando uma acao costuma ser usada;
- comparar o estado antes e depois da acao;
- reduzir coleta manual de screenshots;
- construir posteriormente classificadores de comportamento;
- associar acoes com recompensas e resultados observados no HUD.

A prioridade passa a ser aprender a partir de jogo real e usar rotulagem
manual somente para corrigir ambiguidades que o sistema nao consegue resolver.
