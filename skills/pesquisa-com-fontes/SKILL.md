---
name: pesquisa-com-fontes
description: Use ao pesquisar a pauta de um vídeo, para levantar fatos com fontes confiáveis, separar fato de lenda e entregar o briefing que o roteirista e o revisor usam. Usada pelo pesquisador-pautas e pelo revisor-qualidade.
---
# 🔎 Pesquisa com fontes

## Hierarquia de fontes (da mais forte para a mais fraca)
1. Documento primário: arquivo oficial, processo, artigo científico, relatório de governo.
2. Imprensa de referência, enciclopédias com referências, livros de autor especialista.
3. Museus, universidades, sites institucionais.
4. Blogs, fóruns, vídeos de outros canais → **só para achar pistas**, nunca como fonte final.

## Regras
- Cada fato-chave com **pelo menos 2 fontes independentes** (3 se for surpreendente).
- Registre link, título e data de acesso.
- Classifique cada item: ✅ fato confirmado · 🟡 versão contestada (mostre os lados) · 🔮 lenda/teoria (o roteiro precisa dizer que é lenda).
- Números e datas: copie exatamente da fonte. Divergência entre fontes → registre as duas.
- Nunca invente. Sem fonte = fora do roteiro.

## Como buscar
1. `WebSearch` com o tema em PT e em EN (fontes em inglês costumam ser mais completas).
2. `WebFetch` nas 5–8 melhores páginas; leia, não confie só no resumo da busca.
3. Procure o "detalhe estranho" que vira gancho e a "virada" que vira clímax.
4. Procure o que o público já viu: se 3 grandes canais já fizeram, ache um ângulo novo.

## Formato do `briefing.md`
```markdown
# Briefing: <tema>
## Ideias ranqueadas
| # | Ideia | Gancho em 1 linha | Busca | Concorrência | Nota |
## Pauta escolhida
**Ângulo:** ...  **Gancho:** ...  **Virada:** ...
## Fatos
| id | Fato | Status | Fontes |
| f1 | Três faroleiros sumiram em 15/12/1900 | ✅ | [1], [2] |
## Linha do tempo
## Pontos sensíveis (⚠️ política, saúde, pessoas vivas)
## Fontes
[1] Título — link — acessado em AAAA-MM-DD
```
O roteirista cita `briefing.md#f1`; o revisor confere por esse id.
