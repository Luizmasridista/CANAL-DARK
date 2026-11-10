---
name: politicas-youtube-ia
description: Use antes de narrar e antes de publicar um vídeo do canal, para checar as regras do YouTube que pesam sobre um canal feito com IA (marcação de conteúdo sintético, conteúdo inautêntico ou repetitivo, direitos autorais, temas sensíveis) e não perder alcance nem monetização. Usada pelo revisor-qualidade, roteirista e gerente.
---
# ✅ Políticas do YouTube para canal 100% IA

> As regras mudam. Antes de cada publicação importante, confira as páginas oficiais (links no fim) com `WebFetch` e atualize esta skill se algo mudou.

## 1. Marcação de "conteúdo alterado ou sintético"
No upload, o YouTube pede para marcar quando o vídeo tem conteúdo realista feito ou alterado por IA que alguém pode confundir com real.
- **Marcar SIM** quando: imagem/vídeo IA realista de pessoa real, lugar real ou evento real que parece filmagem; voz IA imitando pessoa real.
- **Não precisa** quando: arte claramente ilustrada/estilizada, narração IA que não imita ninguém (ex.: Kokoro), efeitos óbvios.
- Na dúvida, **marque**. Não marcar pode gerar remoção ou suspensão do Programa de Parcerias.

## 2. Conteúdo inautêntico / repetitivo (o maior risco de monetização)
O YouTube não paga canal que parece produção em massa sem valor próprio. Para ficar seguro:
- Cada vídeo com **roteiro original** e pesquisa própria (skill `pesquisa-com-fontes`), não texto reaproveitado.
- Variar estrutura, abertura e visual entre vídeos; nada de modelo idêntico trocando só o tema.
- Narrativa, opinião e conexão de fatos = valor adicionado. Lista lida por robô = risco.
- Não republicar o mesmo conteúdo em vários vídeos ou canais.

## 3. Direitos autorais
- Imagens: geradas por IA com modelo de licença comercial, como FLUX.1-schnell (registre modelo, prompt e seed), ou banco livre como Pexels/Pixabay (registre link).
- Música e efeitos: Biblioteca de Áudio do YouTube, Pixabay Music ou outra com licença comercial; guarde a licença em `edicao.md`.
- Proibido: trechos de filmes, séries, outros canais, música comercial, logos de marcas como destaque.

## 4. Temas sensíveis
- Pessoas reais vivas: só fatos com fonte, sem acusação; não gerar imagem realista delas.
- Crimes e tragédias: sem violência gráfica, respeito às vítimas, nada de glorificar. Thumbnail sem sangue/cadáver.
- Saúde, eleições, ciência: nada que contradiga consenso sem deixar claro que é teoria.
- Thumbnail e título não podem prometer o que o vídeo não mostra (clickbait enganoso).

## Checklist do revisor (`revisao.md`)
- [ ] Precisa marcar conteúdo sintético? (sim/não + motivo)
- [ ] Roteiro original e com valor próprio?
- [ ] Origem e licença de toda imagem e áudio registradas?
- [ ] Nenhum tema sensível tratado de forma proibida?
- [ ] Título e thumbnail fiéis ao conteúdo?
- Veredito: ✅ liberar · ⚠️ liberar com ajuste · ⛔ bloquear (com motivo)

## Páginas oficiais
- Divulgação de conteúdo alterado ou sintético: https://support.google.com/youtube/answer/14328491
- Políticas de monetização do YouTube: https://support.google.com/youtube/answer/1311392
- Diretrizes da comunidade: https://www.youtube.com/howyoutubeworks/policies/community-guidelines/
