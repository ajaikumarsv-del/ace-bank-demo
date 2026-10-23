"""
ACE BANK — Simulated Commercial Banking Employee Portal
=======================================================
A demo Streamlit app. ACE BANK is fictional and every account,
name and transaction here is synthetic (generated from fixed seeds).
"""

import hmac
import io
import random
from calendar import monthrange
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# ─────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ACE BANK | Employee Portal (Simulated)",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#0B1F3A"
NAVY_2 = "#16365F"
GOLD = "#C9A24D"
GOLD_2 = "#E3C27A"

DATA_START = date(2025, 1, 1)  # synthetic history begins Jan 1, 2025

# ─────────────────────────────────────────────────────────────
# Demo employees (override via Streamlit secrets — see README)
# ─────────────────────────────────────────────────────────────
DEFAULT_EMPLOYEES = {
    "EMP1001": {"password": "Ace@2026", "name": "Emily Carter", "role": "Relationship Manager", "branch": "New York – Midtown"},
    "EMP1002": {"password": "Ace@2026", "name": "Michael Reyes", "role": "Branch Operations Manager", "branch": "Chicago – The Loop"},
    "ADMIN": {"password": "Admin@123", "name": "Demo Administrator", "role": "Commercial Banking Admin", "branch": "Head Office – New York"},
}


def load_employees():
    try:
        if "employees" in st.secrets:
            return {k.upper(): dict(v) for k, v in st.secrets["employees"].items()}
    except Exception:
        pass
    return DEFAULT_EMPLOYEES


EMPLOYEES = load_employees()

# ─────────────────────────────────────────────────────────────
# Synthetic commercial accounts
# ─────────────────────────────────────────────────────────────
COMPANIES = [
    ("Sterling Textiles Inc.", "Textile Manufacturing", "Charlotte", "1420 Tryon Industrial Pkwy, Charlotte, NC 28206"),
    ("Horizon Freight Logistics LLC", "Logistics & Freight", "Newark", "88 Port Street, Newark, NJ 07114"),
    ("Nimbus Software Solutions Inc.", "Software & IT Services", "Austin", "500 Congress Ave, Suite 1200, Austin, TX 78701"),
    ("Greenfield Agri Exports LLC", "Agricultural Exports", "Fresno", "2750 S Cherry Ave, Fresno, CA 93706"),
    ("Apex Medical Supply Co.", "Medical Distribution", "Columbus", "4100 Fisher Rd, Columbus, OH 43228"),
    ("Bluewater Hospitality Group", "Hospitality", "Miami", "1600 Collins Ave, Miami Beach, FL 33139"),
    ("Crestline Construction Corp.", "Construction", "Denver", "3300 Brighton Blvd, Denver, CO 80216"),
    ("Orion Auto Parts Inc.", "Auto Components", "Detroit", "9200 Michigan Ave, Detroit, MI 48210"),
    ("Liberty Foods & Beverage Co.", "Food & Beverage", "Chicago", "2201 W Fulton St, Chicago, IL 60612"),
    ("Vertex Engineering Group LLC", "Engineering Services", "Houston", "1111 Bagby St, Suite 900, Houston, TX 77002"),
    ("Summit Healthcare Partners", "Healthcare", "Phoenix", "2800 N Central Ave, Phoenix, AZ 85004"),
    ("Meridian Retail Holdings", "Retail", "New York", "350 Fifth Avenue, New York, NY 10118"),
    ("Quantum Electric Supply Co.", "Electrical Equipment", "Atlanta", "1050 Marietta Blvd NW, Atlanta, GA 30318"),
    ("Silverline Apparel Co.", "Apparel", "Los Angeles", "1200 S Santee St, Los Angeles, CA 90015"),
    ("Evergreen Packaging Solutions", "Packaging", "Seattle", "4400 E Marginal Way S, Seattle, WA 98134"),
]

ACCOUNT_TYPES = [
    "Business Checking – Premier",
    "Commercial Checking – Elite",
    "Business Analyzed Checking",
    "Business Checking – Small Business Plus",
]
RMS = ["Emily Carter", "Michael Reyes", "Sarah Thompson", "David Kim", "Jessica Alvarez"]


@st.cache_data
def build_accounts():
    rng = random.Random(2026)
    accounts = []
    for i, (name, industry, city, address) in enumerate(COMPANIES):
        acct_no = f"4020{rng.randint(10_000_000, 99_999_999)}"
        accounts.append({
            "account_no": acct_no,
            "name": name,
            "industry": industry,
            "city": city,
            "address": address,
            "account_type": rng.choice(ACCOUNT_TYPES),
            "customer_id": f"CIF{rng.randint(1_000_000, 9_999_999)}",
            "ein": f"{rng.randint(10, 98)}-{rng.randint(1_000_000, 9_999_999)}",
            "branch": f"{city} Main Branch",
            "routing": f"0{rng.randint(21, 99)}{rng.randint(100_000, 999_999)}",
            "opened": date(rng.randint(2012, 2023), rng.randint(1, 12), rng.randint(1, 28)),
            "rm": rng.choice(RMS),
            "scale": rng.choice([2_500, 4_000, 6_000, 9_000, 15_000]),
            "opening_balance": round(rng.uniform(1.5, 9) * 100_000, 2),
            "status": "Active",
        })
    return accounts


ACCOUNTS = build_accounts()
ACCOUNT_MAP = {a["account_no"]: a for a in ACCOUNTS}

CLIENTS = ["Reliant Traders LLC", "Keystone Distributors", "Northstar Retail Inc", "Patriot Wholesale Co",
           "Pinnacle Imports", "Golden Gate Supply", "Metro Wholesale Hub", "Coastal Marine Supply",
           "Prime Mart Stores", "Unity Infrastructure", "Global Sourcing Co", "Sunrise Industries",
           "Lakeside Ventures", "Frontier Trading Co", "Blue Ocean Imports"]
VENDORS = ["Rapid Freight Carriers", "Midwest Raw Materials", "TechServe IT Support", "Allied Steel Supply",
           "City Office Supplies", "Precision Tools Co", "SafeGuard Security Svcs", "Green Power Solutions",
           "Keystone Chemicals", "Elite Facility Mgmt", "Swift Courier Services", "Harbor Insurance Brokers"]
OTHER_BANKS = ["FIRST MERIDIAN BK", "UNITED HARBOR BK", "CASTLE ROCK BK", "PINNACLE NATL BK", "MIDLAND TRUST BK"]
LANDLORDS = ["PARKVIEW PROPERTIES", "SUMMIT REALTY MGMT", "CORNERSTONE LEASING"]
UTILITIES = ["CITY POWER & LIGHT", "METRO GAS & ELECTRIC", "REGIONAL ENERGY CO"]
MONTHS = ["", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def _ref(rng):
    return f"ACE{rng.randint(1_000_000_000, 9_999_999_999)}"


@st.cache_data
def get_transactions(acct_no: str, upto: date) -> pd.DataFrame:
    """Deterministic synthetic ledger for one account from DATA_START to `upto`."""
    a = ACCOUNT_MAP[acct_no]
    rng = random.Random(int(acct_no))
    base = a["scale"]
    floor = base * 3
    bal = a["opening_balance"]
    rows = []

    def post(d, desc, ref, debit=0.0, credit=0.0, value_date=None):
        nonlocal bal
        bal = round(bal - debit + credit, 2)
        rows.append({"Date": d, "Posted Date": value_date or d, "Description": desc, "Ref No": ref,
                     "Withdrawal": round(debit, 2), "Deposit": round(credit, 2), "Balance": bal})

    def try_debit(d, desc, ref, amt, value_date=None):
        amt = round(amt, 2)
        if bal - amt >= floor:
            post(d, desc, ref, debit=amt, value_date=value_date)

    d = DATA_START
    while d <= upto:
        last_day = monthrange(d.year, d.month)[1]
        mon = f"{MONTHS[d.month]} {d.year}"

        # Fixed monthly / semi-monthly items
        if d.day in (1, 15):
            try_debit(d, f"PAYROLL ACH DEBIT - DIRECT DEPOSIT BATCH {rng.randint(1000, 9999)}", _ref(rng), base * rng.uniform(3, 4.3))
        if d.day == 3:
            try_debit(d, f"ACH DEBIT {rng.choice(LANDLORDS)} - LEASE {mon}", _ref(rng), base * rng.uniform(0.8, 1.1))
        if d.day in (2, 16):
            try_debit(d, "IRS USATAXPYMT EFTPS - FORM 941 PAYROLL TAX", _ref(rng), base * rng.uniform(0.6, 0.9))
        if d.day == 12:
            try_debit(d, f"ACH DEBIT {rng.choice(UTILITIES)} - UTILITY BILL", _ref(rng), base * rng.uniform(0.1, 0.25))
        if d.day == 20:
            try_debit(d, f"STATE DEPT OF REVENUE - SALES TAX {mon}", _ref(rng), base * rng.uniform(0.8, 1.6))
        if d.day == 25:
            try_debit(d, "ACH DEBIT GROUP HEALTH PLAN PREMIUM", _ref(rng), base * rng.uniform(0.5, 0.8))

        # Business-day activity (Mon–Fri)
        if d.weekday() < 5:
            for _ in range(rng.choices([0, 1, 2, 3, 4], [2, 3, 3, 2, 1])[0]):
                mode = rng.random()
                if rng.random() < 0.5:  # credit
                    client = rng.choice(CLIENTS).upper()
                    amt = round(base * rng.lognormvariate(0, 0.7), 2)
                    if mode < 0.40:
                        post(d, f"ACH CREDIT {client} - INV {rng.randint(10000, 99999)}", _ref(rng), credit=amt)
                    elif mode < 0.60:
                        post(d, f"INCOMING WIRE - {rng.choice(OTHER_BANKS)} - {client}",
                             f"FED{rng.randint(10**9, 10**10 - 1)}", credit=amt * 2.5)
                    elif mode < 0.80:
                        post(d, f"MOBILE CHECK DEPOSIT #{rng.randint(1000, 9999)} - {client}", _ref(rng), credit=amt,
                             value_date=d + timedelta(days=1))
                    else:
                        post(d, f"RTP INSTANT PAYMENT CR - {client}", _ref(rng), credit=amt * 0.3)
                else:  # debit
                    vendor = rng.choice(VENDORS).upper()
                    amt = base * rng.lognormvariate(0, 0.7) * 0.6
                    if mode < 0.45:
                        try_debit(d, f"ACH DEBIT {vendor} - VENDOR PMT", _ref(rng), amt)
                    elif mode < 0.65:
                        try_debit(d, f"OUTGOING WIRE - {vendor}", f"FED{rng.randint(10**9, 10**10 - 1)}", amt * 2)
                    elif mode < 0.85:
                        try_debit(d, f"CHECK #{rng.randint(1000, 9999)} PAID - {vendor}", _ref(rng), amt)
                    else:
                        try_debit(d, f"BUSINESS CARD PAYMENT - {vendor}", _ref(rng), amt * 0.4)

        if d.day == last_day:
            post(d, f"MONTHLY SERVICE FEE - {mon}", _ref(rng), debit=float(rng.choice([25, 35, 45, 60])))
            if rng.random() < 0.6:
                post(d, "WIRE TRANSFER FEES", _ref(rng), debit=float(rng.choice([15, 30, 45])))

        d += timedelta(days=1)

    return pd.DataFrame(rows)


def statement_for(acct_no, start, end):
    df = get_transactions(acct_no, date.today())
    before = df[df["Date"] < start]
    opening = before["Balance"].iloc[-1] if len(before) else ACCOUNT_MAP[acct_no]["opening_balance"]
    period = df[(df["Date"] >= start) & (df["Date"] <= end)].reset_index(drop=True)
    closing = period["Balance"].iloc[-1] if len(period) else opening
    return period, float(opening), float(closing)


# ─────────────────────────────────────────────────────────────
# Formatting helpers
# ─────────────────────────────────────────────────────────────
def fmt_usd(x, symbol=True):
    return ("-" if x < 0 else "") + ("$" if symbol else "") + f"{abs(x):,.2f}"


def mask(acct_no):
    return "XXXX XXXX " + acct_no[-4:]


# ─────────────────────────────────────────────────────────────
# PDF + CSV builders
# ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def build_pdf(acct_no, start, end, generated_by):
    a = ACCOUNT_MAP[acct_no]
    df, opening, closing = statement_for(acct_no, start, end)
    buf = io.BytesIO()
    W, H = letter
    navy, gold = colors.HexColor(NAVY), colors.HexColor(GOLD)

    def on_page(c, doc):
        c.saveState()
        c.setFillColor(colors.Color(0.75, 0.1, 0.1, alpha=0.06))
        c.setFont("Helvetica-Bold", 64)
        c.translate(W / 2, H / 2)
        c.rotate(35)
        c.drawCentredString(0, 0, "SIMULATED")
        c.restoreState()

        c.saveState()
        c.setFillColor(navy)
        c.rect(0, H - 26 * mm, W, 26 * mm, fill=1, stroke=0)
        c.setFillColor(gold)
        c.rect(0, H - 27.2 * mm, W, 1.2 * mm, fill=1, stroke=0)
        c.setFillColor(gold)
        c.circle(20 * mm, H - 13 * mm, 6 * mm, fill=1, stroke=0)
        c.setFillColor(navy)
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(20 * mm, H - 15.3 * mm, "A")
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 19)
        c.drawString(29 * mm, H - 13.5 * mm, "ACE BANK")
        c.setFont("Helvetica", 8)
        c.drawString(29 * mm, H - 19 * mm, "Commercial Banking  |  SIMULATED DEMO ENVIRONMENT")
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(W - 14 * mm, H - 12.5 * mm, "STATEMENT OF ACCOUNT")
        c.setFont("Helvetica", 8.5)
        c.drawRightString(W - 14 * mm, H - 18.5 * mm, f"{start:%b %d, %Y}  to  {end:%b %d, %Y}")

        c.setStrokeColor(colors.HexColor("#D9DEE7"))
        c.line(14 * mm, 14 * mm, W - 14 * mm, 14 * mm)
        c.setFont("Helvetica", 6.8)
        c.setFillColor(colors.HexColor("#6B7280"))
        c.drawString(14 * mm, 9.5 * mm, "SIMULATED STATEMENT — ACE BANK is a fictional bank. All data is synthetic and for demonstration only. Not a valid financial document.")
        c.drawRightString(W - 14 * mm, 5.5 * mm, f"Page {doc.page}")
        c.drawString(14 * mm, 5.5 * mm, f"Generated by {generated_by} on {datetime.now():%b %d, %Y %I:%M %p}")
        c.restoreState()

    doc = SimpleDocTemplate(buf, pagesize=letter, leftMargin=14 * mm, rightMargin=14 * mm,
                            topMargin=33 * mm, bottomMargin=20 * mm,
                            title=f"ACE BANK Statement {mask(acct_no)}", author="ACE BANK (Simulated)")

    lbl = ParagraphStyle("lbl", fontName="Helvetica", fontSize=7.2, textColor=colors.HexColor("#6B7280"), leading=9)
    val = ParagraphStyle("val", fontName="Helvetica-Bold", fontSize=8.6, textColor=navy, leading=11)
    cell = ParagraphStyle("cell", fontName="Helvetica", fontSize=7.2, leading=8.8)
    big = ParagraphStyle("big", fontName="Helvetica-Bold", fontSize=13, textColor=navy, leading=16)

    def kv(k, v):
        return [Paragraph(k.upper(), lbl), Paragraph(str(v), val)]

    story = [Paragraph(a["name"], big),
             Paragraph(a["address"], ParagraphStyle("addr", parent=lbl, fontSize=8.2, leading=11)),
             Spacer(1, 4 * mm)]

    info = [
        kv("Account Number", a["account_no"]) + kv("Customer ID", a["customer_id"]) + kv("Account Type", a["account_type"]),
        kv("Branch", a["branch"]) + kv("Routing No", a["routing"]) + kv("EIN", a["ein"]),
        kv("Currency", "USD") + kv("Account Opened", a["opened"].strftime("%b %d, %Y")) + kv("Relationship Mgr", a["rm"]),
    ]
    t = Table(info, colWidths=[24 * mm, 36 * mm, 22 * mm, 34 * mm, 26 * mm, 40 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F7FB")),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D9DEE7")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [t, Spacer(1, 4 * mm)]

    tot_dr, tot_cr = df["Withdrawal"].sum(), df["Deposit"].sum()
    summ = [["BEGINNING BALANCE", "TOTAL DEPOSITS", "TOTAL WITHDRAWALS", "ENDING BALANCE", "TRANSACTIONS"],
            [fmt_usd(opening), fmt_usd(tot_cr), fmt_usd(tot_dr), fmt_usd(closing), f"{len(df)}"]]
    s = Table(summ, colWidths=[38 * mm, 38 * mm, 38 * mm, 38 * mm, 30 * mm])
    s.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), navy), ("TEXTCOLOR", (0, 0), (-1, 0), gold),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"), ("FONTSIZE", (0, 1), (-1, 1), 9.5),
        ("TEXTCOLOR", (0, 1), (-1, 1), navy), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.6, navy), ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [s, Spacer(1, 5 * mm)]

    head = ["Date", "Description", "Check / Ref No", "Posted", "Withdrawals", "Deposits", "Balance"]
    data = [head, [start.strftime("%m/%d/%y"), Paragraph("<b>BEGINNING BALANCE</b>", cell), "", "", "", "", fmt_usd(opening, False)]]
    for r in df.itertuples(index=False):
        data.append([r.Date.strftime("%m/%d/%y"), Paragraph(r.Description, cell), r._3, r._1.strftime("%m/%d/%y"),
                     fmt_usd(r.Withdrawal, False) if r.Withdrawal else "",
                     fmt_usd(r.Deposit, False) if r.Deposit else "",
                     fmt_usd(r.Balance, False)])
    data.append(["", Paragraph("<b>ENDING BALANCE</b>", cell), "", "",
                 fmt_usd(tot_dr, False), fmt_usd(tot_cr, False), fmt_usd(closing, False)])

    tx = Table(data, colWidths=[15 * mm, 60 * mm, 27 * mm, 15 * mm, 22 * mm, 22 * mm, 21 * mm], repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), navy), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7.2),
        ("ALIGN", (4, 0), (-1, -1), "RIGHT"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, gold),
        ("LINEBELOW", (0, 1), (-1, -2), 0.25, colors.HexColor("#E3E7EE")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F5EEDC")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(2, len(data) - 1, 2):
        style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FAFBFD")))
    tx.setStyle(TableStyle(style))
    story += [tx, Spacer(1, 6 * mm),
              Paragraph("*** End of Statement ***  This is a system-generated SIMULATED statement and does not require a signature. "
                        "ACE BANK is not a real bank; account holders, numbers and transactions are fictitious.", lbl)]

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    return buf.getvalue()


def build_csv(acct_no, start, end):
    df, opening, closing = statement_for(acct_no, start, end)
    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"]).dt.strftime("%m/%d/%Y")
    out["Posted Date"] = pd.to_datetime(out["Posted Date"]).dt.strftime("%m/%d/%Y")
    for col in ("Withdrawal", "Deposit"):
        out[col] = out[col].map(lambda v: f"{v:.2f}" if v else "")
    out["Balance"] = out["Balance"].map(lambda v: f"{v:.2f}")
    opening_row = pd.DataFrame([{"Date": start.strftime("%m/%d/%Y"), "Posted Date": "", "Description": "BEGINNING BALANCE",
                                 "Ref No": "", "Withdrawal": "", "Deposit": "", "Balance": round(opening, 2)}])
    out = pd.concat([opening_row, out], ignore_index=True)
    out.columns = ["Date", "Posted Date", "Description", "Ref No", "Withdrawals (USD)", "Deposits (USD)", "Balance (USD)"]
    return out.to_csv(index=False).encode("utf-8")


# ─────────────────────────────────────────────────────────────
# Styling
# ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
html, body, [class*="css"], .stMarkdown, input, button, textarea {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background: radial-gradient(1200px 600px at 100% -10%, #E9E2CF 0%, transparent 55%),
                      linear-gradient(180deg, #F7F5EF 0%, #EEF1F7 100%); }}
#MainMenu, footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.6rem; max-width: 1250px; }}

.sim-banner {{ position: fixed; top: 0; left: 0; right: 0; z-index: 999999;
  background: repeating-linear-gradient(45deg, #7A1F1F, #7A1F1F 14px, #8A2626 14px, #8A2626 28px);
  color: #FFE9C2; text-align: center; font-size: 12.5px; font-weight: 600; letter-spacing: .4px; padding: 6px 10px; }}

.brand {{ display:flex; align-items:center; gap:14px; }}
.brand-mark {{ width:46px; height:46px; border-radius:12px; display:grid; place-items:center;
  background: linear-gradient(135deg, {GOLD}, {GOLD_2}); color:{NAVY}; font-family:'Playfair Display',serif;
  font-weight:700; font-size:24px; box-shadow:0 6px 18px rgba(201,162,77,.45); }}
.brand-name {{ font-family:'Playfair Display',serif; font-size:28px; font-weight:700; color:{NAVY}; letter-spacing:1.5px; line-height:1; }}
.brand-sub {{ font-size:11px; letter-spacing:2.5px; color:#7B8597; text-transform:uppercase; margin-top:4px; }}

.hero {{ background: linear-gradient(135deg, {NAVY} 0%, {NAVY_2} 65%, #1F4B82 100%); color:#fff; border-radius:22px;
  padding:38px 36px; position:relative; overflow:hidden; box-shadow: 0 20px 50px rgba(11,31,58,.25); min-height: 430px; }}
.hero:before {{ content:""; position:absolute; right:-90px; top:-90px; width:300px; height:300px; border-radius:50%;
  background: radial-gradient(circle, rgba(227,194,122,.45), transparent 68%); }}
.hero:after {{ content:""; position:absolute; left:-60px; bottom:-120px; width:260px; height:260px; border-radius:50%;
  border: 1px solid rgba(227,194,122,.25); }}
.hero h1 {{ font-family:'Playfair Display',serif; font-size:38px; line-height:1.15; margin:18px 0 12px; color:#fff; }}
.hero p {{ color:#C9D3E3; font-size:15px; line-height:1.6; max-width:460px; }}
.hero .gold {{ color:{GOLD_2}; }}
.chip {{ display:inline-block; padding:6px 12px; border-radius:999px; font-size:11.5px; font-weight:600; letter-spacing:.6px;
  background: rgba(227,194,122,.15); color:{GOLD_2}; border:1px solid rgba(227,194,122,.35); }}
.feat {{ display:flex; gap:22px; margin-top:28px; flex-wrap:wrap; }}
.feat div {{ font-size:13px; color:#DCE4F0; }}
.feat b {{ display:block; font-size:20px; color:#fff; font-weight:700; }}

[data-testid="stForm"] {{ background:#fff; border:1px solid rgba(11,31,58,.07); border-radius:20px; padding:28px 26px;
  box-shadow: 0 18px 45px rgba(11,31,58,.10); }}
.stTextInput input, .stDateInput input {{ border-radius:10px !important; }}

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {{
  background: linear-gradient(135deg, {GOLD} 0%, {GOLD_2} 100%); color:{NAVY}; border:none; border-radius:11px;
  font-weight:700; letter-spacing:.3px; padding:.6rem 1.2rem; box-shadow:0 8px 20px rgba(201,162,77,.35); transition: all .15s ease; }}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {{
  transform: translateY(-1px); box-shadow:0 12px 26px rgba(201,162,77,.45); color:{NAVY}; }}

section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {NAVY} 0%, #0F2747 100%); }}
section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {{ color:#DCE4F0 !important; }}
section[data-testid="stSidebar"] .stButton > button {{ width:100%; background: transparent; color:{GOLD_2} !important;
  border:1px solid rgba(227,194,122,.5); box-shadow:none; }}
section[data-testid="stSidebar"] .stButton > button p {{ color:{GOLD_2} !important; }}

.emp-card {{ background: rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.1); border-radius:16px; padding:18px; margin:10px 0 18px; }}
.avatar {{ width:52px; height:52px; border-radius:50%; display:grid; place-items:center; font-weight:700; font-size:18px;
  background: linear-gradient(135deg, {GOLD}, {GOLD_2}); color:{NAVY}; margin-bottom:10px; }}
.emp-name {{ font-size:16px; font-weight:700; color:#fff; }}
.emp-role {{ font-size:12px; color:#AFC0D8; }}

.page-head {{ display:flex; justify-content:space-between; align-items:flex-end; margin: 6px 0 18px; }}
.page-head h2 {{ font-family:'Playfair Display',serif; color:{NAVY}; font-size:30px; margin:0; }}
.page-head span {{ color:#7B8597; font-size:13px; }}

.acct-card {{ background: linear-gradient(135deg, {NAVY} 0%, {NAVY_2} 100%); color:#fff; border-radius:20px; padding:26px 28px;
  position:relative; overflow:hidden; box-shadow:0 16px 40px rgba(11,31,58,.22); }}
.acct-card:after {{ content:""; position:absolute; right:-70px; top:-70px; width:220px; height:220px; border-radius:50%;
  background: radial-gradient(circle, rgba(227,194,122,.35), transparent 70%); }}
.acct-card .nm {{ font-family:'Playfair Display',serif; font-size:24px; font-weight:700; }}
.acct-card .no {{ font-size:15px; letter-spacing:3px; color:{GOLD_2}; margin-top:4px; font-weight:600; }}
.grid {{ display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:16px 22px; margin-top:20px; position:relative; z-index:1; }}
.grid .k {{ font-size:10.5px; letter-spacing:1.4px; text-transform:uppercase; color:#9FB0C8; }}
.grid .v {{ font-size:14px; font-weight:600; color:#fff; margin-top:3px; }}
@media (max-width: 900px) {{ .grid {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}

.kpis {{ display:grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap:14px; margin: 18px 0 8px; }}
.kpi {{ background:#fff; border-radius:16px; padding:16px 18px; border:1px solid rgba(11,31,58,.07); box-shadow:0 8px 22px rgba(11,31,58,.06); }}
.kpi .k {{ font-size:11px; color:#7B8597; letter-spacing:1px; text-transform:uppercase; font-weight:600; }}
.kpi .v {{ font-size:20px; font-weight:700; color:{NAVY}; margin-top:6px; }}
.kpi.cr .v {{ color:#127A4A; }} .kpi.dr .v {{ color:#B42318; }}
@media (max-width: 900px) {{ .kpis {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} }}

.section-title {{ font-size:13px; font-weight:700; color:{NAVY}; letter-spacing:1.6px; text-transform:uppercase; margin: 22px 0 10px;
  display:flex; align-items:center; gap:10px; }}
.section-title:before {{ content:""; width:22px; height:3px; background:{GOLD}; border-radius:3px; }}
.foot {{ text-align:center; color:#8A93A3; font-size:11.5px; margin-top:40px; }}
</style>
<div class="sim-banner">⚠ SIMULATED WEBSITE — ACE BANK is a fictional bank. All customers, accounts and transactions are synthetic, for demonstration only.</div>
""", unsafe_allow_html=True)


def brand():
    st.markdown("""<div class="brand"><div class="brand-mark">A</div>
        <div><div class="brand-name">ACE BANK</div><div class="brand-sub">Commercial Banking · Employee Portal</div></div></div>""",
                unsafe_allow_html=True)


def footer():
    st.markdown('<div class="foot">© ACE BANK (Simulated) · Demo application · No real customer data is stored or processed.</div>',
                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Session
# ─────────────────────────────────────────────────────────────
for k, v in {"emp_id": None, "acct_no": None, "stmt": None}.items():
    st.session_state.setdefault(k, v)


def do_login(emp_id, pwd):
    emp = EMPLOYEES.get(emp_id.strip().upper())
    if emp and hmac.compare_digest(str(emp["password"]), pwd):
        st.session_state.emp_id = emp_id.strip().upper()
        return True
    return False


# ─────────────────────────────────────────────────────────────
# Login page
# ─────────────────────────────────────────────────────────────
def login_page():
    brand()
    st.write("")
    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.markdown(f"""
        <div class="hero">
          <span class="chip">SECURE EMPLOYEE ACCESS · SIMULATED</span>
          <h1>Commercial banking,<br><span class="gold">beautifully simplified.</span></h1>
          <p>Look up commercial account holders, review activity and issue account statements in PDF or CSV — in seconds.</p>
          <div class="feat">
            <div><b>{len(ACCOUNTS)}</b>Commercial accounts</div>
            <div><b>PDF · CSV</b>Statement formats</div>
            <div><b>USD</b>Commercial checking</div>
          </div>
        </div>""", unsafe_allow_html=True)
    with right:
        with st.form("login", clear_on_submit=False):
            st.markdown(f"<h3 style='font-family:Playfair Display,serif;color:{NAVY};margin:0 0 4px'>Employee Sign in</h3>"
                        "<p style='color:#7B8597;font-size:13px;margin-bottom:14px'>Use your ACE BANK employee credentials.</p>",
                        unsafe_allow_html=True)
            emp_id = st.text_input("Employee ID", placeholder="e.g. EMP1001")
            pwd = st.text_input("Password", type="password", placeholder="••••••••")
            ok = st.form_submit_button("Sign in securely  →", width="stretch")
        if ok:
            if do_login(emp_id, pwd):
                st.rerun()
            else:
                st.error("Invalid Employee ID or password.")
        with st.expander("Demo credentials"):
            st.markdown("**Employee ID:** `EMP1001`  ·  **Password:** `Ace@2026`\n\n"
                        "**Employee ID:** `ADMIN`  ·  **Password:** `Admin@123`")
    footer()


# ─────────────────────────────────────────────────────────────
# Portal
# ─────────────────────────────────────────────────────────────
def sidebar(emp):
    with st.sidebar:
        st.markdown(f"""<div class="brand" style="margin-top:6px"><div class="brand-mark" style="width:38px;height:38px;font-size:19px">A</div>
            <div><div class="brand-name" style="color:#fff;font-size:22px">ACE BANK</div>
            <div class="brand-sub" style="color:#9FB0C8;font-size:9.5px">Employee Portal</div></div></div>""", unsafe_allow_html=True)
        initials = "".join(p[0] for p in emp["name"].split()[:2])
        st.markdown(f"""<div class="emp-card"><div class="avatar">{initials}</div>
            <div class="emp-name">{emp['name']}</div><div class="emp-role">{emp['role']}</div>
            <div class="emp-role" style="margin-top:8px">🆔 {st.session_state.emp_id} &nbsp;·&nbsp; 📍 {emp['branch']}</div></div>""",
                    unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:12px'>🕒 Session started {datetime.now():%b %d, %Y, %I:%M %p}</span>", unsafe_allow_html=True)
        st.write("")
        if st.button("Sign out"):
            for k in ("emp_id", "acct_no", "stmt"):
                st.session_state[k] = None
            st.rerun()
        st.markdown("<div style='margin-top:30px;font-size:11px;color:#8FA1BC'>⚠ Simulated environment. "
                    "No real banking data.</div>", unsafe_allow_html=True)


def portal():
    emp = EMPLOYEES[st.session_state.emp_id]
    sidebar(emp)
    brand()
    st.markdown(f"""<div class="page-head"><div><h2>Account Statements</h2>
        <span>Search a commercial account holder and issue a statement for any date range.</span></div>
        <span>{datetime.now():%A, %B %d, %Y}</span></div>""", unsafe_allow_html=True)

    # Search
    c1, c2 = st.columns([4, 1])
    with c1:
        q = st.text_input("Account number", placeholder="Enter 12-digit account number, e.g. " + ACCOUNTS[0]["account_no"],
                          label_visibility="collapsed")
    with c2:
        search = st.button("🔍  Search", width="stretch")

    if search:
        num = "".join(ch for ch in q if ch.isdigit())
        if num in ACCOUNT_MAP:
            st.session_state.acct_no, st.session_state.stmt = num, None
        else:
            st.error("No commercial account found with that number. Check the directory below for demo accounts.")

    with st.expander(f"📒  Commercial account directory ({len(ACCOUNTS)} demo accounts) — click a row to open"):
        dir_df = pd.DataFrame([{"Account No": a["account_no"], "Account Holder": a["name"], "Industry": a["industry"],
                                "Branch": a["branch"], "Type": a["account_type"]} for a in ACCOUNTS])
        ev = st.dataframe(dir_df, hide_index=True, width="stretch", on_select="rerun",
                          selection_mode="single-row", key="directory")
        rows = ev.selection.rows if ev and hasattr(ev, "selection") else []
        if rows:
            picked = dir_df.iloc[rows[0]]["Account No"]
            if picked != st.session_state.acct_no:
                st.session_state.acct_no, st.session_state.stmt = picked, None
                st.rerun()

    acct_no = st.session_state.acct_no
    if not acct_no:
        st.info("Search by account number or pick an account from the directory to get started.")
        footer()
        return

    a = ACCOUNT_MAP[acct_no]
    full = get_transactions(acct_no, date.today())
    cur_bal = full["Balance"].iloc[-1]
    last30 = full[full["Date"] >= date.today() - timedelta(days=30)]

    st.markdown(f"""<div class="acct-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;position:relative;z-index:1">
        <div><div class="nm">{a['name']}</div><div class="no">{' '.join(acct_no[i:i+4] for i in range(0, 12, 4))}</div></div>
        <span class="chip">● {a['status'].upper()}</span></div>
      <div class="grid">
        <div><div class="k">Account type</div><div class="v">{a['account_type']}</div></div>
        <div><div class="k">Customer ID</div><div class="v">{a['customer_id']}</div></div>
        <div><div class="k">Branch · Routing</div><div class="v">{a['branch']} · {a['routing']}</div></div>
        <div><div class="k">EIN</div><div class="v">{a['ein']}</div></div>
        <div><div class="k">Industry</div><div class="v">{a['industry']}</div></div>
        <div><div class="k">Relationship manager</div><div class="v">{a['rm']}</div></div>
        <div><div class="k">Account opened</div><div class="v">{a['opened']:%b %d, %Y}</div></div>
        <div><div class="k">Registered address</div><div class="v">{a['address']}</div></div>
      </div></div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="kpis">
      <div class="kpi"><div class="k">Available balance</div><div class="v">{fmt_usd(cur_bal)}</div></div>
      <div class="kpi cr"><div class="k">Credits · last 30 days</div><div class="v">{fmt_usd(last30['Deposit'].sum())}</div></div>
      <div class="kpi dr"><div class="k">Debits · last 30 days</div><div class="v">{fmt_usd(last30['Withdrawal'].sum())}</div></div>
      <div class="kpi"><div class="k">Transactions · last 30 days</div><div class="v">{len(last30)}</div></div>
    </div>""", unsafe_allow_html=True)

    # Statement controls
    st.markdown('<div class="section-title">Generate statement</div>', unsafe_allow_html=True)
    today = date.today()
    ytd_start = date(today.year, 1, 1)
    presets = {"Last 30 days": (today - timedelta(days=30), today),
               "Last 3 months": (today - timedelta(days=91), today),
               "Last 6 months": (today - timedelta(days=182), today),
               "Year to date": (ytd_start, today),
               "Custom range": None}
    p1, p2, p3, p4 = st.columns([1.6, 1, 1, 1])
    with p1:
        preset = st.selectbox("Period", list(presets), index=1)
    default = presets[preset] or (today - timedelta(days=30), today)
    custom = preset == "Custom range"
    with p2:
        start = st.date_input("From", value=default[0], min_value=DATA_START, max_value=today,
                              disabled=not custom, key=f"from_{preset}", format="MM/DD/YYYY")
    with p3:
        end = st.date_input("To", value=default[1], min_value=DATA_START, max_value=today,
                            disabled=not custom, key=f"to_{preset}", format="MM/DD/YYYY")
    with p4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        gen = st.button("Generate statement", width="stretch")

    if gen:
        if start > end:
            st.error("'From' date must be on or before 'To' date.")
        else:
            st.session_state.stmt = (acct_no, start, end)

    stmt = st.session_state.stmt
    if stmt and stmt[0] == acct_no:
        _, s, e = stmt
        df, opening, closing = statement_for(acct_no, s, e)
        st.markdown(f"""<div class="kpis">
          <div class="kpi"><div class="k">Beginning · {s:%b %d, %Y}</div><div class="v">{fmt_usd(opening)}</div></div>
          <div class="kpi cr"><div class="k">Total deposits</div><div class="v">{fmt_usd(df['Deposit'].sum())}</div></div>
          <div class="kpi dr"><div class="k">Total withdrawals</div><div class="v">{fmt_usd(df['Withdrawal'].sum())}</div></div>
          <div class="kpi"><div class="k">Ending · {e:%b %d, %Y}</div><div class="v">{fmt_usd(closing)}</div></div>
        </div>""", unsafe_allow_html=True)

        fname = f"ACEBANK_{acct_no}_{s:%Y%m%d}_{e:%Y%m%d}"
        d1, d2, _ = st.columns([1, 1, 2])
        with d1:
            with st.spinner("Preparing PDF…"):
                pdf = build_pdf(acct_no, s, e, f"{st.session_state.emp_id} ({emp['name']})")
            st.download_button("⬇  Download PDF", pdf, file_name=f"{fname}.pdf", mime="application/pdf",
                               width="stretch")
        with d2:
            st.download_button("⬇  Download CSV", build_csv(acct_no, s, e), file_name=f"{fname}.csv",
                               mime="text/csv", width="stretch")

        st.markdown(f'<div class="section-title">Statement preview · {len(df)} transactions</div>', unsafe_allow_html=True)
        if df.empty:
            st.info("No transactions in the selected period.")
        else:
            view = df.copy()
            view["Withdrawal"] = view["Withdrawal"].replace(0, None)
            view["Deposit"] = view["Deposit"].replace(0, None)
            st.dataframe(
                view, hide_index=True, width="stretch", height=420,
                column_config={
                    "Date": st.column_config.DateColumn(format="MM/DD/YYYY"),
                    "Posted Date": st.column_config.DateColumn(format="MM/DD/YYYY"),
                    "Description": st.column_config.TextColumn(width="large"),
                    "Withdrawal": st.column_config.NumberColumn("Withdrawals", format="dollar"),
                    "Deposit": st.column_config.NumberColumn("Deposits", format="dollar"),
                    "Balance": st.column_config.NumberColumn(format="dollar"),
                })
    footer()


if st.session_state.emp_id and st.session_state.emp_id in EMPLOYEES:
    portal()
else:
    login_page()
