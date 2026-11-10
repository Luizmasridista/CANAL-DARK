"""Testes de regressão dos próprios gates: mídia sintética gerada pelo FFmpeg (sem rede, sem GPU).

Rodar: python -m pytest scripts/qualidade/tests -q
Regra: todo defeito real que escapou vira um caso aqui (o gate precisa pegar de novo).
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gates  # noqa: E402

tem_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg ausente")


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def status(rel, item):
    return [i["status"] for i in rel.itens if i["item"] == item]


ROTEIRO = """---
duracao_meta: 0.1
---
## [B01] Gancho
[CENA: farol à noite]
[VOZ: tom=suspense, pausa_final=0.5s]
Em mil e novecentos, três homens sumiram de um farol. Ninguém sabe por quê.
"""


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "producao" / "2026-11-10-teste"
    for d in ("audio", "final", "shorts", "thumb"):
        (p / d).mkdir(parents=True)
    (p / "roteiro.md").write_text(ROTEIRO, encoding="utf-8")
    return p


# ---------- funções puras ----------
def test_wer_identico_e_troca():
    assert gates.wer("três homens sumiram", "Três homens sumiram.")[0] == 0
    taxa, faltando = gates.wer("três homens sumiram", "três homem sumiram")
    assert round(taxa, 2) == 0.33 and faltando == ["homens"]


def test_planos():
    assert gates.planos([3.0, 9.0], 12.0) == [(0.0, 3.0), (3.0, 6.0), (9.0, 3.0)]


def test_roteiro_bom(pasta):
    rel = gates.Relatorio()
    gates.gate_roteiro(pasta, rel)
    assert "FALHOU" not in {i["status"] for i in rel.itens}


def test_roteiro_ruim(pasta):
    (pasta / "roteiro.md").write_text(
        "## [B01] Gancho\nOlá, pessoal, neste vídeo " + "palavra " * 60 + "⚠️\n", encoding="utf-8")
    rel = gates.Relatorio()
    gates.gate_roteiro(pasta, rel)
    assert status(rel, "marcações [CENA]/[VOZ]") == ["FALHOU"]
    assert status(rel, "fato sem confirmação (⚠️)") == ["FALHOU"]
    assert "AVISO" in status(rel, "abertura genérica no gancho")
    assert status(rel, "frases longas (>25 palavras)") == ["AVISO"]


def test_roteiro_repetido(pasta):
    outro = pasta.parent / "2026-11-01-antigo"
    outro.mkdir()
    (outro / "roteiro.md").write_text(ROTEIRO, encoding="utf-8")
    rel = gates.Relatorio()
    gates.gate_roteiro(pasta, rel)
    assert status(rel, "similaridade com vídeo anterior") == ["FALHOU"]


def srt(pasta, texto):
    (pasta / "final" / "legendas.srt").write_text(texto, encoding="utf-8")


def test_legenda_boa(pasta):
    srt(pasta, "1\n00:00:00,000 --> 00:00:02,500\nEm mil e novecentos,\n\n"
               "2\n00:00:02,500 --> 00:00:05,000\ntrês homens sumiram.\n")
    rel = gates.Relatorio()
    gates.gate_legenda(pasta, rel)
    assert "FALHOU" not in {i["status"] for i in rel.itens}


def test_legenda_ruim(pasta):
    srt(pasta, "1\n00:00:00,000 --> 00:00:01,000\n" + "x" * 50 + "\nb\nc\n\n"
               "2\n00:00:00,800 --> 00:00:09,000\nok\n")
    rel = gates.Relatorio()
    gates.gate_legenda(pasta, rel)
    assert status(rel, "linhas por legenda") == ["FALHOU"]
    assert status(rel, "caracteres por linha") == ["FALHOU"]
    assert status(rel, "velocidade de leitura (CPS)") == ["FALHOU"]
    assert status(rel, "legendas sobrepostas") == ["FALHOU"]
    assert status(rel, "duração da legenda") == ["AVISO"]


def test_legenda_fora_de_sincronia(pasta):
    srt(pasta, "1\n00:00:01,000 --> 00:00:03,000\nEm mil e novecentos\n")
    (pasta / "audio" / "tempos.json").write_text(json.dumps({"blocos": [{"id": "B01", "inicio_s": 0.0}]}))
    (pasta / "audio" / "B01.words.json").write_text(json.dumps([{"p": "Em", "ini": 0.2, "fim": 0.4}]))
    rel = gates.Relatorio()
    gates.gate_legenda(pasta, rel)
    assert status(rel, "sincronia com a fala") == ["FALHOU"]


def test_regressao(pasta):
    gates.BASELINE.parent.mkdir(parents=True)
    gates.BASELINE.write_text(json.dumps({"legenda.cps_max": 14.0}))
    rel = gates.Relatorio()
    rel.metricas["legenda.cps_max"] = 19.0
    gates.gate_regressao(rel)
    assert status(rel, "regressão legenda.cps_max") == ["FALHOU"]


def test_caso_aprendido(pasta):
    gates.CASOS.parent.mkdir(parents=True)
    gates.CASOS.write_text(json.dumps([{"id": "gancho-lento", "metrica": "edicao.plano_medio_gancho_s", "max": 4.0,
                                         "origem": "queda aos 0:20 no vídeo X", "dono": "editor-video"}]))
    rel = gates.Relatorio()
    rel.metricas["edicao.plano_medio_gancho_s"] = 5.5
    gates.gate_regressao(rel)
    assert status(rel, "caso gancho-lento") == ["FALHOU"]


# ---------- mídia sintética ----------
@tem_ffmpeg
def test_voz_ritmo_e_clipping(pasta):
    # 15 palavras em 6 s (+0,5 s de pausa final) = 150 palavras/min
    ff("-f", "lavfi", "-i", "sine=f=220:d=6.5", "-af", "volume=-12dB", "-ar", "24000", str(pasta / "audio" / "B01.wav"))
    rel = gates.Relatorio()
    gates.gate_voz(pasta, rel)
    assert status(rel, "velocidade (palavras/min)") == ["PASSOU"]
    ff("-f", "lavfi", "-i", "sine=f=220:d=2", "-af", "volume=24dB", "-ar", "24000", str(pasta / "audio" / "B01.wav"))
    rel = gates.Relatorio()
    gates.gate_voz(pasta, rel)
    assert status(rel, "velocidade (palavras/min)") == ["FALHOU"]
    assert status(rel, "estouro (clipping)") == ["FALHOU"]


@tem_ffmpeg
def test_video_bom(pasta):
    v = pasta / "final" / "video.mp4"
    # 4 cenas de 3 s (troca de imagem no ritmo certo) com áudio já em -14 LUFS
    cenas = []
    for cor in ("red", "green", "blue", "yellow"):
        cenas += ["-f", "lavfi", "-i", f"color={cor}:s=1920x1080:r=30:d=3"]
    ff(*cenas, "-f", "lavfi", "-i", "sine=f=330:d=12", "-filter_complex",
       "[0][1][2][3]concat=n=4:v=1:a=0[v];[4]loudnorm=I=-14:TP=-1.5,aresample=48000[a]",
       "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(v))
    rel = gates.Relatorio()
    gates.checar_video(v, rel, "edicao", "longo")
    falhas = [i for i in rel.itens if i["status"] == "FALHOU"]
    assert not falhas, falhas


@tem_ffmpeg
def test_video_com_tela_preta_silencio_e_plano_longo(pasta):
    v = pasta / "final" / "video.mp4"
    ff("-f", "lavfi", "-i", "color=red:s=1280x720:r=25:d=14", "-f", "lavfi", "-i", "color=black:s=1280x720:r=25:d=2",
       "-f", "lavfi", "-i", "color=blue:s=1280x720:r=25:d=3",
       "-f", "lavfi", "-i", "aevalsrc='if(between(t,5,9),0,0.3*sin(2*PI*330*t))':d=19",
       "-filter_complex", "[0][1][2]concat=n=3:v=1:a=0[v]", "-map", "[v]", "-map", "3:a",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(v))
    rel = gates.Relatorio()
    gates.checar_video(v, rel, "edicao", "longo")
    assert status(rel, "resolução") == ["FALHOU"]
    assert status(rel, "fps") == ["FALHOU"]
    assert "FALHOU" in status(rel, "tela preta")
    assert "FALHOU" in status(rel, "silêncio na mixagem")
    assert status(rel, "plano mais longo sem troca (s)") in (["AVISO"], ["FALHOU"])
    assert status(rel, "imagem congelada")


@tem_ffmpeg
def test_preview_e_relatorio(pasta):
    ff("-f", "lavfi", "-i", "testsrc2=s=1920x1080:r=30:d=6", "-f", "lavfi", "-i", "sine=d=6",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(pasta / "final" / "video.mp4"))
    out = gates.preview(pasta)
    for nome in ("contato.png", "gancho.png", "celular.png", "onda.png", "gancho_30s.mp3", "LEIA.md"):
        assert (out / nome).exists(), nome
    rel = gates.Relatorio()
    rel.add("voz", "x", "FALHOU", 1, 0, "corrigir")
    assert gates.escrever(pasta, rel) == "REPROVADO"
    assert "## diretor-narracao" in (pasta / "qualidade" / "correcoes.md").read_text(encoding="utf-8")


# ---------- entonação (prosódia) ----------
def voz_sintetica(arq, contorno_hz, sr=16000):
    """Tom com harmônicos seguindo um contorno de altura, com pausas de 0,3 s a cada 2 s (imita frases)."""
    import numpy as np
    import soundfile as sf
    f = np.asarray(contorno_hz, dtype=float)
    fase = 2 * np.pi * np.cumsum(f) / sr
    y = sum(np.sin(k * fase) / k for k in range(1, 6)) * 0.2
    t = np.arange(len(f)) / sr
    y[(t % 2.0) > 1.7] = 0
    sf.write(arq, y, sr)


@tem_ffmpeg
def test_prosodia_monotona_vs_expressiva(tmp_path):
    pytest.importorskip("librosa")
    import numpy as np
    sr, n = 16000, 16000 * 8
    t = np.arange(n) / sr
    voz_sintetica(tmp_path / "mono.wav", np.full(n, 130.0))
    voz_sintetica(tmp_path / "viva.wav", 130 * 2 ** (4 * np.sin(2 * np.pi * 0.6 * t) / 12))  # ±4 semitons
    mono, viva = gates.prosodia(tmp_path / "mono.wav"), gates.prosodia(tmp_path / "viva.wav")
    assert mono["f0_sigma_st"] < gates.LIM["voz"]["f0_sigma_min"]
    assert viva["f0_sigma_st"] > gates.LIM["voz"]["f0_sigma_aviso"]
    assert 20 <= viva["pausas_min"] <= 40  # 1 pausa a cada 2 s


def test_silabas():
    assert gates.silabas("três homens sumiram") == 6
    assert gates.silabas("o farol") == 3
