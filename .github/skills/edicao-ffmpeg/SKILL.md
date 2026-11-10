---
name: edicao-ffmpeg
description: Use ao montar e renderizar o vídeo final com FFmpeg a partir da narração, das imagens e da trilha, com zoom lento nas imagens, troca de cena no ritmo da fala, trilha abaixando sob a voz, legendas e volume no padrão do YouTube. Usada pelo editor-video e pelo editor-shorts.
---
# 🎬 Edição e render com FFmpeg

Tudo pela linha de comando (`Bash`). Confira antes: `ffmpeg -version`.

## Padrão de saída
| Formato | Resolução | FPS | Vídeo | Áudio |
|---|---|---|---|---|
| Vídeo longo | 1920x1080 | 30 | H.264, CRF 18, `yuv420p` | AAC 192k, -14 LUFS |
| Short | 1080x1920 | 30 | igual | igual |

## 1. Juntar a narração
```bash
cd producao/<pasta>
for f in audio/B*.wav; do echo "file '$PWD/$f'"; done > audio/lista.txt
ffmpeg -y -f concat -safe 0 -i audio/lista.txt -c:a pcm_s16le audio/narracao.wav
```

## 2. Imagem parada com zoom lento ("efeito Ken Burns")
Cada imagem vira um clipe com a duração da cena (`D` em segundos):
```bash
D=5; FR=$((D*30))
ffmpeg -y -loop 1 -i visual/c001.png -t $D -vf \
"scale=3840:-2,zoompan=z='min(zoom+0.0008,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$FR:s=1920x1080:fps=30,format=yuv420p" \
-c:v libx264 -crf 18 clips/c001.mp4
```
- Varie o movimento: zoom in, zoom out (`z='if(eq(on,1),1.12,max(zoom-0.0008,1))'`), pan lateral (mude `x`).
- Troca de imagem a cada 3–6 s. Durações saem de `audio/tempos.json` divididas pelo nº de `[CENA]` do bloco.

## 3. Juntar os clipes
```bash
for f in clips/c*.mp4; do echo "file '$PWD/$f'"; done > clips/lista.txt
ffmpeg -y -f concat -safe 0 -i clips/lista.txt -c copy final/video_mudo.mp4
```
Transição suave (opcional, entre 2 clipes): `xfade=transition=fade:duration=0.4:offset=<D1-0.4>`.

## 4. Trilha abaixando sob a voz ("ducking") + volume padrão
```bash
ffmpeg -y -i final/video_mudo.mp4 -i audio/narracao.wav -stream_loop -1 -i trilha/trilha.mp3 -filter_complex \
"[2:a]volume=0.35[m];[m][1:a]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];\
[1:a][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest final/video.mp4
```

## 5. Legendas
- Gere `final/legendas.srt` a partir de `audio/Bxx.words.json` (gerado pelo `narrar.py --palavras`) somando o `inicio_s` de cada bloco (frases de até 42 caracteres, 1–2 linhas, 1–6 s cada).
- Vídeo longo: suba o `.srt` separado no YouTube (não queime).
- Short: queime no vídeo:
```bash
ffmpeg -y -i short.mp4 -vf "subtitles=legendas.srt:force_style='FontName=Montserrat,FontSize=14,Bold=1,Outline=3,Alignment=2,MarginV=80'" -c:a copy short_leg.mp4
```

## 6. Short a partir do vídeo longo
```bash
ffmpeg -y -ss 00:01:20 -t 45 -i final/video.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a copy shorts/s01.mp4
```

## Conferência final
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate -of compact final/video.mp4
ffmpeg -i final/video.mp4 -af loudnorm=print_format=summary -f null - 2>&1 | grep "Input Integrated"
```
- [ ] Resolução e FPS corretos · [ ] ~-14 LUFS · [ ] áudio e imagem com a mesma duração · [ ] origem de cada imagem/música registrada em `edicao.md`
