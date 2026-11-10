"""Quality gates de produção do canal (custo zero: só FFmpeg + Python; Whisper e UTMOS opcionais).

Uso:
  python scripts/qualidade/gates.py roteiro  producao/<pasta>
  python scripts/qualidade/gates.py voz      producao/<pasta> [--transcrever] [--mos]
  python scripts/qualidade/gates.py legenda  producao/<pasta>
  python scripts/qualidade/gates.py edicao   producao/<pasta>
  python scripts/qualidade/gates.py todos    producao/<pasta> [--transcrever] [--mos]
  python scripts/qualidade/gates.py preview  producao/<pasta>
  python scripts/qualidade/gates.py aprovar-baseline producao/<pasta>

Saída em producao/<pasta>/qualidade/: relatorio.json, relatorio.md, correcoes.md.
Código de saída: 0 = aprovado (com ou sem avisos), 1 = reprovado.
"""
import argparse
import json
import re
import statistics
import subprocess
import unicodedata
from datetime import datetime
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LIM = json.loads((AQUI / "limites.json").read_text(encoding="utf-8"))
BASELINE = Path("canal/qualidade/baseline.json")
CASOS = Path("canal/qualidade/casos.json")

BLOCO = re.compile(r"^## \[(B\d+)\][^\n]*\n(.*?)(?=^## \[B\d+\]|\Z)", re.S | re.M)
PAUSA = re.compile(r"pausa_final=([\d.]+)s")
DONO = {"roteiro": "roteirista", "voz": "diretor-narracao", "legenda": "editor-video",
        "edicao": "editor-video", "audio-mix": "sonoplasta", "thumb": "especialista-thumbnail",
        "shorts": "editor-shorts", "regressao": "gerente"}


# ---------- utilidades ----------
class Relatorio:
    def __init__(self):
        self.itens, self.metricas = [], {}

    def add(self, gate, item, status, valor, limite, correcao="", onde="", dono=None):
        self.itens.append({"gate": gate, "item": item, "status": status, "valor": valor, "limite": limite,
                           "onde": onde, "dono": dono or DONO[gate], "correcao": correcao})

    def faixa(self, gate, item, valor, aviso, maximo, correcao, onde="", maior_ruim=True, dono=None):
        """Compara valor com limites de aviso e de falha (maior_ruim=False inverte)."""
        ruim = (lambda v, l: v > l) if maior_ruim else (lambda v, l: v < l)
        status = "FALHOU" if ruim(valor, maximo) else "AVISO" if ruim(valor, aviso) else "PASSOU"
        self.add(gate, item, status, round(valor, 3), f"aviso {aviso} / falha {maximo}",
                 correcao if status != "PASSOU" else "", onde, dono)

    def parecer(self):
        st = {i["status"] for i in self.itens}
        return "REPROVADO" if "FALHOU" in st else "APROVADO_COM_AVISOS" if "AVISO" in st else "APROVADO"


def rodar(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def sonda(arq):
    r = rodar(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(arq)])
    return json.loads(r.stdout or "{}")


def duracao(arq):
    return float(sonda(arq).get("format", {}).get("duration", 0))


def loudness(arq):
    err = rodar(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arq), "-af",
                 "loudnorm=print_format=json", "-f", "null", "-"]).stderr
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
    d = json.loads(m[0]) if m else {}
    return {"I": float(d.get("input_i", "nan")), "TP": float(d.get("input_tp", "nan")),
            "LRA": float(d.get("input_lra", "nan"))}


def astats(arq):
    err = rodar(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arq), "-af", "astats", "-f", "null", "-"]).stderr
    geral = err.split("Overall")[-1]

    def pega(nome):
        m = re.search(nome + r":\s*(-?[\d.]+|-inf)", geral)
        return -120.0 if not m or m[1] == "-inf" else float(m[1])
    return {"pico": pega("Peak level dB"), "rms": pega("RMS level dB"), "ruido": pega("RMS trough dB")}


def silencios(arq, db=-45, d=0.5):
    err = rodar(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arq), "-af",
                 f"silencedetect=noise={db}dB:d={d}", "-f", "null", "-"]).stderr
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", err)]
    fim = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(ini, fim + [duracao(arq)] * (len(ini) - len(fim))))


def detectar(arq, filtro, chave_ini, chave_fim):
    err = rodar(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arq), "-vf", filtro, "-an", "-f", "null", "-"]).stderr
    ini = [float(x) for x in re.findall(chave_ini + r"[:=]\s*([\d.]+)", err)]
    fim = [float(x) for x in re.findall(chave_fim + r"[:=]\s*([\d.]+)", err)]
    return list(zip(ini, fim))


def cortes(arq, limiar):
    err = rodar(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arq), "-vf",
                 f"select='gt(scene,{limiar})',showinfo", "-an", "-f", "null", "-"]).stderr
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", err)]


def planos(tcortes, total):
    marcas = [0.0] + sorted(tcortes) + [total]
    return [(a, b - a) for a, b in zip(marcas, marcas[1:]) if b - a > 0.05]


def normalizar(txt):
    txt = unicodedata.normalize("NFKC", txt.lower())
    return re.findall(r"[\wà-ú]+", txt)


def wer(ref, hip):
    r, h = normalizar(ref), normalizar(hip)
    if not r:
        return 0.0, []
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        ant, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            ant, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, ant + (r[i - 1] != h[j - 1]))
    faltando = sorted(set(r) - set(h))
    return d[len(h)] / len(r), faltando[:10]


def texto_falado(corpo):
    corpo = re.sub(r"<!--.*?-->", "", corpo, flags=re.S)
    corpo = re.sub(r"^\[(CENA|VOZ)[^\]]*\]\s*$", "", corpo, flags=re.M)
    corpo = re.sub(r"\{\{[^|}]+\|([^}]+)\}\}", r"\1", corpo)
    return " ".join(corpo.split())


def blocos(pasta):
    arq = pasta / "roteiro.md"
    return BLOCO.findall(arq.read_text(encoding="utf-8")) if arq.exists() else []


def meta_min(pasta):
    arq = pasta / "roteiro.md"
    m = re.search(r"duracao_meta:\s*([\d.]+)", arq.read_text(encoding="utf-8")) if arq.exists() else None
    return float(m[1]) if m else None


def ler_srt(arq):
    cues = []
    for bloco in re.split(r"\n\s*\n", arq.read_text(encoding="utf-8-sig").strip()):
        linhas = bloco.strip().splitlines()
        idx = next((k for k, l in enumerate(linhas) if "-->" in l), None)
        if idx is None:
            continue
        t = re.findall(r"(\d+):(\d+):(\d+)[,.](\d+)", linhas[idx])
        seg = [int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000 for h, m, s, ms in t]
        cues.append({"n": len(cues) + 1, "ini": seg[0], "fim": seg[1], "linhas": linhas[idx + 1:]})
    return cues


def palavras_globais(pasta):
    tempos = pasta / "audio" / "tempos.json"
    if not tempos.exists():
        return []
    out = []
    for b in json.loads(tempos.read_text(encoding="utf-8"))["blocos"]:
        w = pasta / "audio" / f"{b['id']}.words.json"
        if w.exists():
            out += [(p["ini"] + b["inicio_s"], p["p"]) for p in json.loads(w.read_text(encoding="utf-8"))]
    return out


def ngramas(txt, n=3):
    p = normalizar(txt)
    return {tuple(p[i:i + n]) for i in range(len(p) - n + 1)}


# ---------- gates ----------
def gate_roteiro(pasta, rel):
    L = LIM["roteiro"]
    bs = blocos(pasta)
    if not bs:
        rel.add("roteiro", "roteiro.md existe", "FALHOU", "ausente", "obrigatório", "Entregar roteiro.md no formato de blocos.")
        return
    txt_total = " ".join(texto_falado(c) for _, c in bs)
    total = len(txt_total.split())
    meta = meta_min(pasta)
    if meta:
        alvo = meta * L["wpm_ref"]
        desvio = abs(total - alvo) / alvo
        rel.faixa("roteiro", "palavras vs duração meta", desvio, L["duracao_tolerancia"], L["duracao_tolerancia"] * 2,
                  f"Roteiro tem {total} palavras; meta {meta} min ≈ {alvo:.0f}. Cortar ou expandir blocos.")
    gancho = texto_falado(bs[0][1])
    seg_gancho = len(gancho.split()) / L["wpm_ref"] * 60
    rel.faixa("roteiro", "gancho (s estimados)", seg_gancho, L["gancho_max_s"], L["gancho_max_s"] * 1.5,
              "Gancho longo: começar no momento mais estranho e cortar contexto.", bs[0][0])
    for termo in L["proibido_gancho"]:
        if termo in gancho.lower():
            rel.add("roteiro", "abertura genérica no gancho", "AVISO", termo, "não usar",
                    f"Remover '{termo}' do gancho (derruba retenção dos 30 s iniciais).", bs[0][0])
    longas = []
    for bid, corpo in bs:
        if "[CENA" not in corpo or "[VOZ" not in corpo:
            rel.add("roteiro", "marcações [CENA]/[VOZ]", "FALHOU", "faltando", "obrigatório",
                    "Todo bloco precisa de [CENA] e [VOZ].", bid)
        n_cena = max(corpo.count("[CENA"), 1)
        ppc = len(texto_falado(corpo).split()) / n_cena
        if ppc > L["palavras_por_cena_max"]:
            rel.add("roteiro", "palavras por [CENA]", "AVISO", round(ppc, 1), L["palavras_por_cena_max"],
                    "Adicionar [CENA] (troca de imagem a cada 3–6 s).", bid)
        if "⚠️" in corpo:
            rel.add("roteiro", "fato sem confirmação (⚠️)", "FALHOU", "⚠️", "nenhum", "Confirmar ou remover o fato.", bid)
        for frase in re.split(r"(?<=[.!?…])\s+", texto_falado(corpo)):
            if len(frase.split()) > L["frase_max_palavras"]:
                longas.append(f"{bid}: {frase[:60]}…")
    rel.add("roteiro", "frases longas (>25 palavras)", "AVISO" if longas else "PASSOU", len(longas),
            L["frase_max_palavras"], "Quebrar: TTS soa robótico em frases longas. " + " | ".join(longas[:5]) if longas else "")
    # similaridade com roteiros anteriores (risco de 'conteúdo inautêntico')
    meus, pior, qual = ngramas(txt_total), 0.0, ""
    for outro in pasta.parent.glob("*/roteiro.md"):
        if outro.parent == pasta:
            continue
        deles = ngramas(" ".join(texto_falado(c) for _, c in BLOCO.findall(outro.read_text(encoding="utf-8"))))
        if meus and deles:
            j = len(meus & deles) / len(meus | deles)
            if j > pior:
                pior, qual = j, outro.parent.name
    rel.faixa("roteiro", "similaridade com vídeo anterior", pior, L["similaridade_aviso"], 0.5,
              f"Texto parecido demais com {qual}: reescrever estrutura e frases (política de conteúdo inautêntico).")
    rel.metricas["roteiro.palavras"] = total


def gate_voz(pasta, rel, transcrever=False, mos=False):
    L = LIM["voz"]
    textos = {bid: (texto_falado(c), PAUSA.search(c)) for bid, c in blocos(pasta)}
    wavs = sorted((pasta / "audio").glob("B*.wav"))
    if not wavs:
        rel.add("voz", "áudios por bloco", "FALHOU", 0, "1 por bloco", "Gerar narração (narrar.py).")
        return
    faltam = set(textos) - {w.stem for w in wavs}
    if faltam:
        rel.add("voz", "áudios por bloco", "FALHOU", sorted(faltam), "todos", "Gerar os blocos que faltam.")
    wpms, wers, moss = [], [], []
    modelo = preditor = None
    if transcrever:
        try:
            from faster_whisper import WhisperModel
            modelo = WhisperModel("small", device="auto", compute_type="int8")
        except ImportError:
            rel.add("voz", "transcrição (Whisper)", "AVISO", "indisponível", "instalado",
                    "pip install faster-whisper", dono="gerente")
    if mos:
        try:
            import torch
            import soundfile as sf
            preditor = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
        except Exception as e:  # noqa: BLE001 (opcional)
            rel.add("voz", "naturalidade (UTMOS)", "AVISO", f"indisponível: {e.__class__.__name__}", "instalado",
                    "pip install torch soundfile", dono="gerente")
    for w in wavs:
        bid = w.stem
        texto, pausa = textos.get(bid, ("", None))
        dur = duracao(w) - (float(pausa[1]) if pausa else 0)
        if texto and dur > 0:
            wpm = len(texto.split()) / dur * 60
            wpms.append(wpm)
            st = "FALHOU" if not (L["wpm_min"] <= wpm <= L["wpm_max"]) else "PASSOU"
            rel.add("voz", "velocidade (palavras/min)", st, round(wpm), f"{L['wpm_min']}–{L['wpm_max']}",
                    "Ajustar 'velocidade' em canal/voz.md ou quebrar/encurtar frases." if st != "PASSOU" else "", bid)
        a = astats(w)
        if a["pico"] >= L["pico_clip_db"]:
            rel.add("voz", "estouro (clipping)", "FALHOU", a["pico"], f"< {L['pico_clip_db']} dB", "Baixar ganho e regerar.", bid)
        elif a["pico"] > L["pico_aviso_db"]:
            rel.add("voz", "pico", "AVISO", a["pico"], f"≤ {L['pico_aviso_db']} dB", "Aplicar limitador a -3 dB.", bid)
        if not (L["rms_min_db"] <= a["rms"] <= L["rms_max_db"]):
            rel.add("voz", "volume médio (RMS)", "AVISO", a["rms"], f"{L['rms_min_db']}..{L['rms_max_db']} dB",
                    "Normalizar o bloco para ficar igual aos outros.", bid)
        if a["ruido"] > L["ruido_max_db"]:
            rel.add("voz", "ruído de fundo", "AVISO", a["ruido"], f"≤ {L['ruido_max_db']} dB", "Aplicar gate/denoise.", bid)
        fim_util = duracao(w) - (float(pausa[1]) if pausa else 0) - 0.3
        estranhas = [(round(i, 2), round(f - i, 2)) for i, f in silencios(w, -45, L["pausa_interna_max_s"])
                     if 0.2 < i < fim_util]
        if estranhas:
            rel.add("voz", "pausa estranha no meio", "AVISO", estranhas[:3], f"≤ {L['pausa_interna_max_s']} s",
                    "Revisar pontuação (reticências/ponto) perto desses tempos.", bid)
        if modelo and texto:
            segs, _ = modelo.transcribe(str(w), language="pt")
            taxa, erradas = wer(texto, " ".join(s.text for s in segs))
            wers.append(taxa)
            rel.faixa("voz", "inteligibilidade (WER Whisper)", taxa, L["wer_aviso"], L["wer_max"],
                      f"Palavras mal pronunciadas: {erradas}. Usar {{{{grafia|pronúncia}}}} no roteiro e regerar.", bid)
        if preditor:
            onda, sr = sf.read(str(w), dtype="float32")
            nota = float(preditor(torch.from_numpy(onda if onda.ndim == 1 else onda.mean(1)).unsqueeze(0), sr))
            moss.append(nota)
            rel.faixa("voz", "naturalidade (UTMOS 1–5)", nota, L["mos_aviso"], L["mos_min"],
                      "Voz soa artificial: frases menores, pontuação, velocidade 0.9–1.0.", bid, maior_ruim=False)
    if len(wpms) > 1:
        cv = statistics.pstdev(wpms) / statistics.mean(wpms)
        rel.faixa("voz", "consistência de ritmo entre blocos", cv, L["wpm_cv_max"], L["wpm_cv_max"] * 2,
                  "Blocos com ritmos muito diferentes: igualar tamanho de frase e pontuação.")
        rel.metricas["voz.wpm_cv"] = round(cv, 4)
    if wpms:
        rel.metricas["voz.wpm_medio"] = round(statistics.mean(wpms), 1)
    if wers:
        rel.metricas["voz.wer_medio"] = round(statistics.mean(wers), 4)
    if moss:
        rel.metricas["voz.mos_medio"] = round(statistics.mean(moss), 3)


def checar_srt(arq, rel, gate, palavras=None):
    L = LIM["legenda"]
    cues = ler_srt(arq)
    if not cues:
        rel.add(gate, "legenda existe", "FALHOU", "vazia", "obrigatória", "Gerar .srt a partir dos words.json.")
        return
    cps_max, sync_max = 0.0, 0.0
    for c in cues:
        onde = f"{arq.name}#{c['n']} ({c['ini']:.2f}s)"
        dur = c["fim"] - c["ini"]
        txt = " ".join(c["linhas"])
        if len(c["linhas"]) > L["linhas_max"]:
            rel.add(gate, "linhas por legenda", "FALHOU", len(c["linhas"]), L["linhas_max"], "Dividir a legenda.", onde)
        maior = max((len(l) for l in c["linhas"]), default=0)
        if maior > L["chars_linha_max"]:
            rel.add(gate, "caracteres por linha", "FALHOU", maior, L["chars_linha_max"], "Quebrar a linha.", onde)
        if dur <= 0:
            rel.add(gate, "duração da legenda", "FALHOU", dur, "> 0", "Tempo de fim antes do início.", onde)
            continue
        cps = len(txt) / dur
        cps_max = max(cps_max, cps)
        if cps > L["cps_aviso"]:
            rel.faixa(gate, "velocidade de leitura (CPS)", cps, L["cps_aviso"], L["cps_max"],
                      "Texto demais para o tempo: dividir ou alongar a legenda.", onde)
        if dur < L["dur_min_s"] or dur > L["dur_max_s"]:
            rel.add(gate, "duração da legenda", "AVISO", round(dur, 2), f"{L['dur_min_s']}–{L['dur_max_s']} s",
                    "Juntar com a vizinha ou dividir.", onde)
        if palavras:
            prox = min(palavras, key=lambda p: abs(p[0] - c["ini"]))
            desvio = abs(prox[0] - c["ini"])
            sync_max = max(sync_max, desvio)
            if desvio > L["sync_aviso_s"]:
                rel.faixa(gate, "sincronia com a fala", desvio, L["sync_aviso_s"], L["sync_max_s"],
                          "Recalcular tempos a partir de audio/Bxx.words.json + inicio_s do bloco.", onde)
    for a, b in zip(cues, cues[1:]):
        gap = b["ini"] - a["fim"]
        if gap < 0:
            rel.add(gate, "legendas sobrepostas", "FALHOU", round(gap, 3), "≥ 0", "Ajustar fim da anterior.", f"#{a['n']}/#{b['n']}")
        elif 0 < gap < L["gap_min_s"]:
            rel.add(gate, "intervalo entre legendas", "AVISO", round(gap, 3), f"0 ou ≥ {L['gap_min_s']} s",
                    "Encostar (gap 0) ou abrir 2 quadros.", f"#{a['n']}/#{b['n']}")
    rel.add(gate, "legendas checadas", "PASSOU", len(cues), "-")
    rel.metricas[f"{gate}.cps_max"] = round(cps_max, 2)
    if palavras:
        rel.metricas[f"{gate}.sync_max_s"] = round(sync_max, 3)


def gate_legenda(pasta, rel):
    srt = pasta / "final" / "legendas.srt"
    if not srt.exists():
        rel.add("legenda", "final/legendas.srt", "FALHOU", "ausente", "obrigatório", "Gerar a legenda (skill edicao-ffmpeg §5).")
        return
    checar_srt(srt, rel, "legenda", palavras_globais(pasta))


def checar_video(arq, rel, gate, formato, meta_s=None):
    L = LIM["edicao"]
    info = sonda(arq)
    v = next((s for s in info.get("streams", []) if s["codec_type"] == "video"), None)
    a = next((s for s in info.get("streams", []) if s["codec_type"] == "audio"), None)
    nome = arq.name
    if not v or not a:
        rel.add(gate, "faixas de vídeo e áudio", "FALHOU", "faltando", "ambas", "Renderizar de novo com -map.", nome)
        return
    alvo = L[formato]
    res_ok = (v["width"], v["height"]) == (alvo["w"], alvo["h"])
    rel.add(gate, "resolução", "PASSOU" if res_ok else "FALHOU", f"{v['width']}x{v['height']}",
            f"{alvo['w']}x{alvo['h']}", "" if res_ok else "Ajustar scale/crop no render.", nome)
    n, d = (int(x) for x in v["r_frame_rate"].split("/"))
    fps = n / d if d else 0
    rel.add(gate, "fps", "PASSOU" if abs(fps - L["fps"]) < 0.01 else "FALHOU", round(fps, 2), L["fps"],
            "" if abs(fps - L["fps"]) < 0.01 else "Usar fps=30.", nome)
    for item, valor, esperado in [("codec de vídeo", v["codec_name"], L["codec_v"]),
                                  ("formato de cor", v.get("pix_fmt"), L["pix_fmt"]),
                                  ("codec de áudio", a["codec_name"], L["codec_a"])]:
        rel.add(gate, item, "PASSOU" if valor == esperado else "FALHOU", valor, esperado,
                "" if valor == esperado else "Ajustar parâmetros do render.", nome)
    dv, da = float(v.get("duration", 0)), float(a.get("duration", 0))
    if dv and da:
        rel.faixa(gate, "imagem e som com a mesma duração", abs(dv - da), L["av_desvio_max_s"], L["av_desvio_max_s"] * 5,
                  "Usar -shortest ou ajustar o último clipe.", nome)
    total = duracao(arq)
    if meta_s:
        rel.faixa(gate, "duração vs meta", abs(total - meta_s) / meta_s, L["duracao_tolerancia"], L["duracao_tolerancia"] * 2,
                  f"Duração {total/60:.1f} min vs meta {meta_s/60:.0f} min.", nome)
    lu = loudness(arq)
    desvio = abs(lu["I"] - L["lufs_alvo"])
    rel.faixa(gate, "volume integrado (LUFS)", desvio, L["lufs_aviso"], L["lufs_max"],
              f"Volume em {lu['I']} LUFS; aplicar loudnorm=I=-14:TP=-1.5.", nome, dono="sonoplasta")
    rel.add(gate, "pico real (dBTP)", "PASSOU" if lu["TP"] <= L["true_peak_max"] else "FALHOU", lu["TP"],
            f"≤ {L['true_peak_max']}", "" if lu["TP"] <= L["true_peak_max"] else "Limitar TP a -1.5 no loudnorm.",
            nome, dono="sonoplasta")
    rel.metricas[f"{gate}.lufs_desvio"] = round(desvio, 2)
    for i, f in detectar(arq, "blackdetect=d=0.1:pix_th=0.10", "black_start", "black_end"):
        if f - i > L["preto_max_s"] and 1.0 < i < total - 1.0:
            rel.add(gate, "tela preta", "FALHOU", round(f - i, 2), f"≤ {L['preto_max_s']} s",
                    "Clipe faltando ou imagem não gerada nesse trecho.", f"{nome} @ {i:.1f}s")
    for i, f in detectar(arq, f"freezedetect=n=-60dB:d={L['congelado_aviso_s']}",
                         "lavfi.freezedetect.freeze_start", "lavfi.freezedetect.freeze_end"):
        rel.add(gate, "imagem congelada", "AVISO", round(f - i, 2), f"≤ {L['congelado_aviso_s']} s",
                "Faltou zoom/pan (Ken Burns) ou troca de cena.", f"{nome} @ {i:.1f}s")
    for i, f in silencios(arq, L["silencio_db"], L["silencio_max_s"]):
        if i < total - 1.0:
            rel.add(gate, "silêncio na mixagem", "FALHOU", round(f - i, 2), f"≤ {L['silencio_max_s']} s",
                    "Buraco no áudio: conferir concat da narração e a trilha.", f"{nome} @ {i:.1f}s", dono="sonoplasta")
    pl = planos(cortes(arq, L["cena_limiar"]), total)
    if pl:
        pior = max(pl, key=lambda p: p[1])
        rel.faixa(gate, "plano mais longo sem troca (s)", pior[1], L["plano_max_s"], L["plano_max_s"] * 2,
                  "Trocar de imagem a cada 3–6 s.", f"{nome} @ {pior[0]:.1f}s")
        gancho = [d for t, d in pl if t < 30] or [pl[0][1]]
        medio = statistics.mean(gancho)
        rel.faixa(gate, "ritmo nos 30 s iniciais (s/plano)", medio, L["plano_medio_gancho_max_s"],
                  L["plano_medio_gancho_max_s"] * 1.5, "Gancho lento: mais cortes nos primeiros 30 s.", nome)
        rel.metricas[f"{gate}.plano_max_s"] = round(pior[1], 2)
        rel.metricas[f"{gate}.plano_medio_gancho_s"] = round(medio, 2)


def gate_edicao(pasta, rel):
    video = pasta / "final" / "video.mp4"
    if not video.exists():
        rel.add("edicao", "final/video.mp4", "FALHOU", "ausente", "obrigatório", "Renderizar o vídeo.")
    else:
        meta = meta_min(pasta)
        checar_video(video, rel, "edicao", "longo", meta * 60 if meta else None)
    for s in sorted((pasta / "shorts").glob("*.mp4")):
        checar_video(s, rel, "shorts", "short")
        if duracao(s) > LIM["edicao"]["short_dur_max_s"]:
            rel.add("shorts", "duração do Short", "FALHOU", round(duracao(s)), "≤ 180 s", "Cortar o Short.", s.name)
    L = LIM["thumb"]
    for t in sorted((pasta / "thumb").glob("*.[pj][np]g")):
        st = next((x for x in sonda(t).get("streams", [])), {})
        ok = (st.get("width"), st.get("height")) == (L["w"], L["h"]) and t.stat().st_size <= L["bytes_max"]
        rel.add("thumb", "thumbnail 1280x720 e ≤ 2 MB", "PASSOU" if ok else "FALHOU",
                f"{st.get('width')}x{st.get('height')}, {t.stat().st_size // 1024} KB", "1280x720, ≤ 2048 KB",
                "" if ok else "Exportar em 1280x720 JPG/PNG abaixo de 2 MB.", t.name)


def gate_regressao(rel):
    """Compara métricas com a baseline do canal e roda os casos aprendidos (casos.json)."""
    if BASELINE.exists():
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        for chave, regra in LIM["regressao"].items():
            if chave in rel.metricas and chave in base:
                atual, ref = rel.metricas[chave], base[chave]
                piorou = atual > ref + regra["tol"] if regra["dir"] == "menor" else atual < ref - regra["tol"]
                rel.add("regressao", f"regressão {chave}", "FALHOU" if piorou else "PASSOU", atual,
                        f"baseline {ref} ± {regra['tol']}",
                        "Piorou em relação aos vídeos aprovados: devolver ao dono da etapa." if piorou else "")
    else:
        rel.add("regressao", "baseline do canal", "AVISO", "ausente", "canal/qualidade/baseline.json",
                "Após o 1º vídeo aprovado pelo usuário, rodar 'aprovar-baseline'.")
    if CASOS.exists():
        for caso in json.loads(CASOS.read_text(encoding="utf-8")):
            v = rel.metricas.get(caso["metrica"])
            if v is None:
                continue
            ruim = ("max" in caso and v > caso["max"]) or ("min" in caso and v < caso["min"])
            rel.add("regressao", f"caso {caso['id']}", "FALHOU" if ruim else "PASSOU", v,
                    caso.get("max", caso.get("min")), caso.get("correcao", "") if ruim else "",
                    caso.get("origem", ""), dono=caso.get("dono", "gerente"))


def preview(pasta):
    """Gera material para olhar e ouvir: folha de contato, gancho, celular, onda e trecho de áudio."""
    out = pasta / "qualidade" / "preview"
    out.mkdir(parents=True, exist_ok=True)
    video = pasta / "final" / "video.mp4"
    cmds = []
    if video.exists():
        total = duracao(video)
        passo = max(total / 20, 1)
        cmds += [
            ["-i", str(video), "-vf", f"fps=1/{passo:.2f},scale=384:-2,tile=5x4", "-frames:v", "1", str(out / "contato.png")],
            ["-i", str(video), "-t", "30", "-vf", "fps=1/2,scale=384:-2,tile=5x3", "-frames:v", "1", str(out / "gancho.png")],
            ["-ss", str(total / 2), "-i", str(video), "-vf", "scale=360:-2", "-frames:v", "1", str(out / "celular.png")],
            ["-i", str(video), "-filter_complex", "showwavespic=s=1600x240:split_channels=1", "-frames:v", "1", str(out / "onda.png")],
            ["-i", str(video), "-t", "30", "-vn", "-c:a", "libmp3lame", "-q:a", "4", str(out / "gancho_30s.mp3")],
        ]
    for s in sorted((pasta / "shorts").glob("*.mp4")):
        # zona segura: faixas de 15% em cima e 25% embaixo ficam sob a interface do app
        cmds.append(["-ss", "2", "-i", str(s), "-vf",
                     "scale=360:640,drawbox=y=0:w=iw:h=ih*0.15:color=red@0.35:t=fill,"
                     "drawbox=y=ih*0.75:w=iw:h=ih*0.25:color=red@0.35:t=fill",
                     "-frames:v", "1", str(out / f"{s.stem}_zona_segura.png")])
    for t in sorted((pasta / "thumb").glob("*.[pj][np]g")):
        cmds.append(["-i", str(t), "-vf", "scale=168:94", str(out / f"{t.stem}_pequena.png")])
    for c in cmds:
        rodar(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + c)
    srt = pasta / "final" / "legendas.srt"
    ao_vivo = f'ffplay -vf "subtitles={srt.as_posix()}" {video.as_posix()}' if srt.exists() else f"ffplay {video.as_posix()}"
    (out / "LEIA.md").write_text(
        "# Preview para olhar e ouvir\n\n"
        "- `contato.png`: 20 quadros do vídeo inteiro (ritmo visual, repetição, tela preta).\n"
        "- `gancho.png`: um quadro a cada 2 s dos 30 s iniciais.\n"
        "- `celular.png`: quadro no tamanho de tela de celular (texto legível?).\n"
        "- `*_zona_segura.png`: Shorts com as faixas que a interface cobre em vermelho.\n"
        "- `*_pequena.png`: thumbnail no tamanho da lista de sugestões.\n"
        "- `onda.png`: forma de onda da mixagem (buracos, estouros, trilha alta).\n"
        "- `gancho_30s.mp3`: ouvir o começo.\n\n"
        f"Assistir e ouvir em tempo real com legenda:\n\n```bash\n{ao_vivo}\n```\n", encoding="utf-8")
    return out


# ---------- saída ----------
def escrever(pasta, rel):
    out = pasta / "qualidade"
    out.mkdir(exist_ok=True)
    parecer = rel.parecer()
    dados = {"video": pasta.name, "data": datetime.now().isoformat(timespec="seconds"), "parecer": parecer,
             "metricas": rel.metricas, "itens": rel.itens}
    (out / "relatorio.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    emoji = {"PASSOU": "✅", "AVISO": "⚠️", "FALHOU": "❌"}
    linhas = [f"# Quality gates: {pasta.name}", "", f"**Parecer: {parecer}**", "",
              "| Gate | Item | Status | Valor | Limite | Onde | Dono |", "|---|---|---|---|---|---|---|"]
    for i in rel.itens:
        linhas.append(f"| {i['gate']} | {i['item']} | {emoji[i['status']]} | {i['valor']} | {i['limite']} | {i['onde']} | {i['dono']} |")
    (out / "relatorio.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    por_dono = {}
    for i in rel.itens:
        if i["status"] != "PASSOU":
            por_dono.setdefault(i["dono"], []).append(i)
    corr = [f"# Correções para devolver: {pasta.name}", "", "O gerente repassa cada seção ao agente dono. "
            "❌ bloqueia; ⚠️ corrigir se der, senão justificar.", ""]
    for dono, itens in sorted(por_dono.items()):
        corr.append(f"## {dono}")
        corr += [f"- {emoji[i['status']]} **{i['item']}** ({i['onde'] or 'geral'}): {i['valor']} vs {i['limite']}. {i['correcao']}"
                 for i in itens]
        corr.append("")
    (out / "correcoes.md").write_text("\n".join(corr), encoding="utf-8")
    icone = {"APROVADO": "✅", "APROVADO_COM_AVISOS": "⚠️", "REPROVADO": "❌"}[parecer]
    print(f"{icone} {parecer} -> {out}/relatorio.md")
    return parecer


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("gate", choices=["roteiro", "voz", "legenda", "edicao", "todos", "preview", "aprovar-baseline"])
    ap.add_argument("pasta", type=Path)
    ap.add_argument("--transcrever", action="store_true", help="checa pronúncia com Whisper (WER)")
    ap.add_argument("--mos", action="store_true", help="nota de naturalidade com UTMOS")
    a = ap.parse_args()
    if a.gate == "preview":
        print(f"🎞️ preview em {preview(a.pasta)}")
        return 0
    if a.gate == "aprovar-baseline":
        dados = json.loads((a.pasta / "qualidade" / "relatorio.json").read_text(encoding="utf-8"))
        if dados["parecer"] == "REPROVADO":
            print("❌ Não dá para usar um vídeo reprovado como baseline.")
            return 1
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(dados["metricas"], ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📌 baseline atualizada com {a.pasta.name}")
        return 0
    rel = Relatorio()
    if a.gate in ("roteiro", "todos"):
        gate_roteiro(a.pasta, rel)
    if a.gate in ("voz", "todos"):
        gate_voz(a.pasta, rel, a.transcrever, a.mos)
    if a.gate in ("legenda", "todos"):
        gate_legenda(a.pasta, rel)
    if a.gate in ("edicao", "todos"):
        gate_edicao(a.pasta, rel)
    gate_regressao(rel)
    return 0 if escrever(a.pasta, rel) != "REPROVADO" else 1


if __name__ == "__main__":
    raise SystemExit(main())
