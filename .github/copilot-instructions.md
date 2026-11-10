# Canal Dark IA — instruções para o GitHub Copilot

Projeto: canal dark no YouTube, conteúdos diversos, 100% feito com IA (voz ElevenLabs).
Agentes em `.github/agents/` (espelho de `agents/` do plugin Claude Code). Sempre comece pelo `gerente`.

Pipeline: pesquisador-pautas → roteirista → diretor-narracao → editor-video → especialista-thumbnail → especialista-youtube.
Cada vídeo em `producao/<AAAA-MM-DD>-<slug>/`. Idioma: português do Brasil.
Ao mudar um agente em `agents/`, atualize o espelho em `.github/agents/` no mesmo commit.

## Imagens (fase custo zero)
Imagens IA grátis no PC do usuário (RTX 3050): `python scripts/imagens/gerar_imagem.py` via ComfyUI + FLUX.1-schnell GGUF. Instalação em `docs/configurar-imagens.md`.
