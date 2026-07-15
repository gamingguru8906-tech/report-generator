/**
 * Veshann Astro — Orders sheet cleaner
 * -----------------------------------------------------------------------------
 * Fixes two things in the Orders sheet:
 *   1) Writes a clean, correct 24-column header (A..X).
 *   2) Converts serial-number timestamps / DOBs (e.g. 46216.67, 46205) that were
 *      stored via USER_ENTERED back into readable TEXT, and locks those columns
 *      to plain-text so they never coerce to a serial again.
 *
 * HOW TO USE
 *   1. Open your Google Sheet.
 *   2. Extensions -> Apps Script.
 *   3. Delete any sample code, paste this whole file, click Save.
 *   4. Select the function "fixOrdersSheet" in the toolbar dropdown, click Run.
 *   5. Approve the permission prompt the first time. Done.
 *
 * Safe to run multiple times (idempotent). It only touches the header row and
 * the date/timestamp columns; all other data is left exactly as-is.
 */

var SHEET_NAME = 'Orders';   // change if your tab is named differently

var HEADERS = [
  'Timestamp', 'Order ID', 'Name', 'DOB', 'Email', 'Gender', 'Report Type', 'Extra',
  'Birth Time', 'Birth Place', 'Focus Area', 'Partner Name', 'Partner DOB',
  'Partner Birth Time', 'Partner Birth Place', 'Marriage Date', 'Current Issue',
  'Children', 'Main Question', 'Report URL', 'Status', 'Status Time', 'Error', 'Pipeline'
];

// Column numbers (1-based) that hold date/time values.
var DATETIME_COLS = [1, 22];   // A = Timestamp, V = Status Time
var DATE_COLS     = [4, 13];   // D = DOB,       M = Partner DOB

function fixOrdersSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME) || ss.getActiveSheet();
  var tz = ss.getSpreadsheetTimeZone() || 'Asia/Kolkata';

  // 1) Header row -------------------------------------------------------------
  sh.getRange(1, 1, 1, HEADERS.length)
    .setValues([HEADERS])
    .setFontWeight('bold');
  sh.setFrozenRows(1);

  var lastRow = sh.getLastRow();
  var n = lastRow - 1;
  if (n < 1) {
    ss.toast('Header set. No data rows to convert.', 'Veshann', 5);
    return;
  }

  // Google Sheets serial date -> JS Date (epoch is 1899-12-30).
  function fromSerial(num) {
    var d = new Date(1899, 11, 30, 0, 0, 0, 0);
    var whole = Math.floor(num);
    var frac = num - whole;
    d.setDate(d.getDate() + whole);
    d.setTime(d.getTime() + Math.round(frac * 86400000));
    return d;
  }
  function toText(v, fmt) {
    if (v === '' || v === null || v === undefined) return v;   // keep blanks
    if (v instanceof Date) return Utilities.formatDate(v, tz, fmt);
    if (typeof v === 'number') return Utilities.formatDate(fromSerial(v), tz, fmt);
    return v;                                                  // already text
  }

  // 2) Convert each date/time column to readable text -------------------------
  function convertColumn(col, fmt) {
    var rng = sh.getRange(2, col, n, 1);
    var vals = rng.getValues();
    for (var i = 0; i < vals.length; i++) vals[i][0] = toText(vals[i][0], fmt);
    rng.setNumberFormat('@');      // lock to plain text
    rng.setValues(vals);
  }
  DATETIME_COLS.forEach(function (c) { convertColumn(c, 'yyyy-MM-dd HH:mm:ss'); });
  DATE_COLS.forEach(function (c) { convertColumn(c, 'dd MMMM yyyy'); });

  // 3) A little tidiness ------------------------------------------------------
  try { sh.autoResizeColumns(1, HEADERS.length); } catch (e) {}

  ss.toast('Cleaned ' + n + ' rows: header fixed, dates/timestamps are now text.',
           'Veshann', 6);
}
