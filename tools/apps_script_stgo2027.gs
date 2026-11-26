/**
 * STGO 2027 · Gestorías en tiempo real
 * Pegar en la hoja de Google: Extensiones → Apps Script → reemplazar todo con este código.
 * 1) Cambia TOKEN por una clave tuya (la misma que pondrás en la app, en Más → Hoja de gestorías).
 * 2) Implementar → Nueva implementación → Tipo: Aplicación web
 *      Ejecutar como: Yo · Quién tiene acceso: Cualquier usuario
 * 3) Copia la URL que termina en /exec y pégala en la app.
 *
 * La app manda filas; cada gestoría se actualiza en su misma fila (por ID).
 * Las columnas de SEGUIMIENTO TELEFÓNICO son del equipo: la app nunca las sobrescribe.
 * Reglas: las gestorías nunca se condicionan al voto; no se guarda preferencia política.
 */
const TOKEN = 'CAMBIA-ESTA-CLAVE';
const HOJA = 'Gestorías';
const COLS_APP = ['Folio', 'ID', 'Fecha de alta', 'Tipo', 'Urgencia', 'Etapa', 'Días para resolver', 'Sección', 'Colonia',
  'Dirección', 'Nombre', 'Teléfono', 'WhatsApp', '¿Aceptó que lo contactemos?', 'Detalle', 'Quién la resuelve (dependencia)',
  'Responsable', 'Folio de la dependencia', 'Último avance', 'Historial', 'Ubicación', 'Quién la recibió', 'Última actualización'];
const COLS_EQUIPO = ['Llamada de seguimiento (fecha)', 'Quién llamó', 'Resultado de la llamada', '¿Quedó satisfecho?', 'Notas del equipo'];

function hoja_() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(HOJA);
  if (!sh) sh = ss.insertSheet(HOJA);
  if (sh.getLastRow() === 0) {
    const H = COLS_APP.concat(COLS_EQUIPO);
    sh.getRange(1, 1, 1, H.length).setValues([H]).setFontWeight('bold').setWrap(true);
    sh.getRange(1, 1, 1, COLS_APP.length).setBackground('#c8102e').setFontColor('#ffffff');
    sh.getRange(1, COLS_APP.length + 1, 1, COLS_EQUIPO.length).setBackground('#009a44').setFontColor('#ffffff');
    sh.setFrozenRows(1); sh.setFrozenColumns(1);
    const n = 1000, c0 = COLS_APP.length + 1;
    sh.getRange(2, c0 + 2, n, 1).setDataValidation(SpreadsheetApp.newDataValidation()
      .requireValueInList(['Contestó', 'No contestó', 'Número equivocado', 'Pidió no ser contactado'], true).build());
    sh.getRange(2, c0 + 3, n, 1).setDataValidation(SpreadsheetApp.newDataValidation()
      .requireValueInList(['Sí', 'Más o menos', 'No'], true).build());
    sh.getRange(2, c0, n, 1).setNumberFormat('dd/mm/yyyy');
  }
  return sh;
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const d = JSON.parse(e.postData.contents);
    if (d.tok !== TOKEN) return out_({ ok: false, err: 'token' });
    const sh = hoja_();
    const last = sh.getLastRow();
    const ids = last > 1 ? sh.getRange(2, 2, last - 1, 1).getValues().map(r => String(r[0])) : [];
    const ahora = new Date();
    (d.rows || []).forEach(r => {
      const row = r.slice(0, COLS_APP.length);
      row[2] = new Date(Number(row[2]));                              // fecha de alta
      if (row[6] === null) row[6] = '';                                // días: solo cuando se resuelve
      row[COLS_APP.length - 1] = ahora;                                // última actualización
      for (let k = 0; k < row.length; k++) if (row[k] === null) row[k] = '';
      if (typeof row[11] === 'string' && row[11]) row[11] = "'" + row[11]; // teléfono como texto
      const i = ids.indexOf(String(row[1]));
      if (i >= 0) sh.getRange(i + 2, 1, 1, row.length).setValues([row]);
      else { sh.appendRow(row); ids.push(String(row[1])); }
    });
    (d.del || []).forEach(id => {
      const i = ids.indexOf(String(id));
      if (i >= 0) sh.getRange(i + 2, 6).setValue('Borrada en la app');
    });
    return out_({ ok: true });
  } catch (err) {
    return out_({ ok: false, err: String(err).slice(0, 120) });
  } finally { lock.releaseLock(); }
}

function doGet() { return out_({ ok: true, app: 'STGO 2027' }); }
function out_(o) { return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }
