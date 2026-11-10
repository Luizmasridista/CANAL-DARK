---
name: gates-qualidade
description: Use ao checar a qualidade técnica de qualquer entrega da produção (roteiro, narração, legenda, edição, Shorts, thumbnail) com quality gates medidos, regressão contra os vídeos já aprovados e preview para olhar e ouvir, e ao montar a lista de correções por agente. Usada pelo qualidade-producao.
---
# 🚦 Quality gates de produção

**Quality gate** = um portão: a entrega só passa para a próxima etapa se as medições ficarem dentro dos limites.
Os limites ficam em `scripts/qualidade/limites.json`; a fonte de cada número está em [referencias.md](referencias.md).

## Os 3 tipos de gate
| Tipo | Explicação simples | Como roda |
|---|---|---|
| **Medição** | número contra limite (volume, velocidade da fala, letras por segundo na legenda) | `gates.py <gate> <pasta>` |
| **Regressão** | "não pode piorar": compara com a média dos vídeos já aprovados (baseline) e com os erros que já escaparam antes (casos) | automático em todo gate |
| **Visual/auditivo** | olhar quadros e ouvir trechos, em tamanho de TV e de celular | `gates.py preview <pasta>` + ler os PNGs |

## Quando rodar (gate de cada etapa)
| Depois de | Comando | Dono se falhar |
|---|---|---|
| roteiro | `python scripts/qualidade/gates.py roteiro producao/<pasta>` | roteirista |
| narração | `... voz producao/<pasta> --transcrever` (+ `--mos` se tiver torch) | diretor-narracao |
| edição | `... legenda producao/<pasta>` e `... edicao producao/<pasta>` | editor-video / sonoplasta |
| antes do revisor final | `... todos producao/<pasta> --transcrever` + `... preview producao/<pasta>` | cada dono |

Saída em `producao/<pasta>/qualidade/`: `relatorio.md` (tabela), `relatorio.json` (máquina), `correcoes.md` (por agente).
Código de saída 1 = **REPROVADO** (há ❌). Avisos (⚠️) não travam, mas vão para o dono corrigir ou justificar.

## O que cada gate mede
**Roteiro**: palavras vs duração meta (±10% a 150 palavras/min), gancho ≤ 15 s, sem "olá, pessoal / neste vídeo" no gancho, frase ≤ 25 palavras (TTS fica robótico em frase longa), `[CENA]` a cada ≤ 20 palavras, nada com ⚠️, similaridade com roteiros anteriores (risco de "conteúdo inautêntico" do YouTube).

**Voz**: palavras/min por bloco (130–175), consistência entre blocos (variação ≤ 12%), estouro (clipping), pico ≤ -3 dB, volume médio -23 a -18 dB, ruído ≤ -60 dB, pausa estranha > 1,2 s no meio da frase, **inteligibilidade** (o Whisper transcreve o áudio de volta e compara com o roteiro: WER = % de palavras erradas; > 8% reprova e lista as palavras para corrigir com `{{grafia|pronúncia}}`), **naturalidade** (UTMOS, nota 1–5 prevista por IA).

**Legenda**: ≤ 42 caracteres por linha, ≤ 2 linhas, leitura ≤ 17 caracteres/s (> 20 reprova), duração 0,83–7 s, sem sobreposição, sincronia com a fala ≤ 0,3 s (pelos `words.json`).

**Edição**: 1920x1080 30 fps H.264 yuv420p AAC (Shorts 1080x1920, ≤ 3 min), imagem e som com a mesma duração, -14 LUFS ±1, pico real ≤ -1 dBTP, tela preta > 0,5 s, imagem congelada > 4 s (faltou zoom lento), silêncio > 2 s na mixagem, plano mais longo ≤ 10 s, ritmo nos 30 s iniciais ≤ 6 s por plano, duração vs meta.

**Thumbnail**: 1280x720 e ≤ 2 MB.

## Preview (visualização e audição)
`gates.py preview` gera em `qualidade/preview/`:
- `contato.png` (20 quadros do vídeo todo) e `gancho.png` (1 quadro a cada 2 s dos 30 s iniciais): **abra com Read e olhe**: imagem repetida, fora do estilo, texto ilegível, tela preta.
- `celular.png`, `*_zona_segura.png` (Shorts com as faixas cobertas pela interface em vermelho) e `*_pequena.png` (thumbnail no tamanho da lista do YouTube): teste "responsivo", ou seja, se funciona em tela pequena.
- `onda.png` (forma de onda: buracos e estouros) e `gancho_30s.mp3`.
- Em tempo real, o usuário assiste e ouve com `ffplay` (comando no `LEIA.md`). O agente não ouve: usa transcrição, métricas e a onda.

## Regressão: o canal só melhora
1. Primeiro vídeo aprovado pelo **usuário** → `gates.py aprovar-baseline producao/<pasta>` grava `canal/qualidade/baseline.json`.
2. Todo vídeo novo é comparado a ela (tolerâncias em `limites.json > regressao`). Piorou além da tolerância = ❌.
3. **Erro que escapou vira caso**: quando o usuário ou o `analista-metricas` achar um problema (ex.: queda de retenção aos 0:20 por gancho lento), registre em `canal/qualidade/casos.json`:
```json
[{"id": "gancho-lento", "metrica": "edicao.plano_medio_gancho_s", "max": 4.0,
  "origem": "2026-11-20-farol: queda de 35% aos 0:20", "dono": "editor-video",
  "correcao": "Trocar imagem a cada 2–4 s no gancho."}]
```
4. Mudou um script de gate → rode `python -m pytest scripts/qualidade/tests -q` (testes dos próprios gates com mídia sintética).

## Devolver correções
- Entregue ao `gerente` o `correcoes.md`: uma seção por agente dono, com item, onde (bloco/tempo), valor, limite e o que fazer.
- O gerente repassa; o dono corrige; o gate roda de novo. **Máximo 2 rodadas**, depois o gerente leva ao usuário.
- Limite que parece errado para o canal? Não afrouxe sozinho: proponha a mudança no `limites.json` com o motivo (em branch `tools/gates-qualidade`).

## Fronteira com o revisor-qualidade
| qualidade-producao (esta skill) | revisor-qualidade |
|---|---|
| técnico e medido: voz, legenda, edição, ritmo, formato | editorial: fatos e fontes, políticas do YouTube, direitos/licenças, coerência título-thumb-vídeo |
| roda em cada etapa e no fim | roda após o roteiro e no fim |
O vídeo só vai ao usuário com **os dois** aprovados.
