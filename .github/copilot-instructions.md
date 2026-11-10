# Canal Dark IA — instruções para o GitHub Copilot

Projeto: canal dark no YouTube, conteúdos diversos, 100% feito com IA (voz ElevenLabs).
Agentes em `.github/agents/` (espelho de `agents/` do plugin Claude Code). Sempre comece pelo `gerente`.

Pipeline: pesquisador-pautas → roteirista → diretor-narracao → editor-video → especialista-thumbnail → especialista-youtube.
Cada vídeo em `producao/<AAAA-MM-DD>-<slug>/`. Idioma: português do Brasil.
Ao mudar um agente em `agents/`, atualize o espelho em `.github/agents/` no mesmo commit.

## Skills e MCPs planejados
Mapa priorizado de skills e conectores MCP por agente: `docs/mapa-skills-mcp.md`. Consulte antes de criar skill (`skills/<nome>/SKILL.md`, espelho em `.github/skills/`) ou MCP (`.mcp.json`, chaves sempre via `${VAR}`).
