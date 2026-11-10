# Canal Dark IA — instruções para o GitHub Copilot

Projeto: canal dark no YouTube, conteúdos diversos, 100% feito com IA (voz ElevenLabs).
Agentes em `.github/agents/` (espelho de `agents/` do plugin Claude Code). Sempre comece pelo `gerente`.

Pipeline: pesquisador-pautas → roteirista → diretor-narracao → editor-video → especialista-thumbnail → especialista-youtube.
Cada vídeo em `producao/<AAAA-MM-DD>-<slug>/`. Idioma: português do Brasil.
Ao mudar um agente em `agents/`, atualize o espelho em `.github/agents/` no mesmo commit.

## Ferramentas (fase custo zero)
Narração grátis: `python scripts/narracao/narrar.py producao/<pasta> --palavras` (Kokoro, PT-BR). Instalação em `docs/configurar-ferramentas.md`. Não use serviço pago (ElevenLabs, Replicate) sem autorização do usuário.
