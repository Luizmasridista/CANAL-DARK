# Canal Dark IA — instruções para o GitHub Copilot

Projeto: canal dark no YouTube, conteúdos diversos, 100% feito com IA (voz ElevenLabs).
Agentes em `.github/agents/` (espelho de `agents/` do plugin Claude Code). Sempre comece pelo `gerente`.

Pipeline: pesquisador-pautas → roteirista → diretor-narracao → editor-video → especialista-thumbnail → especialista-youtube → editor-shorts → revisor-qualidade → (publica) → analista-metricas. Apoio: diretor-arte (identidade) e sonoplasta (trilha/SFX, junto da edição).
Cada vídeo em `producao/<AAAA-MM-DD>-<slug>/`. Idioma: português do Brasil.
Ao mudar um agente em `agents/`, atualize o espelho em `.github/agents/` no mesmo commit.

## Git
Siga `CONVENCAO-GIT.md`: uma branch por função (`agentes/<nome>`, `tools/<nome>`, `skills/<nome>`, `docs/<tema>`, `producao/<data>-<slug>`), PR e merge `--no-ff` na `main`. Nunca commitar direto na `main`.
