---
name: narracao-ia
description: Use ao gerar a narração de um vídeo do canal, para manter a mesma voz, ajustar pausas e pronúncia, gerar um áudio por bloco do roteiro com o Kokoro (grátis) e entregar o arquivo de tempos e as palavras com tempo para a edição. Usada pelo diretor-narracao.
---
# 🎙️ Narração com IA (custo zero)

Motor padrão: **Kokoro** (grátis, roda local, licença Apache 2.0 permite monetizar).
Motor futuro: ElevenLabs (pago), só com autorização do usuário.

## Voz do canal (definir uma vez)
Arquivo `canal/voz.md`:
```yaml
motor: kokoro
voz: pm_alex        # PT-BR: pm_alex (masc.), pm_santa (masc.), pf_dora (fem.)
velocidade: 0.95    # 0.9–1.0 soa mais "documentário"
```
- Escolha: gere o mesmo parágrafo de gancho com as 3 vozes e peça ao usuário para escolher (única pergunta desta etapa).
- Depois, **nunca troque** sem aprovação. A voz é a marca do canal.

## Preparar o texto (o Kokoro lê exatamente o que está escrito)
1. Pronúncia: use `{{grafia|pronúncia}}` no roteiro (`{{Eilean Mor|Ê-lan Mór}}`); o script troca sozinho.
2. Números, datas e siglas por extenso quando a leitura for ambígua ("1900" → "mil e novecentos", "FBI" → "efe-bi-ai").
3. Pausas: pontuação manda (vírgula curta, ponto médio, reticências longa). Pausa no fim do bloco: `pausa_final=0.8s` no `[VOZ: ...]`.
4. Frases acima de ~25 palavras soam robóticas: quebre.

## Gerar
```bash
python scripts/narracao/narrar.py producao/<pasta> --palavras
```
- Saída: `audio/Bxx.wav` (24 kHz), `audio/tempos.json`, `audio/Bxx.words.json` (tempo de cada palavra, usado nas legendas).
- Palavra errada ou estranha → corrija a grafia no roteiro e rode de novo (é grátis).
- Registre em `custos.md`: `narração: kokoro, R$ 0`.

## `audio/tempos.json`
```json
{ "motor": "kokoro", "voz": "pm_alex", "total_s": 612.4,
  "blocos": [ { "id": "B01", "arquivo": "B01.wav", "inicio_s": 0.0, "duracao_s": 14.2 } ] }
```

## Se um dia usar ElevenLabs
Só com o "pode" do usuário. Mesma estrutura de saída; registre `voice_id`, modelo e caracteres gastos em `canal/voz.md` e `custos.md`.

## Pronto quando
- [ ] Todos os blocos com a voz de `canal/voz.md`
- [ ] Duração total ±10% da meta (se sair curto, ajuste a velocidade, não o roteiro)
- [ ] `tempos.json` e `words.json` gerados
