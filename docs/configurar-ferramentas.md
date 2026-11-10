# 🔧 Ferramentas grátis do canal

Fase atual: **custo zero**. Tudo roda no seu computador, sem chave e sem cobrança.

| Ferramenta | Para quê | Licença (pode monetizar?) | Instalação |
|---|---|---|---|
| **Kokoro-82M** | Voz da narração (PT-BR: `pm_alex`, `pm_santa`, `pf_dora`) | Apache 2.0 ✅ | `pip install -r scripts/narracao/requirements.txt` |
| **espeak-ng** | Pronúncia usada pelo Kokoro | GPL (só ferramenta) ✅ | Win: instalador `.msi` em github.com/espeak-ng/espeak-ng/releases · Mac: `brew install espeak-ng` · Linux: `apt install espeak-ng` |
| **faster-whisper** | Tempo de cada palavra → legendas | MIT ✅ | já no requirements |
| **FFmpeg** | Montagem e render do vídeo | LGPL/GPL ✅ | Win: `winget install Gyan.FFmpeg` |

Requisitos: Python 3.10–3.12. Com NVIDIA, instale o PyTorch com CUDA antes (pytorch.org → "Get Started") para ficar bem mais rápido.

## Testar a narração
```bash
python scripts/narracao/narrar.py producao/<pasta> --palavras
```
Saída: `audio/B01.wav…`, `audio/tempos.json`, `audio/Bxx.words.json`.

## ❌ Descartadas por licença ou custo
| Opção | Motivo |
|---|---|
| ElevenLabs (plano grátis) | Não permite uso comercial. Volta quando houver orçamento (o MCP continua no `.mcp.json`, sem chave ele só não liga). |
| XTTS-v2, F5-TTS | Pesos com licença **não comercial**. |
| Edge-TTS | Grátis, mas uso comercial das vozes da Microsoft não é garantido. |
| Replicate | Cobra por uso. |
