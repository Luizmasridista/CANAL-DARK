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

## 🎚️ Padrão de voz que retém (PT-BR)
Medido pelo gate `voz` do `qualidade-producao` (limites em `scripts/qualidade/limites.json`).

| O quê | Alvo | Por quê |
|---|---|---|
| Velocidade | **4,2–5,8 sílabas/s** (≈ 130–175 palavras/min, alvo 150) | locução neutra de TV em PT-BR mede ~5,5 sílabas/s; narração de mistério pede um pouco menos |
| Variação de tom | **≥ 1,8 semitom** de desvio (falha < 1,2) | leitura natural fica em ~2,2 semitons; abaixo disso soa monótona (semitom = degrau de altura, igual a uma nota musical) |
| Pausas | **10–30 por minuto** | locução informal de TV PT-BR usa ~16 pausas/min |
| Ritmo entre blocos | variar de propósito, sem passar de 12% de diferença | voz sempre igual cansa; muito diferente parece outra pessoa |

### Como "dirigir" a entonação (o TTS só obedece ao texto)
1. **Ritmo por bloco** no roteiro: `[VOZ: ritmo=lento]` no gancho, tensão e revelação; `normal` no contexto; `rapido` em listas e sequências de ação. O `narrar.py` multiplica a velocidade (0,92 / 1,0 / 1,06).
2. **Pergunta sobe o tom**: termine os ganchos e os reengates com "?" ("Mas quem abriu aquela porta?").
3. **Reticências antes da revelação** criam a pausa dramática: "E na porta... uma única capa de chuva."
4. **Frase curta = ênfase**: depois de uma frase longa, uma frase de 2 a 4 palavras. "O relógio, parado."
5. **Vírgula para respirar** a cada 8–12 palavras; nada acima de 25 palavras por frase.
6. Evite exclamação em sequência: soa teatral (o gate avisa variação > 5 semitons).
7. Teste do gancho: gere os 15 s iniciais, rode `gates.py voz` e só siga com variação de tom ≥ 1,8.

### Motor de voz
- Kokoro tem só 3 vozes PT-BR, com pouco dado de treino: entonação tende a ser plana. Use as regras acima para compensar.
- Candidato a voz principal: **Chatterbox Multilingual pt-br** (MIT, permite monetizar, tem controle de expressividade `exaggeration`). Só adotar depois de testar na RTX 3050 e passar no gate.
- Proibidos por licença não comercial: XTTS-v2, F5-TTS (inclusive o fine-tune pt-br), Fish Speech.

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
- [ ] Gate `voz` sem ❌ (velocidade, variação de tom, pausas)
