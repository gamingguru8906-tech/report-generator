"""The owner's "Make a report" page (GET /admin/make).

For orders that come in on WhatsApp and are paid outside the website: the owner picks the report, types the
customer's details, and the server builds the same PDF a paid website order gets. The page then hands the PDF
to the phone's share sheet (WhatsApp, straight to the customer's chat), or downloads it.

The page itself holds no data. Every call it makes carries the admin pass in a request header, and the pass is
kept only in this browser's storage on the owner's phone.
"""
import json

# per report: the extra inputs it needs (key, label, type, required, hint)
FIELDS = {
    "forecast": [],
    "forecast_blend": [],
    "complete": [],
    "mobile": [("number", "Mobile number to read", "tel", False, "Leave empty to read the customer's WhatsApp number")],
    "name": [("check_name", "Name to check", "text", False, "Optional: a new spelling or a nickname")],
    "business": [("business", "Business name", "text", True, "")],
    "baby": [("baby", "Preferences", "text", False, "Optional: starting letter, gender, family names")],
    "love": [("partner_name", "Partner's name", "text", True, ""), ("partner_dob", "Partner's date of birth", "date", True, "")],
    "house": [("number", "House number", "text", True, "")],
    "vehicle": [("number", "Vehicle number", "text", True, "")],
    "snapshot": [("question", "Customer's question", "text", False, "Optional")],
    "career": [("question", "Customer's question", "text", False, "Optional")],
    "money": [("question", "Customer's question", "text", False, "Optional")],
    "astrology_life_path": [("birth_time", "Birth time", "time", True, ""), ("birth_place", "Birth place", "text", True, "City, state"),
                            ("focus_area", "Focus area", "text", False, "Optional: career, marriage, health"),
                            ("main_question", "Main question", "text", False, "Optional")],
    "divorce_separation_report": [("birth_time", "Birth time", "time", True, ""), ("birth_place", "Birth place", "text", True, "City, state"),
                                  ("partner_name", "Partner's name", "text", True, ""), ("partner_dob", "Partner's date of birth", "date", True, ""),
                                  ("marriage_date", "Marriage date", "date", False, "Optional"),
                                  ("current_issue", "Current issue", "text", False, "Optional"),
                                  ("children", "Children", "text", False, "Optional"),
                                  ("main_question", "Main question", "text", False, "Optional")],
}

PAGE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Make a report</title>
<style>
:root{--bg:#FAF7F5;--card:#FFFFFF;--ink:#26222A;--soft:#6B6470;--line:#E7E0E4;--pink:#D63FAF;--pink-l:#FBE3F5;--ok:#1F7A4D;--bad:#B4231C}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
main{max-width:540px;margin:0 auto;padding:22px 16px 60px}
h1{font-size:24px;margin:0 0 4px}
.sub{color:var(--soft);font-size:14px;margin:0 0 20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px 16px;margin-bottom:16px}
label{display:block;font-size:13.5px;font-weight:600;margin:14px 0 6px}
label:first-child{margin-top:0}
.hint{font-weight:400;color:var(--soft)}
input,select{width:100%;font:inherit;padding:11px 12px;border:1px solid #D5CCD2;border-radius:6px;background:#fff;color:var(--ink)}
input:focus,select:focus{outline:2px solid var(--pink);outline-offset:0;border-color:var(--pink)}
.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.row label{margin-top:14px}
button,.btn{display:block;width:100%;font:inherit;font-weight:600;padding:13px 14px;border-radius:6px;border:1px solid var(--pink);background:var(--pink);color:#fff;cursor:pointer;text-align:center;text-decoration:none;margin-top:10px}
button.alt,.btn.alt{background:#fff;color:var(--pink)}
button:disabled{opacity:.55;cursor:default}
.chk{display:flex;gap:10px;align-items:center;font-weight:400;margin-top:14px}
.chk input{width:auto}
.status{font-size:15px}
.status b{display:block;font-size:17px;margin-bottom:4px}
.bar{height:6px;background:var(--pink-l);border-radius:3px;overflow:hidden;margin:12px 0 2px}
.bar i{display:block;height:100%;width:30%;background:var(--pink);animation:mv 1.6s ease-in-out infinite}
@keyframes mv{0%{margin-left:-30%}100%{margin-left:100%}}
.err{color:var(--bad)}
.okc{color:var(--ok)}
.recent div{display:flex;justify-content:space-between;gap:10px;padding:10px 0;border-top:1px solid var(--line);font-size:14px}
.recent div:first-child{border-top:0}
.recent a{color:var(--pink);font-weight:600;white-space:nowrap}
.small{font-size:13px;color:var(--soft)}
.hide{display:none}
a.link{color:var(--pink)}
body.embed{--pink:#C2185B;--pink-l:#FCE7EF;background:#FBF7F8}
body.embed h1,body.embed .sub{display:none}
body.embed main{padding-top:16px}
</style></head><body><main>
<h1>Make a report</h1>
<p class="sub">For WhatsApp orders. Builds the same PDF a website order gets, ready to send to the customer.</p>

<div class="card" id="keyCard">
  <label for="key">Admin pass <span class="hint">(ADMIN_PASS on Render, saved on this phone only)</span></label>
  <input id="key" type="password" autocomplete="off">
  <button id="saveKey" type="button">Continue</button>
</div>

<form class="card hide" id="form" autocomplete="off">
  <label for="product">Report</label>
  <select id="product"></select>
  <label for="name">Customer's full name</label>
  <input id="name" required>
  <div class="row">
    <div><label for="dob">Date of birth</label><input id="dob" type="date" required></div>
    <div><label for="gender">Gender</label><select id="gender"><option value="">Not given</option><option value="female">Female</option><option value="male">Male</option></select></div>
  </div>
  <label for="phone">Customer's WhatsApp number <span class="hint" id="phoneHint">(adds the free mobile reading to the forecast)</span></label>
  <input id="phone" type="tel" inputmode="numeric" placeholder="10 digits">
  <div id="extra"></div>
  <label class="chk"><input id="sendEmail" type="checkbox"> Also email it to the customer</label>
  <div id="emailBox" class="hide"><label for="email">Customer's email</label><input id="email" type="email"></div>
  <button id="go" type="submit">Make report</button>
  <p class="small" style="margin:12px 0 0">Takes about a minute. If the server was asleep, the first one can take two.</p>
</form>

<div class="card hide" id="job"></div>

<div class="card hide" id="recentCard"><label>Made recently</label><div class="recent" id="recent"></div></div>

<p class="small" id="forget" style="text-align:center"><a href="#" class="link">Forget the admin pass on this phone</a></p>
</main>
<script>
const PRODUCTS = __PRODUCTS__;
const FIELDS = __FIELDS__;
const $ = id => document.getElementById(id);
if (new URLSearchParams(location.search).get("embed")) document.body.classList.add("embed");   // inside the Kamala dashboard
let KEY = ""; try { KEY = localStorage.getItem("va_admin_pass") || ""; } catch (e) {}
let job = null, pdfBlob = null, poll = null;

function headers() { return {"Content-Type": "application/json", "X-Admin-Pass": KEY}; }
async function api(path, opts) {
  const r = await fetch(path, Object.assign({headers: headers()}, opts || {}));
  if (r.status === 403) { showKey("That admin pass was not accepted."); throw new Error("key"); }
  const t = await r.text(); let d = {}; try { d = JSON.parse(t); } catch (e) { d = {detail: t}; }
  if (!r.ok) throw new Error(d.detail || ("Server error " + r.status));
  return d;
}
function showKey(msg) {
  $("keyCard").classList.remove("hide"); $("form").classList.add("hide");
  if (msg) { let p = $("keyMsg"); if (!p) { p = document.createElement("p"); p.id = "keyMsg"; p.className = "err small"; $("keyCard").appendChild(p); } p.textContent = msg; }
}
function showForm() { $("keyCard").classList.add("hide"); $("form").classList.remove("hide"); loadRecent(); }

$("saveKey").onclick = () => { KEY = $("key").value.trim(); if (!KEY) return; try { localStorage.setItem("va_admin_pass", KEY); } catch (e) {} showForm(); };
$("forget").querySelector("a").onclick = e => { e.preventDefault(); try { localStorage.removeItem("va_admin_pass"); } catch (er) {} KEY = ""; $("key").value = ""; showKey(); };
$("sendEmail").onchange = () => $("emailBox").classList.toggle("hide", !$("sendEmail").checked);

for (const [k, label, ready] of PRODUCTS) { const o = document.createElement("option"); o.value = k; o.textContent = label + (ready ? "" : " (not ready yet)"); o.disabled = !ready; $("product").appendChild(o); }
function drawExtra() {
  const k = $("product").value, box = $("extra"); box.innerHTML = "";
  for (const [key, label, type, req, hint] of (FIELDS[k] || [])) {
    const l = document.createElement("label"); l.htmlFor = "x_" + key; l.textContent = label + " ";
    if (hint) { const s = document.createElement("span"); s.className = "hint"; s.textContent = "(" + hint + ")"; l.appendChild(s); }
    const i = document.createElement("input"); i.id = "x_" + key; i.type = type; i.required = !!req; i.dataset.key = key;
    box.appendChild(l); box.appendChild(i);
  }
  $("phoneHint").textContent = k === "forecast" ? "(adds the free mobile reading to the forecast)" : k === "complete" ? "(adds the mobile number section)" : "(for opening the chat)";
}
$("product").onchange = drawExtra; drawExtra();

$("form").onsubmit = async e => {
  e.preventDefault();
  const body = {product: $("product").value, name: $("name").value.trim(), dob: $("dob").value, gender: $("gender").value,
                phone: $("phone").value.trim(), email: $("sendEmail").checked ? $("email").value.trim() : ""};
  for (const i of $("extra").querySelectorAll("input")) body[i.dataset.key] = i.value.trim();
  $("go").disabled = true;
  try {
    const d = await api("/admin/make-report", {method: "POST", body: JSON.stringify(body)});
    job = d; pdfBlob = null; drawJob(d); clearInterval(poll); poll = setInterval(check, 4000);
  } catch (er) { if (er.message !== "key") drawJob({status: "failed", error: er.message}); }
  $("go").disabled = false;
};

async function check() {
  if (!job) return;
  try { const d = await api("/admin/make-report/" + job.id); job = d; drawJob(d); if (d.status === "ready" || d.status === "failed") { clearInterval(poll); loadRecent(); } }
  catch (er) { /* keep polling through a slow wake-up */ }
}

function waText(d) { const first = (d.name || "").split(" ")[0]; return "Namaste " + first + ", here is your " + (d.title || d.label) + " from Veshannastro."; }
// Phones share the PDF through the share sheet. Laptops download it and open the customer's WhatsApp chat,
// because a laptop's share sheet often has no WhatsApp in it.
const PHONE = window.matchMedia && matchMedia("(pointer: coarse)").matches;
let sharing = false;
function note(msg, bad) { const p = $("note"); if (p) { p.textContent = msg || ""; p.className = "small" + (bad ? " err" : ""); } }
function chatUrl(d) { return "https://wa.me/91" + d.phone + "?text=" + encodeURIComponent(waText(d)); }
function drawJob(d) {
  const c = $("job"); c.classList.remove("hide");
  if (d.status === "failed") { c.innerHTML = '<div class="status"><b class="err">Could not make the report</b></div><p class="small err"></p>'; c.querySelector("p").textContent = d.error || ""; return; }
  if (d.status !== "ready") {
    const what = d.status === "waiting" ? "Waiting for the order before it to finish" : "Building the report";
    c.innerHTML = '<div class="status"><b></b><span class="small"></span></div><div class="bar"><i></i></div>';
    c.querySelector("b").textContent = what; c.querySelector("span").textContent = (d.label || "") + " for " + (d.name || "") + (d.elapsed ? " · " + d.elapsed + "s" : "");
    return;
  }
  const canShare = !!navigator.share;
  const viaKamala = d.kamala && d.phone;
  c.innerHTML = '<div class="status"><b class="okc">Ready</b><span class="small"></span></div>' +
    (d.card ? '<img id="cardImg" alt="Summary card" style="display:block;width:160px;aspect-ratio:9/16;object-fit:cover;border-radius:8px;margin:4px 0 14px;border:1px solid #0001">' : '') +
    (viaKamala ? '<button id="kamala" type="button">' + (d.sent ? 'Sent through Kamala. Send again' : 'Send through Kamala: PDF, card and voice note') + '</button>' : '') +
    '<button id="share" type="button"' + (viaKamala ? ' class="alt"' : '') + '>' + (viaKamala ? 'Send it myself' : 'Send on WhatsApp') + '</button>' +
    (PHONE && d.phone ? '<a class="btn alt" id="chat" target="_blank" rel="noopener">Open the customer\'s chat</a>' : '') +
    (!PHONE && canShare ? '<button id="sys" type="button" class="alt">Share with this computer\'s share menu</button>' : '') +
    '<button id="dl" type="button" class="alt">Download PDF</button>' +
    (d.card ? '<button id="dlc" type="button" class="alt">Download card</button>' : '') +
    '<p class="small" id="note" style="margin:12px 0 0;min-height:1em"></p><p class="small" id="extraInfo" style="margin:6px 0 0"></p>';
  c.querySelector("span").textContent = d.label + " for " + d.name + " · " + (d.pages ? d.pages + " pages · " : "") + d.size_kb + " KB";
  if ($("chat")) $("chat").href = chatUrl(d);
  const info = [];
  if (d.drive) info.push('Saved to Drive: <a class="link" target="_blank" rel="noopener" href="' + d.drive + '">open</a>');
  if (d.email) info.push("Email: " + d.email.replace(/[<>&]/g, ""));
  $("extraInfo").innerHTML = info.join(" · ");
  $("share").onclick = () => (PHONE ? share(d) : laptopSend(d));
  if ($("sys")) $("sys").onclick = () => share(d);
  $("dl").onclick = () => download(d).then(ok => ok && note("Downloaded."));
  if (d.card) {
    cardBlob(d).then(b => { const im = $("cardImg"); if (im) im.src = URL.createObjectURL(b); }).catch(() => {});
    $("dlc").onclick = () => cardBlob(d).then(b => { const u = URL.createObjectURL(b); const a = document.createElement("a"); a.href = u; a.download = d.filename.replace(/\.pdf$/, "_card.png"); a.click(); setTimeout(() => URL.revokeObjectURL(u), 60000); }).catch(er => note(er.message, true));
  }
  if ($("kamala")) $("kamala").onclick = async () => {
    const b = $("kamala"); b.disabled = true; note("Handing the report to Kamala. If she is asleep this takes up to a minute...");
    try { const r = await api("/admin/make-report/" + d.id + "/send", {method: "POST"}); note(r.message || "Sent."); d.sent = "sending"; b.textContent = "Sent through Kamala. Send again"; }
    catch (er) { if (er.message !== "key") note(er.message, true); }
    b.disabled = false;
  };
  // fetch the PDF now, so the share happens straight from the tap (browsers refuse a share that waits on the network)
  blobFor(d).catch(er => note(er.message, true));
}
async function cardBlob(d) {
  const r = await fetch("/admin/make-report/" + d.id + "/card", {headers: {"X-Admin-Pass": KEY}});
  if (!r.ok) throw new Error("The card is no longer on the server.");
  return r.blob();
}
async function blobFor(d) {
  if (pdfBlob && pdfBlob.id === d.id) return pdfBlob.blob;
  const r = await fetch("/admin/make-report/" + d.id + "/pdf", {headers: {"X-Admin-Pass": KEY}});
  if (!r.ok) throw new Error("The PDF is no longer on the server (it restarts when idle). Use the Drive copy.");
  const b = await r.blob(); pdfBlob = {id: d.id, blob: b}; return b;
}
async function share(d) {
  if (sharing) { note("The share menu is already open. Pick WhatsApp there, or close it first."); return; }
  const blob = pdfBlob && pdfBlob.id === d.id ? pdfBlob.blob : null;
  if (!blob) { note("Getting the PDF ready..."); blobFor(d).then(() => note("Ready. Tap Send on WhatsApp again.")).catch(er => note(er.message, true)); return; }
  const f = new File([blob], d.filename, {type: "application/pdf"});
  if (!(navigator.canShare && navigator.canShare({files: [f]}))) { laptopSend(d); return; }
  sharing = true;
  const release = setTimeout(() => { sharing = false; }, 60000);
  try { await navigator.share({files: [f], text: waText(d)}); note("Sent to the share menu. Check it reached the customer."); }
  catch (er) {
    if (er.name === "AbortError") note("");
    else if (er.name === "InvalidStateError") note("The share menu is already open. Pick WhatsApp there, or close it first.");
    else if (er.name === "NotAllowedError") note("Tap Send on WhatsApp again.");
    else note(er.message, true);
  } finally { clearTimeout(release); sharing = false; }
}
function laptopSend(d) {
  if (d.phone) window.open(chatUrl(d), "_blank", "noopener");
  download(d).then(ok => { if (ok) note(d.phone ? "PDF downloaded and the customer's chat is open: attach the PDF there (or drag it in)." : "PDF downloaded: attach it in the customer's WhatsApp chat."); });
}
async function download(d) {
  try { const u = URL.createObjectURL(await blobFor(d)); const a = document.createElement("a"); a.href = u; a.download = d.filename; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(u), 60000); return true; }
  catch (er) { note(er.message, true); return false; }
}
async function loadRecent() {
  try {
    const d = await api("/admin/make-report");
    const box = $("recent"); box.innerHTML = "";
    $("recentCard").classList.toggle("hide", !d.jobs.length);
    for (const j of d.jobs) {
      const row = document.createElement("div"); const s = document.createElement("span");
      s.textContent = j.name + " · " + j.label + " · " + j.made; row.appendChild(s);
      const a = document.createElement("a"); a.href = "#";
      a.textContent = j.status === "ready" ? "Send" : j.status === "failed" ? "Failed" : "Building";
      a.onclick = e => { e.preventDefault(); job = j; drawJob(j); if (j.status !== "ready" && j.status !== "failed") { clearInterval(poll); poll = setInterval(check, 4000); } window.scrollTo(0, $("job").offsetTop - 10); };
      row.appendChild(a); box.appendChild(row);
    }
  } catch (er) {}
}
if (KEY) showForm(); else showKey();
</script></body></html>"""


def render(products):
    """products: [(key, label, ready)] in the order to show them; a report that is not ready is listed but cannot be picked."""
    fields = {k: [list(f) for f in v] for k, v in FIELDS.items()}
    return (PAGE.replace("__PRODUCTS__", json.dumps([list(p) for p in products]))
                .replace("__FIELDS__", json.dumps(fields)))
