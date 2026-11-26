"""Adapta el código de la DL02 a STGO 2027 (Santiago, N.L.). Correr una sola vez sobre los .js copiados."""
import re, json
FILES = ['app3.js', 'org.js', 'dd.js', 'fis.js', 'v5.js', 'v6.js', 'v7.js', 'v8.js', 'build_app3.py']
src = {f: open(f).read() for f in FILES}
def rep(f, old, new, cnt=None):
    s = src[f]; n = s.count(old)
    assert n and (cnt is None or n == cnt), (f, old[:60], n)
    src[f] = s.replace(old, new)
def allrep(old, new):
    hit = 0
    for f in FILES:
        if old in src[f]: src[f] = src[f].replace(old, new); hit += 1
    assert hit, old
ZONES = json.load(open('../out/stgo_zonas.json'))
# --- claves de almacenamiento propias (no se mezclan con la DL02)
for a, b in [("'dl02v3_bk_'", "'stgo27v1_bk_'"), ("'dl02v3'", "'stgo27v1'"), ("'dl02v2'", "'stgo27v0'"), ("'dl02photos'", "'stgo27photos'"), ("'dl02_ok'", "'stgo27_ok'"), ("'dl02-tiles'", "'stgo27-tiles'"), ("const V='dl02-", "const V='stgo27-")]:
    allrep(a, b)
# --- candidato y mascota
allrep('David de la Peña', 'Jorge Espronceda'); allrep('Davidsito', 'Jorgito'); allrep('David', 'Jorge')
rep('org.js', 'Candidato · Diputación local DL02', 'Candidato · Presidencia municipal de Santiago')
rep('org.js', "slot('sup','Diputado(a) suplente','Fórmula con Jorge Espronceda',true)", "slot('sup','Planilla (síndicos y regidores)','Planilla de Jorge Espronceda',true)")
rep('org.js', "['Direccion','','','Diputado(a) supl", "['Direccion','','','Planilla (síndicos y regidores) supl")
allrep('Diputación local', 'Presidencia municipal')
# --- territorio
allrep('Distrito 02', 'Santiago'); allrep('estructura_DL02', 'estructura_STGO2027')
for a in ['respaldo_DL02_', 'registros_DL02_', 'gestorias_DL02_', 'dia_d_DL02', 'agenda_DL02', 'gastos_DL02']: allrep(a, a.replace('DL02', 'STGO2027'))
allrep('DL02', 'STGO 2027')
allrep('343 casillas', '75 casillas')
allrep('fuera del distrito', 'fuera del municipio'); allrep('Fuera del distrito', 'Fuera del municipio')
rep('org.js', 'casillas en el distrito', 'casillas en el municipio'); rep('dd.js', 'Estimación simple del distrito', 'Estimación simple del municipio')
rep('org.js', 'Ej. 1012 o Mitras', 'Ej. 2101 o El Barro')
rep('v7.js', "'Servicios Públicos (Monterrey)'", "'Servicios Públicos (Santiago)'")
rep('v5.js', "'🗳 Santiago</div>", "'🗳 Santiago 2027</div>") if "'🗳 Santiago</div>" in src['v5.js'] else None
# --- fiscalización: tope de Santiago por capturar
rep('fis.js', 'tope:1503662.51', "tope:0")
src['fis.js'] = re.sub(r"El tope de 2024 para el Distrito 2 fue de \$1,503,662\.51; actualízalo[^']*", 'Captura el tope de gastos de campaña para el Ayuntamiento de Santiago que apruebe el IEEPCNL para 2027.', src['fis.js'])
src['fis.js'] = re.sub(r"2024, Distrito 2: \$1,503,662\.51 \(acuerdo IEEPCNL/CG/102/2023\)\. Pon el de 2027 cuando[^<']*", 'Pon el tope 2027 del Ayuntamiento de Santiago cuando lo apruebe el IEEPCNL.', src['fis.js'])
assert 'Distrito 2' not in src['fis.js']
# --- fases = zonas del municipio
FN = '{' + ','.join("%d:'%s'" % (int(k), v) for k, v in ZONES['FN'].items()) + '}'
rep('app3.js', "const FN={1:'Fase 1 · Zona a favor',2:'Fase 2 · Zonas en empate',3:'Fase 3 · Zonas por recuperar'},CM={1:'#1d4f9c',2:'#1d4f9c',3:'#1d4f9c'};",
    "const FN=" + FN + ",CM={1:'#c8102e',2:'#c8102e',3:'#c8102e',4:'#c8102e'};")
# --- partidos: el bloque ganador de 2024 en Santiago fue PRI-PAN-PRD
rep('app3.js', "FyC:{c:'#1d4f9c',n:'Ganó Fuerza y Corazón',s:'Fuerza y Corazón'}", "FyC:{c:'#c8102e',n:'Ganó PRI-PAN-PRD',s:'PRI-PAN-PRD'}")
rep('app3.js', "PT:{c:'#d52b1e'", "PT:{c:'#e0a800'")
rep('app3.js', "'Fuerza y Corazón (PAN-PRI-PRD)'", "'PRI-PAN-PRD (Fuerza y Corazón)'")
allrep('#1f5fbf', '#c8102e'); allrep('#c62828', '#e0a800')
rep('dd.js', "'Jorge (coalición)'", "'Jorge (PRI y aliados)'")
src['app3.js'] = src['app3.js'].replace("'2024: FyC '", "'2024: PRI-PAN-PRD '")
# --- color principal: rojo PRI
for f in FILES: src[f] = src[f].replace('#1d4f9c', '#c8102e').replace('1d4f9c', 'c8102e')
# --- propuestas (borrador editable, sin cifras no verificadas)
i = src['org.js'].index('const PROP0=['); j = src['org.js'].index('if(!S.props)')
PROPS = r"""const PROP0=[
 {id:'serv',ico:'💡',t:'Servicios que sí llegan',f:'Lámpara reportada, lámpara reparada; bache reportado, bache tapado. Con folio y fecha.',
  p:'BORRADOR para editar: describe aquí, con datos verificados, el problema de alumbrado, baches y recolección de basura en las congregaciones y colonias de Santiago.',
  b:['Reporte con folio y tiempo máximo de atención para alumbrado, baches y basura.','Mapa público de reportes atendidos y pendientes por colonia y congregación.','Cuadrillas por zona: Centro, Norte, Sur y Sierra.'],
  c:'BORRADOR: competencia directa del Ayuntamiento (servicios públicos municipales).',cats:['Alumbrado','Basura','Calles']},
 {id:'agua',ico:'💧',t:'Agua y drenaje en cada congregación',f:'Que ninguna congregación se quede sin agua sin aviso ni pipa.',
  p:'BORRADOR para editar: problema del agua y drenaje en Santiago, con fuente.',
  b:['Aviso previo de cortes por colonia y pipa garantizada.','Gestión ante Agua y Drenaje de Monterrey de las obras pendientes del municipio.','Atención especial a las comunidades de la Sierra.'],
  c:'BORRADOR: coordinación del Ayuntamiento con Agua y Drenaje de Monterrey.',cats:['Agua','Drenaje']},
 {id:'cerca',ico:'🤝',t:'Presidencia en tu colonia',f:'Un sábado al mes en tu zona, y cada gestoría con folio y respuesta.',
  p:'En 2024 votó el 60% del padrón de Santiago (26,773 de 44,318 electores). La gente quiere ver a sus autoridades fuera de campaña.',
  b:['Módulo de atención itinerante: un sábado al mes en cada una de las 4 zonas del municipio.','Cada gestoría con folio y respuesta en un máximo de 30 días, con seguimiento por WhatsApp.','Informe público cada 3 meses por colonia y congregación: qué se pidió y qué se resolvió.'],
  c:'Compromiso de campaña que se opera desde la Presidencia Municipal. Esta misma app ya lleva el registro y seguimiento de gestorías.',cats:null}];
"""
src['org.js'] = src['org.js'][:i] + PROPS + src['org.js'][j:]
# --- textos que quedaron con "distrito"
for f in FILES:
    src[f] = src[f].replace('del distrito', 'del municipio').replace('el distrito', 'el municipio').replace('en distrito', 'en el municipio')
for f in FILES: open(f, 'w').write(src[f])
left = {f: sorted(set(re.findall(r"(?i)distrito|dl02|monterrey|mitras|topo chico|peña", src[f]))) for f in FILES}
print({k: v for k, v in left.items() if v})
