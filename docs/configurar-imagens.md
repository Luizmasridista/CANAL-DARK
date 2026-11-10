# 🎨 Imagens IA grátis no seu PC (RTX 3050)

Motor: **FLUX.1-schnell** (licença Apache 2.0 ✅ pode monetizar) rodando no **ComfyUI**, em versão "comprimida" (GGUF = o modelo em tamanho menor para caber na memória da placa).

## Instalação (uma vez)
1. Baixe o **ComfyUI Portable para Windows (NVIDIA)** em github.com/comfyanonymous/ComfyUI/releases e extraia.
2. Instale o **ComfyUI-Manager** e, por ele, o nó **ComfyUI-GGUF** (de city96). Reinicie.
3. Baixe os modelos (Hugging Face) para as pastas do ComfyUI:

| Arquivo | De onde | Pasta |
|---|---|---|
| `flux1-schnell-Q4_K_S.gguf` (~6,8 GB) | `city96/FLUX.1-schnell-gguf` | `models/unet/` |
| `t5-v1_1-xxl-encoder-Q4_K_M.gguf` (~3 GB) | `city96/t5-v1_1-xxl-encoder-gguf` | `models/clip/` |
| `clip_l.safetensors` | `comfyanonymous/flux_text_encoders` | `models/clip/` |
| `ae.safetensors` | `black-forest-labs/FLUX.1-schnell` | `models/vae/` |

## Qual versão da RTX 3050 você tem?
| Placa | Memória | O que usar | Tempo por imagem (aprox.) |
|---|---|---|---|
| 3050 desktop | 8 GB | `Q4_K_S` (padrão) | 20–40 s |
| 3050 notebook | 4–6 GB | `flux1-schnell-Q3_K_S.gguf` e abrir o ComfyUI com `--lowvram` | 1–2 min |

Veja a memória no Gerenciador de Tarefas → Desempenho → GPU → "Memória dedicada". Recomendado 16 GB+ de RAM no PC. Se trocar o arquivo, ajuste `MODELOS` no script.

## Usar
Com o ComfyUI aberto:
```bash
python scripts/imagens/gerar_imagem.py "farol abandonado à noite, neblina, estilo cinematográfico escuro" teste.png --formato 16:9
python scripts/imagens/gerar_imagem.py --lote producao/<pasta>/visual/prompts.json
```
O lote grava a `seed` (número que permite refazer a mesma imagem) de cada cena no próprio JSON, para registro de origem.

## Dicas
- FLUX entende prompt em inglês melhor que em português.
- Gere em 16:9 (1344x768) e o `edicao-ffmpeg` amplia no zoom; para Shorts use `--formato 9:16`.
- Sem PC ligado? Plano B grátis: fotos e vídeos de Pexels/Pixabay (licença livre, registrar link).
