# Convenção de Git do CANAL-DARK

Toda mudança nasce numa branch própria, separada por função, vira PR e só então é mesclada na `main`.
Nunca commitar direto na `main`.

## Branches (prefixo = tipo de mudança)

| Prefixo | Quando usar | Exemplo |
|---|---|---|
| `agentes/<nome>` | Criar ou alterar um agente (1 agente por branch) | `agentes/roteirista` |
| `tools/<nome>` | MCP, `.mcp.json`, scripts e ferramentas | `tools/elevenlabs-mcp` |
| `skills/<nome>` | Criar ou alterar uma skill | `skills/pipeline-video` |
| `docs/<tema>` | README, convenções, instruções do Copilot | `docs/convencao-git` |
| `producao/<data>-<slug>` | Arquivos de um vídeo | `producao/2026-11-10-triangulo-bermudas` |
| `fix/<tema>` | Correção pontual | `fix/plugin-json` |

## Regras
1. Uma branch = um assunto. Não misturar agente com tool ou skill.
2. Mudou `agents/<nome>.md`? Atualize `.github/agents/<nome>.agent.md` **no mesmo commit** (espelho do Copilot).
3. Mensagem de commit: `<tipo>(<escopo>): <resumo>` — ex.: `feat(roteirista): adiciona loops abertos`. Tipos: feat, fix, docs, refactor, chore.
4. PR com título igual ao commit principal e descrição do que mudou e por quê.
5. Merge na `main` com `--no-ff` (mantém o histórico da branch visível) e apaga a branch depois.
6. Commits só no nome do autor do projeto, sem trailer de co-autoria de IA.
