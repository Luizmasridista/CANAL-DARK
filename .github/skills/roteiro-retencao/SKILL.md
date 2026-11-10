---
name: roteiro-retencao
description: Use ao escrever ou revisar o roteiro de um vídeo do canal, para prender o público do primeiro segundo ao fim com gancho, loops abertos e ritmo, no formato de blocos que a narração e a edição leem. Usada pelo roteirista.
---
# ✍️ Roteiro que segura a audiência

## Tamanho
- ~150 palavras por minuto de narração. 8 min ≈ 1.200 palavras. 12 min ≈ 1.800.
- Blocos de 60 a 120 palavras (30 a 50 s cada).

## Estrutura
| Parte | Tempo | O que fazer |
|---|---|---|
| Gancho | 0–15 s | Começar no momento mais estranho da história. Nada de "olá, pessoal" nem logo. Fechar com uma pergunta que só o vídeo responde. |
| Promessa | 15–30 s | Dizer o que a pessoa vai descobrir ("no fim, você vai entender por que…"). |
| Contexto | até 1 min | Só o mínimo para entender. |
| Desenvolvimento | miolo | Blocos com **loops abertos**: abrir um mistério, segurar, fechar 1–2 blocos depois e abrir outro antes de fechar o anterior. |
| Virada | ~70% | Revelação ou dado que muda a leitura da história. |
| Fechamento | últimos 30 s | Fechar todos os loops. CTA curto ligado ao tema ("se você gostou deste caso, o próximo é ainda mais estranho"). |

## Técnicas
- **Loop aberto**: "mas isso não foi o mais estranho daquela noite…"
- **Reengate a cada 60–90 s**: pergunta, número chocante ou mudança de ponto de vista.
- **Concreto vence abstrato**: datas, lugares, nomes, números.
- Frases curtas, linguagem falada, uma ideia por frase. Leia em voz alta.
- Evite: "neste vídeo", "não esqueça de se inscrever" no começo, listas secas, adjetivos vagos ("incrível", "assustador").

## Formato obrigatório (`roteiro.md`)
```markdown
---
titulo_provisorio: ...
duracao_meta: 10 min
palavras: 1500
---
## [B01] Gancho
[CENA: farol abandonado à noite, neblina, câmera se aproximando]
[VOZ: tom=suspense, ritmo=lento, pausa_final=0.8s]
Em dezembro de 1900, três homens desapareceram de um farol...
<!-- fonte: briefing.md#f1 -->
```
- `[CENA]` a cada 3–6 s de fala (≈ 1 a cada 10–15 palavras) para o editor trocar de imagem.
- Todo fato com comentário `<!-- fonte -->` apontando para o briefing. Sem fonte, não entra.
- Nomes estrangeiros: escreva também a pronúncia `{{Eilean Mor|Ê-lan Mór}}` para a narração.

## Checklist antes de entregar
- [ ] O gancho funciona sem contexto?
- [ ] Há pelo menos 3 loops abertos no miolo e todos fecham?
- [ ] Contagem de palavras bate com a duração (±10%)?
- [ ] Todo fato tem fonte?
