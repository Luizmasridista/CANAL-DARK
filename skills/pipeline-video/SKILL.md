---
name: pipeline-video
description: Use ao produzir um vídeo do canal do pedido até a publicação, para saber a ordem das etapas, a pasta de cada vídeo, o briefing padrão de cada agente e quando um passo está pronto. Usada pelo gerente.
---
# 🧭 Pipeline de um vídeo

## Ordem fixa
| # | Etapa | Agente | Entrada | Saída | Pronto quando |
|---|---|---|---|---|---|
| 1 | Pauta | pesquisador-pautas | tema ou "sugira" | `briefing.md` | 5 ideias ranqueadas, a escolhida com ≥3 fontes por fato |
| 2 | Roteiro | roteirista | `briefing.md` | `roteiro.md` | gancho ≤15 s, blocos `[Bxx]` com `[CENA]` e `[VOZ]`, tamanho bate com a duração |
| 3 | Checagem | revisor-qualidade | `roteiro.md` + `briefing.md` | `revisao.md` | todo fato com fonte, nada que fira as políticas (skill `politicas-youtube-ia`) |
| 4 | Narração | diretor-narracao | `roteiro.md` | `audio/Bxx.wav`, `audio/tempos.json` | um áudio por bloco, duração total ±10% da meta |
| 5 | Visual | diretor-arte | `roteiro.md` | `visual/` | uma imagem por `[CENA]`, no estilo de `canal/biblia-visual.md` |
| 6 | Edição | editor-video (+ sonoplasta) | áudio + visual | `final/video.mp4`, `final/legendas.srt` | render 1920x1080 30fps, áudio em -14 LUFS |
| 7 | Thumbnail | especialista-thumbnail | `roteiro.md` | `thumb/` | 3 variações 1280x720 |
| 8 | SEO | especialista-youtube | tudo acima | `seo.md` | título, descrição com capítulos, tags |
| 9 | Revisão final | revisor-qualidade | pasta inteira | `revisao.md` atualizado | checklist final ok |
| 10 | Publicar | **usuário** | — | — | aprovação explícita do usuário |

As etapas 5 e 7 podem rodar em paralelo com a 4.

## Pasta do vídeo
```
producao/<AAAA-MM-DD>-<slug>/
  briefing.md  roteiro.md  revisao.md  seo.md
  audio/  visual/  thumb/  final/
  custos.md   # fase atual: tudo R$ 0
```
Branch git: `producao/<AAAA-MM-DD>-<slug>`.

## Briefing padrão para cada agente
```
Objetivo: <uma frase>
Entrada: <arquivos>
Saída: <arquivo e formato>
Critério de pronto: <da tabela acima>
Limites: <duração, orçamento, o que NÃO fazer>
```

## Regras
- Revise cada entrega contra o critério de pronto. No máximo 2 devoluções; depois, leve ao usuário.
- Pergunte ao usuário só: tema (se não veio), duração, e aprovação antes de publicar.
- Fase custo zero: nenhum serviço pago (ElevenLabs, Replicate etc.) sem o "pode" do usuário. Registre em `custos.md`.
- Reporte final em tabela: etapa, agente, arquivo, status, custo.
