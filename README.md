# STGO 2027 · app de campaña · Santiago, N.L. (Ayuntamiento 2027)

Hecha a partir de la app DL02 (repo `ruta-dl02`, rama `fuente`), **sin tocarla**. Claves de almacenamiento propias (`stgo27v1`, `stgo27photos`, caché `stgo27-*`), así que nunca se mezcla con la DL02 aunque se abran en el mismo teléfono.

- `out/site/` → lo que se publica (GitHub Pages): `index.html`, `app.js`, `data.js`, `sw.js`, `manifest.webmanifest`, íconos.
- Candidato: Jorge Espronceda (PRI). Color principal rojo PRI `#c8102e`. Mascota provisional: "Jorgito" (`tools/mascot.svg`).
- Hoja de Google: `tools/apps_script_stgo2027.gs` (instrucciones dentro).

## Cómo se regenera (desde `tools/`)
1. `python3 dl02.py` — secciones y colonias del **municipio 49 (Santiago)** → `out/dl02_data.json` (25 secciones, 2086–2110).
2. `python3 results.py ../res/NL_AYUN_2024.xlsx` — Ayuntamiento 2024 por sección → `out/dl02_resultados.json`.
3. `python3 stgo_streets.py` — calles de la cartografía INE (`shp/VIALIDAD`) → `out/stgo_red.json` (sustituye el export.osm).
4. `python3 stgo_plan.py` — metas por sección, zonas (Centro, Norte, Sur, Sierra), 102 turnos del 5 abr al 2 jun 2027 y domingos de mercadito.
5. Desde la raíz: `python3 casillas/stgo_casillas_geo.py && python3 casillas/stgo_casillas_pack.py` — 75 casillas (25 domicilios), solo domicilios.
6. `python3 build_app3.py` → `out/site/`.

`stgo_patch.py` es el parche que ya se aplicó a los .js copiados de la DL02 (no volver a correr).

## Metas por sección (editables en `stgo_plan.py`)
Votos 2024 del bloque PRI-PAN-PRD × 1.10 (margen ≥ 55 pts), × 1.15 (40–55) o × 1.25 (< 40).

## Reglas que se mantienen
- No guardar nombres de funcionarios de casilla (el PDF del INE no se incluye; solo `casillas/raw_stgo.json` con domicilios).
- Nunca cargar la lista nominal.
- Las gestorías nunca se condicionan al voto.
- Nada de envíos automáticos por WhatsApp: los botones solo abren el chat para que una persona escriba.
