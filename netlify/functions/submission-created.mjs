// Netlify runs this automatically after every verified form submission.
// For "Price request" submissions on the enquiry form, it emails the piece's
// price to the customer (with a copy to the studio) through Resend.
//
// Netlify environment variables:
//   RESEND_API_KEY  required. From resend.com, after verifying marquetry.uk.
//   MAIL_FROM       optional. Default: Marquetry.uk <info@marquetry.uk>
//   MAIL_COPY_TO    optional. Default: info@marquetry.uk (blind copy of every price email)
//   SITE_URL        optional. Default: https://marquetry.uk
import { readFile } from "node:fs/promises";

const FROM = process.env.MAIL_FROM || "Marquetry.uk <info@marquetry.uk>";
const COPY = process.env.MAIL_COPY_TO || "info@marquetry.uk";
const SITE = (process.env.SITE_URL || "https://marquetry.uk").replace(/\/$/, "");

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const gbp = (n) => "£" + Number(n).toLocaleString("en-GB");
const okEmail = (e) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e || "");

async function loadPrices() {
  const url = new URL("./prices.json", import.meta.url);
  return JSON.parse(await readFile(url, "utf8"));
}

function emailHtml({ first, piece, id }) {
  const img = piece.image ? `${SITE}/${piece.image}` : "";
  const link = `${SITE}/#${id}`;
  return `<!doctype html><html><body style="margin:0;background:#F0EEE9;font-family:Georgia,'Times New Roman',serif;color:#111">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#F0EEE9"><tr><td align="center" style="padding:32px 16px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#fff">
<tr><td style="padding:28px 32px 8px;letter-spacing:.32em;font-size:13px;text-transform:uppercase">Marquetry</td></tr>
<tr><td style="padding:8px 32px 0;font-size:16px;line-height:1.6">Dear ${esc(first)},<br><br>Thank you for your interest in the <strong>${esc(piece.name)}</strong>. Here is the price you requested.</td></tr>
${img ? `<tr><td align="center" style="padding:24px 32px 0"><a href="${link}"><img src="${img}" width="320" alt="${esc(piece.name)}" style="display:block;width:320px;max-width:100%;height:auto;border:0"></a></td></tr>` : ""}
<tr><td style="padding:24px 32px 0">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-top:1px solid #111;border-bottom:1px solid #ddd;font-size:15px">
<tr><td style="padding:14px 0">${esc(piece.name)}<br><span style="color:#666;font-size:13px">${esc(piece.dimensions)} (W x D x H)</span></td>
<td align="right" style="padding:14px 0;font-size:24px;white-space:nowrap">${gbp(piece.price)}<br><span style="color:#666;font-size:11px;letter-spacing:.12em">INC. VAT</span></td></tr></table></td></tr>
<tr><td style="padding:20px 32px 0;font-size:14px;line-height:1.7;color:#333">
Made to order in our workshop in Portugal, with a lead time of 10 to 12 weeks.<br>
Free white glove delivery across the UK by Gander &amp; White.<br>
Veneers, finish and size can be adapted; ask us for a quotation on any variation.</td></tr>
<tr><td style="padding:24px 32px 0;font-size:15px;line-height:1.6">To place an order or ask a question, simply reply to this email or call us on +44 7519 450282.</td></tr>
<tr><td style="padding:24px 32px 32px"><a href="${link}" style="display:inline-block;background:#111;color:#fff;text-decoration:none;padding:12px 22px;font-size:12px;letter-spacing:.14em;text-transform:uppercase">View the piece</a></td></tr>
<tr><td style="padding:16px 32px 28px;border-top:1px solid #eee;font-size:11px;line-height:1.6;color:#888">Prices valid from November 2026 and subject to change. Marquetry.uk is a trading name of After Hours Collections Ltd, company no. 15580283, 66 Paul Street, London EC2A 4NA.</td></tr>
</table></td></tr></table></body></html>`;
}

function emailText({ first, piece, id }) {
  return `Dear ${first},

Thank you for your interest in the ${piece.name}.

${piece.name} (${piece.dimensions}, W x D x H): ${gbp(piece.price)} inc. VAT

Made to order in Portugal, 10 to 12 weeks. Free white glove delivery across the UK by Gander & White. Veneers, finish and size can be adapted.

To order, reply to this email or call +44 7519 450282.
${SITE}/#${id}

Marquetry.uk, a trading name of After Hours Collections Ltd, company no. 15580283.`;
}

export const handler = async (event) => {
  let payload;
  try { payload = JSON.parse(event.body).payload; } catch { return { statusCode: 400, body: "Bad payload" }; }
  const d = payload?.data || {};
  const form = payload?.form_name || d["form-name"];
  if (form !== "enquiry" || d.request !== "Price request") return { statusCode: 200, body: "Not a price request" };
  if (!okEmail(d.email)) return { statusCode: 200, body: "No valid email" };

  const prices = await loadPrices();
  const id = d["piece-id"];
  const piece = prices[id];
  if (!piece) { console.warn("Price request for unknown piece", id, d.piece); return { statusCode: 200, body: "Unknown piece" }; }
  if (!process.env.RESEND_API_KEY) { console.error("RESEND_API_KEY is not set; price email not sent to", d.email); return { statusCode: 200, body: "Email not configured" }; }

  const first = String(d.name || "").trim().split(/\s+/)[0] || "there";
  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      from: FROM,
      to: [d.email],
      bcc: COPY ? [COPY] : undefined,
      reply_to: COPY || undefined,
      subject: `Your price for the ${piece.name}`,
      html: emailHtml({ first, piece, id }),
      text: emailText({ first, piece, id }),
    }),
  });
  if (!res.ok) { console.error("Resend error", res.status, await res.text()); return { statusCode: 502, body: "Email failed" }; }
  return { statusCode: 200, body: "Price email sent" };
};
