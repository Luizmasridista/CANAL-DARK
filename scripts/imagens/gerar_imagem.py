"""Gera imagem grátis no seu PC com FLUX.1-schnell (Apache 2.0) via ComfyUI.

Pré-requisito: ComfyUI aberto (http://127.0.0.1:8188) com o nó ComfyUI-GGUF e os modelos
de docs/configurar-imagens.md.

Uso:
  python scripts/imagens/gerar_imagem.py "prompt" saida.png [--formato 16:9|9:16|thumb] [--seed 42]
  python scripts/imagens/gerar_imagem.py --lote producao/<pasta>/visual/prompts.json
     (lista de {"arquivo": "c001.png", "prompt": "...", "formato": "16:9", "seed": 1})
"""
import argparse
import json
import random
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVIDOR = "http://127.0.0.1:8188"
FORMATOS = {"16:9": (1344, 768), "9:16": (768, 1344), "thumb": (1280, 720), "1:1": (1024, 1024)}
MODELOS = {
    "unet": "flux1-schnell-Q4_K_S.gguf",
    "t5": "t5-v1_1-xxl-encoder-Q4_K_M.gguf",
    "clip_l": "clip_l.safetensors",
    "vae": "ae.safetensors",
}


def fluxo(prompt: str, w: int, h: int, seed: int) -> dict:
    return {
        "1": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": MODELOS["unet"]}},
        "2": {"class_type": "DualCLIPLoaderGGUF",
              "inputs": {"clip_name1": MODELOS["t5"], "clip_name2": MODELOS["clip_l"], "type": "flux"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": MODELOS["vae"]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "7": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0],
                         "seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler",
                         "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "canal"}},
    }


def chamar(caminho: str, dados: dict | None = None) -> bytes:
    req = urllib.request.Request(SERVIDOR + caminho, data=json.dumps(dados).encode() if dados else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def gerar(prompt: str, saida: Path, formato: str = "16:9", seed: int | None = None) -> int:
    w, h = FORMATOS[formato]
    seed = random.randint(0, 2**32 - 1) if seed is None else seed
    pid = json.loads(chamar("/prompt", {"prompt": fluxo(prompt, w, h, seed)}))["prompt_id"]
    while True:
        hist = json.loads(chamar(f"/history/{pid}"))
        if pid in hist:
            break
        time.sleep(1.5)
    img = hist[pid]["outputs"]["9"]["images"][0]
    q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": "output"})
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_bytes(chamar(f"/view?{q}"))
    if formato == "thumb":  # FLUX gera em múltiplos de 16; redimensiona para 1280x720 exato
        import subprocess
        tmp = saida.with_suffix(".tmp.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(saida), "-vf", "scale=1280:720", str(tmp)], check=True)
        tmp.replace(saida)
    print(f"{saida}  seed={seed}")
    return seed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="?")
    ap.add_argument("saida", nargs="?", type=Path)
    ap.add_argument("--formato", default="16:9", choices=FORMATOS)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--lote", type=Path)
    a = ap.parse_args()
    if a.lote:
        itens = json.loads(a.lote.read_text(encoding="utf-8"))
        for it in itens:
            it["seed"] = gerar(it["prompt"], a.lote.parent / it["arquivo"], it.get("formato", "16:9"), it.get("seed"))
        a.lote.write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding="utf-8")  # guarda seeds
    else:
        gerar(a.prompt, a.saida, a.formato, a.seed)


if __name__ == "__main__":
    main()
