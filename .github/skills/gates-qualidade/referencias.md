# 📚 De onde vêm os limites

"Heurística" = número de partida, sem norma oficial; calibrar com a baseline do canal depois dos primeiros vídeos.

## Legenda
| Limite | Valor | Fonte |
|---|---|---|
| Caracteres por linha / linhas | 42 / 2 | [Netflix, Brazilian Portuguese Timed Text Style Guide](https://partnerhelp.netflixstudios.com/hc/en-us/articles/215600497-Portuguese-Brazil-Timed-Text-Style-Guide) |
| Velocidade de leitura | ≤ 17 caracteres/s (adulto); 20 = teto (legenda para surdos, SDH) | mesmo guia Netflix PT-BR |
| Duração | mín. 5/6 s (0,833), máx. 7 s | [Netflix, Timed Text Style Guide: General Requirements](https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617) |
| Quebra de linha | depois de pontuação, antes de conjunção/preposição; não separar artigo+nome, nome+sobrenome | guia Netflix PT-BR |
| Intervalo 2 quadros, sincronia ≤ 0,3 s | 0,067 s / 0,3 s | heurística (a Netflix removeu a regra de intervalo em 2020) |

## Áudio e voz
| Limite | Valor | Fonte |
|---|---|---|
| Volume final do vídeo | -14 LUFS integrado | referência de normalização do YouTube medida pelo mercado (não é documento oficial do Google); ver [Production Advice sobre AES TD1008](https://productionadvice.co.uk/td1008/) e [Audio normalization](https://en.wikipedia.org/wiki/Audio_normalization) |
| Pico real (true peak) | ≤ -1 dBTP | margem usual de streaming (EBU R128 / AES) |
| Voz isolada: RMS, pico, ruído | -23 a -18 dB, ≤ -3 dB, ≤ -60 dB | [ACX Audio Submission Requirements](https://webcf.waybackmachine.org/web/20210510175948/https://www.acx.com/help/acx-audio-submission-requirements/201456300) (audiolivros; a ACX proíbe TTS, usamos só como régua de "voz limpa") |
| Velocidade da fala | 130–175 palavras/min (alvo 150) | audiolivros em inglês ficam em ~150–160 wpm ([referência](https://thespeakerlab.com/blog/average-words-per-minute-speaking/)); fala espontânea em PT-BR medida em ~90 palavras/min e ~170 sílabas/min ([CoDAS/SciELO](https://scielo.br/j/codas/a/sTGZRHGzpSkLwLS6fZCyVLc/?lang=en)). Narração lida é mais rápida que fala espontânea: **heurística**, calibrar pela voz escolhida |
| Consistência entre blocos | variação ≤ 12% | heurística (ACX pede "nível, tom e ritmo consistentes") |
| Inteligibilidade (WER) | aviso > 4%, falha > 8% | heurística; Whisper como "ouvinte" automático |
| Naturalidade (UTMOS) | aviso < 3,5, falha < 3,0 | [SpeechMOS/UTMOS (MIT)](https://github.com/tarepan/SpeechMOS). Treinado em inglês: em PT-BR, use **mais para comparar com a baseline** do que como nota absoluta |

## Roteiro, edição e retenção
| Limite | Valor | Fonte |
|---|---|---|
| Os 30 s iniciais | métrica oficial "intro" na retenção; melhora com título/thumb fiéis e abertura testada | [YouTube Help: key moments for audience retention](https://support.google.com/youtube/answer/9314415?hl=en) |
| Quedas (dips) e picos | trechos pulados viram caso de regressão | mesmo artigo do YouTube |
| Gancho ≤ 15 s, 150 palavras/min, [CENA] a cada 3–6 s | skill `roteiro-retencao` do canal | interno |
| Plano ≤ 10 s, ritmo do gancho ≤ 6 s/plano | heurística a partir da troca de 3–6 s da skill `edicao-ffmpeg` |
| Similaridade com roteiros anteriores | aviso > 0,30 (trigramas) | risco da política de **conteúdo inautêntico** (jul/2025): "histórias com diferenças superficiais" e "slideshows com a mesma narração" ([Social Media Today](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/)) |
| Thumbnail | 1280x720, ≤ 2 MB | Ajuda do YouTube (miniaturas personalizadas) |
| Shorts | 1080x1920, ≤ 3 min | formato vertical do YouTube Shorts |
