"""Narração grátis com Kokoro (Apache 2.0) a partir do roteiro.md do canal.

Uso:
  python scripts/narracao/narrar.py producao/<pasta> [--voz pm_alex] [--velocidade 0.95] [--palavras]

Gera audio/Bxx.wav, audio/tempos.json e, com --palavras, audio/Bxx.words.json
(tempo de cada palavra via faster-whisper, para as legendas).
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf

TAXA = 24000  # Kokoro gera áudio em 24 kHz
BLOCO = re.compile(r"^## \[(B\d+)\][^\n]*\n(.*?)(?=^## \[B\d+\]|\Z)", re.S | re.M)
PAUSA = re.compile(r"pausa_final=([\d.]+)s")


def texto_falado(corpo: str) -> str:
    corpo = re.sub(r"<!--.*?-->", "", corpo, flags=re.S)
    corpo = re.sub(r"^\[(CENA|VOZ)[^\]]*\]\s*$", "", corpo, flags=re.M)
    corpo = re.sub(r"\{\{[^|}]+\|([^}]+)\}\}", r"\1", corpo)  # {{grafia|pronúncia}}
    return " ".join(corpo.split())


def ler_voz() -> dict:
    cfg = Path("canal/voz.md")
    voz = {"voz": "pm_alex", "velocidade": 0.95}
    if cfg.exists():
        for linha in cfg.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(voz|velocidade):\s*([\w.]+)", linha)
            if m:
                voz[m[1]] = float(m[2]) if m[1] == "velocidade" else m[2]
    return voz


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta", type=Path)
    ap.add_argument("--voz")
    ap.add_argument("--velocidade", type=float)
    ap.add_argument("--palavras", action="store_true", help="gera tempo por palavra para legenda")
    a = ap.parse_args()

    from kokoro import KPipeline

    cfg = ler_voz()
    voz = a.voz or cfg["voz"]
    vel = a.velocidade or cfg["velocidade"]
    roteiro = (a.pasta / "roteiro.md").read_text(encoding="utf-8")
    saida = a.pasta / "audio"
    saida.mkdir(exist_ok=True)

    pipe = KPipeline(lang_code="p")  # p = português do Brasil
    tempos, inicio = [], 0.0
    for bid, corpo in BLOCO.findall(roteiro):
        texto = texto_falado(corpo)
        if not texto:
            continue
        audio = np.concatenate([np.asarray(aud) for _, _, aud in pipe(texto, voice=voz, speed=vel)])
        m = PAUSA.search(corpo)
        if m:
            audio = np.concatenate([audio, np.zeros(int(float(m[1]) * TAXA), dtype=audio.dtype)])
        arq = saida / f"{bid}.wav"
        sf.write(arq, audio, TAXA)
        dur = len(audio) / TAXA
        tempos.append({"id": bid, "arquivo": arq.name, "inicio_s": round(inicio, 3), "duracao_s": round(dur, 3)})
        inicio += dur
        print(f"{bid}: {dur:.1f}s")

    (saida / "tempos.json").write_text(
        json.dumps({"motor": "kokoro", "voz": voz, "velocidade": vel, "total_s": round(inicio, 3), "blocos": tempos},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    if a.palavras:
        from faster_whisper import WhisperModel
        modelo = WhisperModel("small", device="auto", compute_type="int8")
        for b in tempos:
            segs, _ = modelo.transcribe(str(saida / b["arquivo"]), language="pt", word_timestamps=True)
            palavras = [{"p": w.word.strip(), "ini": round(w.start, 2), "fim": round(w.end, 2)}
                        for s in segs for w in s.words]
            (saida / f"{b['id']}.words.json").write_text(json.dumps(palavras, ensure_ascii=False), encoding="utf-8")

    print(f"Total: {inicio/60:.1f} min -> {saida}/tempos.json")


if __name__ == "__main__":
    main()
