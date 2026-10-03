#!/usr/bin/env python3
"""Gera os arquivos finais a partir de raw.psv (deduplicado por username normalizado)."""
import re, collections, os
NI = "não identificado"
DATA = "2026-10-03"
def norm(u):
    u = u.strip().lower()
    u = re.sub(r'^https?://', '', u); u = re.sub(r'^(www\.|m\.)', '', u)
    u = re.sub(r'^instagram\.com/', '', u); u = u.split('?')[0].split('/')[0]
    return u.lstrip('@')
def v(x): x = x.strip(); return NI if x in ('', '-', NI) else x
seen, rows, dup, bruto = {}, [], 0, 0
for line in open('raw.psv', encoding='utf-8'):
    p = line.rstrip('\n').split('|')
    if len(p) != 10: continue
    bruto += 1
    u = norm(p[0])
    if not re.fullmatch(r'[a-z0-9._]{1,30}', u): continue
    if u in seen: dup += 1; continue
    seen[u] = 1; rows.append([u] + [v(x) for x in p[1:]])
hdr = "ID | INSTAGRAM_USUARIO | INSTAGRAM_URL | STATUS_INSTAGRAM | NOME | NOME_COMERCIAL | ATIVIDADE | CATEGORIA | ESPECIALIDADE | CIDADE | BAIRRO | ENDERECO | CEP | TELEFONE | WHATSAPP | STATUS_WHATSAPP | EMAIL_PROFISSIONAL | SITE | FACEBOOK | LINKEDIN | GOOGLE_MAPS | AVALIACAO_GOOGLE | QUANTIDADE_AVALIACOES | EVIDENCIA_DE_GENERO | FONTE_INSTAGRAM | FONTE_WHATSAPP | FONTE_PRINCIPAL | FONTES_ADICIONAIS | FERRAMENTA_ORIGEM | DATA_CONSULTA"
full, short = [hdr], ["INSTAGRAM_USUARIO | INSTAGRAM_URL | NOME | ATIVIDADE | CIDADE | BAIRRO | STATUS_INSTAGRAM"]
st = collections.Counter(); city = collections.Counter(); cat = collections.Counter(); ativ = collections.Counter(); bai = collections.Counter()
comb = collections.Counter()
for i, (u, nome, at, ca, ci, ba, tel, wa, ev, gen) in enumerate(rows, 1):
    status = "CONFIRMADO PUBLICAMENTE" if ev == 'B' else "PROVÁVEL — NÃO CONFIRMADO"
    fonte = ("Perfil público do Instagram (bio/nome/localização citam a cidade) via resultado de busca TinyFish" if ev == 'B'
             else "Resultado de busca TinyFish para a cidade; cidade não citada na bio indexada")
    url = f"https://www.instagram.com/{u}/"
    swa = "CONFIRMADO PUBLICAMENTE (indicação textual/wa.me na bio)" if wa != NI else NI
    fwa = "Bio pública do Instagram (trecho indexado)" if wa != NI else NI
    gen = f'texto público: "{gen}"' if gen != NI else NI
    full.append(" | ".join(map(str, [i, '@'+u, url, status, nome, nome, at, ca, at, ci, ba, NI, NI, tel, wa, swa, NI, NI, NI, NI, NI, NI, NI, gen, fonte, fwa, "Instagram (perfil público)", NI, "TinyFish", DATA])))
    short.append(" | ".join(['@'+u, url, nome, at, ci, ba, status]))
    st[status]+=1; city[ci]+=1; cat[ca]+=1; ativ[at]+=1; bai[f"{ci} / {ba}"]+=1
    comb['WA'] += wa != NI; comb['TEL'] += tel != NI; comb['WA+TEL'] += wa != NI and tel != NI
open('../instagram_profissionais_leste_rj_20k.txt','w',encoding='utf-8').write("\n".join(full)+"\n")
open('../instagram_apenas_leste_rj_20k.txt','w',encoding='utf-8').write("\n".join(short)+"\n")
n = len(rows); pct = lambda k: f"{k} ({100*k/n:.1f}%)" if n else "0"
conf = st["CONFIRMADO PUBLICAMENTE"]
nA = sum(1 for r in rows if r[8]=='B' and r[7]!=NI); nB = sum(1 for r in rows if r[8]=='B' and r[7]==NI and r[6]!=NI)
R = [f"RELATÓRIO — Instagrams profissionais Leste Fluminense (data {DATA})", "",
 f"TOTAL BRUTO DE PERFIS ENCONTRADOS: {bruto}", f"TOTAL DE INSTAGRAMS ÚNICOS: {n}",
 f"TOTAL DE INSTAGRAMS CONFIRMADOS: {conf}", f"TOTAL DE INSTAGRAMS PROVÁVEIS: {n-conf}",
 "TOTAL DESCARTADO: posts/reels, perfis de mídia/notícia e perfis fora da região não foram registrados (não contabilizados individualmente)",
 f"TOTAL DE DUPLICATAS REMOVIDAS: {dup}", f"TOTAL FINAL: {n}", "META: 20.000+", f"META ATINGIDA: {'SIM' if n>=20000 else 'NÃO'}", "",
 "TOTAL POR CIDADE:"] + [f"  {k}: {c}" for k,c in city.most_common()] + ["", "TOTAL POR CATEGORIA:"] + [f"  {k}: {c}" for k,c in cat.most_common()] + \
 ["", "TOTAL POR FERRAMENTA:", f"  TINYFISH: {n}", "  APIFY: 0 (não conectado nesta sessão)", "  OUTSCRAPER: 0 (não conectado nesta sessão)", "  FIRECRAWL: 0 (disponível; não usado nesta rodada)", "",
 "COMBINAÇÕES:", f"  INSTAGRAM + WHATSAPP: {pct(comb['WA'])}", f"  INSTAGRAM + TELEFONE: {pct(comb['TEL'])}", f"  INSTAGRAM + WHATSAPP + TELEFONE: {pct(comb['WA+TEL'])}",
 "  INSTAGRAM + SITE / EMAIL / GOOGLE MAPS: 0 (rodada de enriquecimento não executada)", "",
 "NÍVEIS:", f"  A (IG confirmado + WhatsApp): {nA}", f"  B (IG confirmado + telefone): {nB}", f"  C (IG confirmado, sem contato): {conf-nA-nB}", f"  D (IG provável): {n-conf}", "",
 "TOTAL POR BAIRRO:"] + [f"  {k}: {c}" for k,c in bai.most_common()] + ["", "TOTAL POR ATIVIDADE:"] + [f"  {k}: {c}" for k,c in ativ.most_common()]
open('../relatorio_instagram_leste_rj.txt','w',encoding='utf-8').write("\n".join(R)+"\n")
print("\n".join(R[:12]))
