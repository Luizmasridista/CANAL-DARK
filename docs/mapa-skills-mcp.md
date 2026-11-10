# 🗺️ Mapa de skills e conectores MCP por agente

> 💸 **Fase atual: custo zero** (decisão do usuário em 2026-11-10). Narração com **Kokoro** e imagens com **FLUX.1-schnell no ComfyUI** (RTX 3050), tudo local e grátis. ElevenLabs e Replicate ficam para quando houver orçamento.
>
> Status: **mapeamento** (nada implementado ainda). Cada item aqui vira depois uma branch própria (`skills/<nome>` ou `tools/<nome>`).
>
> **Glossário rápido**
> - **Skill** = um "manual de procedimento" que o agente lê antes de trabalhar (ex.: como montar um gancho de 15 s). Fica em `skills/<nome>/SKILL.md`.
> - **MCP** = uma "tomada" que liga o agente a um serviço externo (ex.: ElevenLabs para gerar a voz). Fica no `.mcp.json`.
> - **Prioridade**: 🔴 P0 = sem isso o primeiro vídeo não sai · 🟡 P1 = melhora qualidade/escala · 🟢 P2 = depois que o canal rodar.

---

## 1. Resumo por agente

| Agente | Skills a criar | MCP / ferramenta | Prioridade |
|---|---|---|---|
| 🧭 gerente | `pipeline-video` | GitHub (já existe) | 🔴 P0 |
| 🔎 pesquisador-pautas | `pesquisa-com-fontes`, `caca-de-pautas` | Busca web (WebSearch/WebFetch nativos) + Brave Search ou Exa | 🔴 P0 |
| ✍️ roteirista | `roteiro-retencao` | — (só texto) | 🔴 P0 |
| 🎙️ diretor-narracao | `narracao-ia` | **Kokoro** local (grátis) · ElevenLabs MCP no futuro | 🔴 P0 |
| 🎨 diretor-arte | `biblia-visual`, `prompts-imagem-ia` | Geração de imagem (ver §3) | 🔴 P0 |
| 🎬 editor-video | `edicao-ffmpeg`, `legendas-srt` | FFmpeg via Bash · banco de imagens (Pexels/Pixabay) | 🔴 P0 |
| 🔊 sonoplasta | `trilha-e-mixagem` | ElevenLabs (efeitos e música) · Splice | 🟡 P1 |
| 🖼️ especialista-thumbnail | `thumbnail-ctr` (+ usa `prompts-imagem-ia`) | Geração de imagem · Canva/Adobe para texto e recorte | 🔴 P0 |
| 📈 especialista-youtube | `seo-youtube` | YouTube Data API (MCP próprio, ver §3) | 🔴 P0 (texto) · 🟡 P1 (upload) |
| ✅ revisor-qualidade | `politicas-youtube-ia`, `checagem-de-fatos` | Busca web | 🔴 P0 |
| ✂️ editor-shorts | `cortes-shorts` | FFmpeg via Bash | 🟡 P1 |
| 📊 analista-metricas | `analise-metricas` | YouTube Analytics API (mesmo MCP próprio) | 🟡 P1 |

---

## 2. Skills (o "como fazer" de cada agente)

| # | Skill | Dono | O que ensina | Prioridade |
|---|---|---|---|---|
| 1 | `pipeline-video` | gerente | Ordem das etapas, pastas de `producao/<data>-<slug>/`, briefing padrão, critério de pronto por etapa, quando escalar ao usuário | 🔴 |
| 2 | `pesquisa-com-fontes` | pesquisador | Mínimo 3 fontes confiáveis por fato, registrar link + data, separar fato de lenda/teoria | 🔴 |
| 3 | `caca-de-pautas` | pesquisador | Achar temas com demanda (tendências, perguntas do público, concorrentes), nota de potencial (curiosidade × busca × concorrência) | 🟡 |
| 4 | `roteiro-retencao` | roteirista | Gancho nos primeiros 15 s, "loops abertos" (promessas que prendem até o fim), ritmo por bloco, marcações `[CENA]` e `[PAUSA]`, tamanho por duração (~150 palavras/min) | 🔴 |
| 5 | `narracao-ia` | diretor-narracao | Escolha e trava da voz do canal, ajustes (estabilidade, similaridade, estilo), pausas e ênfase, gerar por bloco, montar `audio/tempos.json` | 🔴 |
| 6 | `biblia-visual` | diretor-arte | Identidade fixa do canal: paleta, estilo de imagem, fontes, logotipo — para todo vídeo parecer do mesmo canal | 🔴 |
| 7 | `prompts-imagem-ia` | diretor-arte, editor, thumbnail | Modelo de prompt com estilo do canal, proporções (16:9, 9:16), o que evitar (mãos, texto na imagem, rostos reais) | 🔴 |
| 8 | `edicao-ffmpeg` | editor-video | Receitas prontas: imagem parada com zoom lento ("efeito Ken Burns"), juntar cenas, trilha por baixo da voz, volume padrão do YouTube (-14 LUFS), render 1080p 30fps | 🔴 |
| 9 | `legendas-srt` | editor-video | Gerar legenda sincronizada a partir dos tempos da narração; legenda "queimada" (fixa no vídeo) para Shorts | 🟡 |
| 10 | `trilha-e-mixagem` | sonoplasta | Clima por tipo de tema, "ducking" (música abaixa sozinha quando a voz fala), efeitos nos cortes, licença de cada som | 🟡 |
| 11 | `thumbnail-ctr` | thumbnail | Até 3 elementos, texto de no máximo 4 palavras, contraste alto, leitura em tela de celular, 3 variações para teste A/B | 🔴 |
| 12 | `seo-youtube` | especialista-youtube | Título (≤60 caracteres, palavra-chave no começo), descrição com capítulos, tags, horário de postagem, cartões e telas finais | 🔴 |
| 13 | `politicas-youtube-ia` | revisor-qualidade | ⚠️ Regras do YouTube para canal 100% IA: marcar "conteúdo alterado ou sintético" quando parecer real, política de "conteúdo inautêntico/repetitivo" (risco de perder monetização), direitos autorais de imagem e música | 🔴 |
| 14 | `checagem-de-fatos` | revisor-qualidade | Conferir cada afirmação do roteiro contra as fontes da pauta antes de narrar | 🔴 |
| 15 | `cortes-shorts` | editor-shorts | Achar os 2–3 melhores trechos, reenquadrar em 9:16, gancho no 1º segundo, legenda grande | 🟡 |
| 16 | `analise-metricas` | analista-metricas | Ler CTR (taxa de cliques na thumb), retenção, duração média, RPM (quanto rende por mil views) e devolver aprendizados ao pesquisador e ao roteirista | 🟡 |

> 💡 As skills 7 (`prompts-imagem-ia`) e 13 (`politicas-youtube-ia`) são compartilhadas: vários agentes leem a mesma.

---

## 3. Conectores MCP e ferramentas

| Necessidade | Recomendação | Alternativas | Precisa de chave? | Prioridade |
|---|---|---|---|---|
| 🎙️ Voz de narração | **Kokoro-82M** local (Apache 2.0, PT-BR) via `scripts/narracao/narrar.py` | ElevenLabs MCP (pago, já configurado) | Não | 🔴 |
| 🔎 Pesquisa | **WebSearch + WebFetch nativos** do Claude (já vêm) | Brave Search MCP (oficial da Brave) · Exa MCP · Firecrawl (ler sites inteiros) | Brave/Exa: sim | 🔴 |
| 🎨 Imagens IA (cenas e thumb) | **FLUX.1-schnell GGUF no ComfyUI** (local, Apache 2.0) via `scripts/imagens/gerar_imagem.py` | Replicate · Adobe Firefly · Canva (pagos) | Não | 🔴 |
| 🎬 Edição e render | **FFmpeg pela linha de comando** (agente usa Bash + receitas da skill `edicao-ffmpeg`) — mais estável que um MCP | MCPs de FFmpeg da comunidade (imaturos) | Não | 🔴 |
| 🖼️ Banco de imagens/vídeos livres | Pexels ou Pixabay API (montar MCP pequeno em `tools/`) | Adobe Stock (pago) | Sim (grátis) | 🟡 |
| 🔊 Efeitos e música | **Biblioteca de Áudio do YouTube** · Pixabay Music/SFX (grátis, uso comercial) | ElevenLabs · Splice (pagos) | Não | 🟡 |
| 📝 Legendas | **faster-whisper** local (MIT) | ElevenLabs Speech-to-Text | Não | 🟡 |
| 📺 YouTube (upload, metadados) | **MCP próprio** `tools/youtube-mcp` sobre a YouTube Data API v3 (login Google OAuth) | MCPs da comunidade (avaliar segurança antes) | OAuth Google | 🟡 |
| 📊 Métricas | Mesmo `youtube-mcp` + YouTube Analytics API | Exportar CSV do YouTube Studio | OAuth Google | 🟡 |
| 🎞️ Vídeo gerado por IA (b-roll em movimento) | Via Replicate/fal (Kling, Runway, Luma, Veo) | — | Sim (caro) | 🟢 |
| 🗂️ Calendário editorial | Notion ou Google Drive (conectores do claude.ai) | Planilha no repo | — | 🟢 |
| 🔧 Versionamento | GitHub (já em uso) | — | — | 🔴 |

### ⚠️ Pontos de atenção
1. **Conectores do claude.ai ≠ MCP do plugin.** Adobe, Canva, Figma, Splice, Notion e Drive já estão ligados na sua conta do claude.ai, mas só funcionam dentro do app do Claude. Para o plugin e o GitHub Copilot usarem, o serviço precisa estar no `.mcp.json` (com chave própria).
2. **Um gerador de imagem só.** Misturar ferramentas quebra a identidade visual do canal.
3. **Chaves nunca no repositório.** Sempre `${NOME_DA_CHAVE}` no `.mcp.json`, valor fica na máquina/segredo do GitHub.
4. **Upload no YouTube sempre com aprovação humana** (publicar não tem volta).

---

## 4. Ordem sugerida de implementação

| Onda | O que entra | Branches |
|---|---|---|
| 1️⃣ Primeiro vídeo | `pipeline-video`, `pesquisa-com-fontes`, `roteiro-retencao`, `narracao-ia`, `edicao-ffmpeg`, `politicas-youtube-ia` + narração e imagem locais | `skills/<nome>` (1 por skill) · `tools/narracao-kokoro` · `tools/imagem-local` |
| 2️⃣ Cara de canal | `biblia-visual`, `prompts-imagem-ia`, `thumbnail-ctr`, `seo-youtube`, `checagem-de-fatos` | `skills/<nome>` |
| 3️⃣ Escala | `trilha-e-mixagem`, `legendas-srt`, `cortes-shorts`, MCP Pexels, `tools/youtube-mcp` | `skills/<nome>` · `tools/<nome>` |
| 4️⃣ Aprender com dados | `analise-metricas`, `caca-de-pautas`, vídeo IA, calendário | `skills/<nome>` · `tools/<nome>` |

> Toda skill criada em `skills/<nome>/SKILL.md` ganha espelho para o Copilot em `.github/skills/<nome>/SKILL.md` no mesmo commit.
