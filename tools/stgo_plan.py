"""Plan de recorridos de Santiago (102 turnos = 51 días x 2, 5 abr–2 jun 2027, domingos de mercadito),
metas por sección y zonas. Usa la red de stgo_streets.py (calles INE)."""
import json, math, heapq, bisect, datetime as dt
from collections import defaultdict, Counter
OUT = '../out/'
D = json.load(open(OUT + 'dl02_data.json')); rings = D['sec_rings_wgs']; cbs = D['col_by_sec']
RES = {t['seccion']: t for t in json.load(open(OUT + 'dl02_resultados.json'))['table']}
R = json.load(open(OUT + 'stgo_red.json')); nodes = {int(k): v for k, v in R['nodes'].items()}
ZONES = [('Centro', [2086, 2087, 2088, 2089, 2090, 2091, 2105, 2110]), ('Norte · El Barro–Los Rodríguez', [2101, 2102, 2103, 2104]),
         ('Sur · Cieneguilla–San Pedro', [2092, 2093, 2094, 2095, 2096, 2097, 2098, 2099, 2100]), ('Sierra', [2106, 2107, 2108, 2109])]
assert sorted(s for _, z in ZONES for s in z) == sorted(RES)
# ---- metas (transparentes): crecer sobre el voto 2024 del bloque PRI-PAN-PRD según qué tan holgada fue la sección
tab = []
for s, t in sorted(RES.items()):
    fy = t['FyC (PAN-PRI-PRD)']; mg = t['margen_pts']
    cat, fac = ('Bastión', 1.10) if mg >= 55 else ('Defender', 1.15) if mg >= 40 else ('Empate', 1.25)
    meta = round(fy * fac)
    tab.append({'seccion': s, 'FyC': fy, 'MC': t['MC'], 'Morena': t['raw']['MORENA'], 'PT': t['PT'], 'PVEM': t['raw']['PVEM'], 'VIDA': t['VIDA'], 'PRI': t['raw']['PRI'], 'PAN': t['raw']['PAN'],
                'total': t['total'], 'ln': t['ln'], 'ganador': 'FyC', 'segundo': t['segundo'], 'margen': mg, 'cat': cat, 'meta': meta, 'delta': meta - fy})
by = {t['seccion']: t for t in tab}
# ---- red
K = 111320 * math.cos(math.radians(25.39))
def m(p): return (p[0] * K, p[1] * 110574)
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
adj = defaultdict(dict); seg_by_sec = defaultdict(list)
for a, b, s, nm, c, t in R['edges']:
    Lg = dist(m(nodes[a]), m(nodes[b]))
    if Lg == 0: continue
    adj[a][b] = (Lg, nm); adj[b][a] = (Lg, nm); seg_by_sec[s].append((a, b, Lg, c == 2, nm))
def dijkstra(src, maxd):
    d_ = {src: 0}; prev = {}; pq = [(0, src)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > d_.get(u, 1e18): continue
        if d > maxd: break
        for v, (Lg, nm) in adj[u].items():
            nd = d + Lg
            if nd < d_.get(v, 1e18): d_[v] = nd; prev[v] = u; heapq.heappush(pq, (nd, v))
    return d_, prev
def pth(prev, src, dst):
    p = [dst]
    while p[-1] != src: p.append(prev[p[-1]])
    return p[::-1]
JUMP = None  # marcador de traslado (salto sin caminar)
def full_walk(s, ref):
    req = {(min(a, b), max(a, b)) for a, b, Lg, door, nm in seg_by_sec[s] if door}
    if not req: return []
    cur = min((n for e in req for n in e), key=lambda n: dist(m(nodes[n]), ref)); walk = [cur]; done = set()
    while req - done:
        nxt = next((v for v in adj[cur] if (min(cur, v), max(cur, v)) in req and (min(cur, v), max(cur, v)) not in done), None)
        if nxt is not None: done.add((min(cur, nxt), max(cur, nxt))); walk.append(nxt); cur = nxt; continue
        d_, prev = dijkstra(cur, 1500)
        cand = [n for e in (req - done) for n in e if n in d_]
        if cand:
            n = min(cand, key=lambda n: d_[n]); p = pth(prev, cur, n)
            for a, b in zip(p, p[1:]):
                e = (min(a, b), max(a, b))
                if e in req: done.add(e)
            walk += p[1:]; cur = n
        else:  # otra parte de la sección: traslado
            n = min((n for e in (req - done) for n in e), key=lambda n: dist(m(nodes[n]), m(nodes[cur])))
            walk += [JUMP, n]; cur = n
    return walk
def cen(s):
    rg = max(rings[str(s)], key=len); return m((sum(p[0] for p in rg) / len(rg), sum(p[1] for p in rg) / len(rg)))
# orden dentro de cada zona: vecino más cercano
W = []; owner = []; zone_of = {}
last = cen(2086)
for zi, (zn, zs) in enumerate(ZONES):
    rem = set(zs)
    while rem:
        s = min(rem, key=lambda x: dist(cen(x), last)); rem.remove(s); zone_of[s] = zi + 1
        w = full_walk(s, m(nodes[W[-1]]) if W and W[-1] is not None else last)
        if not w: continue
        if W:
            d_, prev = dijkstra(W[-1], 2500)
            if w[0] in d_: link = pth(prev, W[-1], w[0])[1:-1]
            else: link = [JUMP]
            W += link; owner += [s] * len(link)
        W += w; owner += [s] * len(w); last = m(nodes[w[-1]])
# acumulado (los traslados no cuentan como caminata)
cum = [0]; prv = W[0]
for i in range(1, len(W)):
    a, b = W[i - 1], W[i]
    if a is None or b is None: cum.append(cum[-1])
    else: cum.append(cum[-1] + (adj[a][b][0] if b in adj[a] else dist(m(nodes[a]), m(nodes[b]))))
TOT = cum[-1]
d0 = dt.date(2027, 4, 5); end = dt.date(2027, 6, 2); work = []; suns = []
d = d0
while d <= end: (suns if d.weekday() == 6 else work).append(d); d += dt.timedelta(1)
NS = len(work) * 2
inter = [j for j in range(1, len(W) - 1) if W[j] is not None and len(adj[W[j]]) >= 3]
cuts = [0]
for q in range(1, NS):
    t = TOT * q / NS; k_ = bisect.bisect_left(inter, bisect.bisect_left(cum, t))
    cand = [inter[x] for x in (k_ - 1, k_) if 0 <= x < len(inter)]
    j = min(cand, key=lambda j: abs(cum[j] - t)) if cand else cuts[-1] + 1
    cuts.append(max(j, cuts[-1] + 1))
cuts.append(len(W) - 1)
door_sec = {(min(a, b), max(a, b)): s for s in seg_by_sec for a, b, Lg, door, nm in seg_by_sec[s] if door}
sessions = []
for q in range(NS):
    i0, i1 = cuts[q], cuts[q + 1]
    while W[i0] is None: i0 += 1
    piece = [n for n in W[i0:i1 + 1]]
    while piece and piece[-1] is None: piece.pop()
    secs = []; streets = []; coords = []; nmseq = []
    for k, n in enumerate(piece):
        if n is None: continue
        coords.append([round(nodes[n][0], 5), round(nodes[n][1], 5)])
        a = piece[k - 1] if k else None
        nm = adj[a][n][1] if a is not None and n in adj[a] else ''
        if k: nmseq.append(nm)
        s_ = door_sec.get((min(a, n), max(a, n))) if a is not None else None
        if s_ and s_ not in secs: secs.append(s_)
        if nm and nm not in streets: streets.append(nm)
    lenby = Counter(owner[j] for j in range(i0, i1 + 1))
    gmain = lenby.most_common(1)[0][0]
    sessions.append({'nmseq': nmseq, 'f': zone_of[gmain], 'secs': secs or [gmain], 'km': round((cum[i1] - cum[i0]) / 1000, 1), 'coords': coords, 'calles': streets[:40]})
span = defaultdict(list)
for q, s_ in enumerate(sessions):
    for x in s_['secs']: span[x].append(q)
for q, s_ in enumerate(sessions):
    lst = span[s_['secs'][0]]; s_['parte'] = '%d/%d' % (lst.index(q) + 1, len(lst))
FN = {i + 1: 'Fase %d · %s' % (i + 1, z[0]) for i, z in enumerate(ZONES)}
for i, s in enumerate(sessions):
    s['dia'] = i + 1; s['cal'] = i // 2 + 1; s['turno'] = 'Mañana' if i % 2 == 0 else 'Tarde'; s['pct'] = 100; s['fase'] = FN[s['f']]
    s['fecha'] = work[s['cal'] - 1].isoformat()
NT = sorted({n for s_ in sessions for n in s_['nmseq']}); NI = {n: i for i, n in enumerate(NT)}
for s_ in sessions: s_['nm'] = [NI[n] for n in s_.pop('nmseq')]
def col1(s): d_ = cbs.get(str(s), {}); return sorted(d_, key=lambda z: -d_[z])[0] if d_ else ''
merc = []
for sd in suns:
    wk = [s for s in sessions if sd < dt.date.fromisoformat(s['fecha']) <= sd + dt.timedelta(6)]
    secs = list(dict.fromkeys(x for s in wk for x in s['secs']))
    top = sorted(secs, key=lambda x: -by[x]['ln'])[:4]
    merc.append({'fecha': sd.isoformat(), 'secs': top, 'cols': [col1(x) for x in top], 'f': wk[0]['f'] if wk else 1})
json.dump({'days': sessions, 'merc': merc, 'NT': NT}, open(OUT + 'calles_days40.json', 'w'), ensure_ascii=False)
json.dump(tab, open(OUT + 'dl02_ruta.json', 'w'), ensure_ascii=False)
segs = [[list(nodes[a]), list(nodes[b])] for a, b, s, nm, c, t in R['edges']]
json.dump(segs, open(OUT + 'calles_segs.json', 'w'))
json.dump({'zones': [{'name': z[0], 'secs': z[1]} for z in ZONES], 'FN': FN}, open(OUT + 'stgo_zonas.json', 'w'), ensure_ascii=False)
ks = [s['km'] for s in sessions]
print('caminata %.0f km · turnos %d · km min/med/max %.1f/%.1f/%.1f' % (TOT / 1000, len(sessions), min(ks), sorted(ks)[len(ks) // 2], max(ks)))
print('por fase', Counter(s['f'] for s in sessions), 'secciones', len({x for s in sessions for x in s['secs']}), 'mercaditos', len(merc))
print('metas: votos por sumar', sum(t['delta'] for t in tab), Counter(t['cat'] for t in tab))
