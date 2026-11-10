# Canal Dark IA — instruções para o GitHub Copilot

Projeto: canal dark no YouTube, conteúdos diversos, 100% feito com IA (voz ElevenLabs).
Agentes em `.github/agents/` (espelho de `agents/` do plugin Claude Code). Sempre comece pelo `gerente`.

Pipeline: pesquisador-pautas → roteirista → diretor-narracao → editor-video → especialista-thumbnail → especialista-youtube.
Cada vídeo em `producao/<AAAA-MM-DD>-<slug>/`. Idioma: português do Brasil.
Ao mudar um agente em `agents/`, atualize o espelho em `.github/agents/` no mesmo commit.

Qualidade técnica: o agente `qualidade-producao` roda os quality gates (`scripts/qualidade/gates.py`, skill `gates-qualidade`) depois de cada etapa e devolve `qualidade/correcoes.md` ao gerente. Fatos, políticas e direitos continuam com o `revisor-qualidade`.
