"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║         QR Certificate Generator Pro V3.0— Complete App                          ║
║         Developed by: Abdul Samad | SBBU Nawabshah                               ║
╠══════════════════════════════════════════════════════════════════════════════════╣
║  INSTALL:                                                                        ║
║    pip install streamlit pillow qrcode[pil] reportlab openpyxl pandas            ║
║  RUN:                                                                            ║
║    streamlit run app.py                                                          ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import qrcode
import io, zipfile
import pandas as pd
import openpyxl
from openpyxl.styles import Font as XFont, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Certificate Generate Pro V3.0",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
.stApp { background: linear-gradient(135deg, #0b132b 0%, #1c2541 100%); }
section[data-testid="stSidebar"] { background: #1e1b4b !important; }
section[data-testid="stSidebar"] * { color: #7ecefd !important; }

/* ── Text ── */
h1 { color: #ffd159 !important; text-align: center; }
h2, h3 { color: #7ecefd !important; }
label, .stTextInput label, .stSelectbox label,
.stSlider label, .stTextArea label { color: #7ecefd !important; font-weight: 600; }
p { color: #c5d8f0; }

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea textarea {
    background: #0d1b35 !important;
    color: white !important;
    border: 1.5px solid #7ecefd55 !important;
    border-radius: 8px !important;
    font-size: 1rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea textarea:focus {
    border-color: #7ecefd !important;
    box-shadow: 0 0 0 2px #7ecefd33 !important;
}
.stSelectbox > div > div { background: #0d1b35 !important; color: white !important; border: 1.5px solid #7ecefd55 !important; border-radius: 8px !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(90deg, #2e6bef, #7ecefd) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; font-weight: bold !important;
    font-size: 1rem !important; padding: .6rem 1.2rem !important;
    transition: all .2s !important;
}
.stButton > button:hover { opacity: .85 !important; transform: scale(1.01) !important; }

/* ── Cards ── */
.card {
    background: rgba(20, 30, 70, 0.92);
    border: 1px solid #7ecefd33;
    border-radius: 16px;
    padding: 24px;
    margin: 10px 0;
}
.card-green {
    background: rgba(10, 60, 40, 0.9);
    border: 1px solid #2ecc7166;
    border-radius: 14px;
    padding: 20px;
    margin: 12px 0;
}
.card-warn {
    background: rgba(80, 40, 0, 0.85);
    border: 1px solid #f39c1266;
    border-radius: 14px;
    padding: 16px;
    margin: 10px 0;
}

/* ── Metrics ── */
[data-testid="stMetricValue"] { color: #ffd159 !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"] { color: #7ecefd !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    color: #7ecefd; background: #1e1b4b;
    border-radius: 8px 8px 0 0; font-weight: 600;
}
.stTabs [aria-selected="true"] { background: #2e6bef !important; color: white !important; }

/* ── Table ── */
.stDataFrame { border-radius: 10px; overflow: hidden; }

/* ── Divider ── */
hr { border-color: #7ecefd22 !important; }

/* ── Student page big inputs ── */
.big-form .stTextInput > div > div > input {
    font-size: 1.2rem !important;
    padding: 14px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────
DEFAULTS = {
    "admin_auth":     False,
    "admin_password": "admin123",
    "registrations":  [],          # [{name, roll_no, dept, batch, category, date, time}]
    "template_bytes": None,
    "event_name":     "Certificate of Participation",
    "event_date":     datetime.now().strftime("%Y-%m-%d"),
    "event_venue":    "",
    "event_topic":    "",
    "organizer":      "",
    "categories":     "Participate,Teacher",
    "qr_data":        None,
    "qr_url":         "",
    # Text settings
    "text_x":         50,
    "text_y":         60,
    "font_size":      72,
    "text_color":     "#1a1a1a",
    "selected_font":  "Arial Bold",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────
#  FONTS  (50+ with search & categories)
# ─────────────────────────────────────────────────────────────────
FONTS = {
    # Sans Serif
    "Arial Regular":          ["arial.ttf",       "DejaVuSans.ttf"],
    "Arial Bold":             ["arialbd.ttf",     "DejaVuSans-Bold.ttf"],
    "Arial Italic":           ["ariali.ttf",      "DejaVuSans-Oblique.ttf"],
    "Arial Bold Italic":      ["arialbi.ttf",     "DejaVuSans-BoldOblique.ttf"],
    "Calibri Regular":        ["calibri.ttf",     "DejaVuSans.ttf"],
    "Calibri Bold":           ["calibrib.ttf",    "DejaVuSans-Bold.ttf"],
    "Calibri Italic":         ["calibrii.ttf",    "DejaVuSans-Oblique.ttf"],
    "Tahoma Regular":         ["tahoma.ttf",      "DejaVuSans.ttf"],
    "Tahoma Bold":            ["tahomabd.ttf",    "DejaVuSans-Bold.ttf"],
    "Verdana Regular":        ["verdana.ttf",     "DejaVuSans.ttf"],
    "Verdana Bold":           ["verdanab.ttf",    "DejaVuSans-Bold.ttf"],
    "Trebuchet MS":           ["trebuc.ttf",      "DejaVuSans.ttf"],
    "Trebuchet Bold":         ["trebucbd.ttf",    "DejaVuSans-Bold.ttf"],
    "Segoe UI":               ["segoeui.ttf",     "DejaVuSans.ttf"],
    "Segoe UI Bold":          ["segoeuib.ttf",    "DejaVuSans-Bold.ttf"],
    "Segoe UI Light":         ["segoeuil.ttf",    "DejaVuSans.ttf"],
    "Segoe UI Italic":        ["segoeuii.ttf",    "DejaVuSans-Oblique.ttf"],
    # Serif / Formal
    "Times New Roman":        ["times.ttf",       "DejaVuSerif.ttf"],
    "Times New Roman Bold":   ["timesbd.ttf",     "DejaVuSerif-Bold.ttf"],
    "Times New Roman Italic": ["timesi.ttf",      "DejaVuSerif-Italic.ttf"],
    "Times NR Bold Italic":   ["timesbi.ttf",     "DejaVuSerif-BoldItalic.ttf"],
    "Georgia Regular":        ["georgia.ttf",     "DejaVuSerif.ttf"],
    "Georgia Bold":           ["georgiab.ttf",    "DejaVuSerif-Bold.ttf"],
    "Georgia Italic":         ["georgiai.ttf",    "DejaVuSerif-Italic.ttf"],
    "Palatino Linotype":      ["pala.ttf",        "DejaVuSerif.ttf"],
    "Palatino Bold":          ["palab.ttf",       "DejaVuSerif-Bold.ttf"],
    "Palatino Italic":        ["palai.ttf",       "DejaVuSerif-Italic.ttf"],
    "Book Antiqua":           ["bkant.ttf",       "DejaVuSerif.ttf"],
    "Garamond":               ["GARA.TTF",        "DejaVuSerif.ttf"],
    "Garamond Bold":          ["GARABD.TTF",      "DejaVuSerif-Bold.ttf"],
    "Garamond Italic":        ["GARAIT.TTF",      "DejaVuSerif-Italic.ttf"],
    # Monospace
    "Courier New":            ["cour.ttf",        "DejaVuSansMono.ttf"],
    "Courier New Bold":       ["courbd.ttf",      "DejaVuSansMono-Bold.ttf"],
    "Courier New Italic":     ["couri.ttf",       "DejaVuSansMono-Oblique.ttf"],
    "Consolas":               ["consola.ttf",     "DejaVuSansMono.ttf"],
    "Consolas Bold":          ["consolab.ttf",    "DejaVuSansMono-Bold.ttf"],
    "Lucida Console":         ["lucon.ttf",       "DejaVuSansMono.ttf"],
    # Display / Stylish
    "Century Gothic":         ["GOTHIC.TTF",      "DejaVuSans.ttf"],
    "Century Gothic Bold":    ["GOTHICB.TTF",     "DejaVuSans-Bold.ttf"],
    "Century Gothic Italic":  ["GOTHICI.TTF",     "DejaVuSans-Oblique.ttf"],
    "Impact":                 ["impact.ttf",      "DejaVuSans-Bold.ttf"],
    "Franklin Gothic":        ["framd.ttf",       "DejaVuSans-Bold.ttf"],
    "Gill Sans MT":           ["GILSANUB.TTF",    "DejaVuSans.ttf"],
    "Candara Regular":        ["Candara.ttf",     "DejaVuSans.ttf"],
    "Candara Bold":           ["Candarab.ttf",    "DejaVuSans-Bold.ttf"],
    "Corbel Regular":         ["corbel.ttf",      "DejaVuSans.ttf"],
    "Corbel Bold":            ["corbelb.ttf",     "DejaVuSans-Bold.ttf"],
    "Rockwell":               ["ROCK.TTF",        "DejaVuSerif.ttf"],
    "Rockwell Bold":          ["ROCKB.TTF",       "DejaVuSerif-Bold.ttf"],
    # Script / Elegant
    "Brush Script MT":        ["BRUSHSCI.TTF",    "DejaVuSerif-Italic.ttf"],
    "Lucida Handwriting":     ["lhandw.ttf",      "DejaVuSerif-Italic.ttf"],
    "Lucida Calligraphy":     ["LCALLIG.TTF",     "DejaVuSerif-Italic.ttf"],
    "Comic Sans MS":          ["comic.ttf",       "DejaVuSans.ttf"],
    "Comic Sans MS Bold":     ["comicbd.ttf",     "DejaVuSans-Bold.ttf"],
    # Always-available fallbacks
    "DejaVu Sans":            ["DejaVuSans.ttf",           "DejaVuSans.ttf"],
    "DejaVu Sans Bold":       ["DejaVuSans-Bold.ttf",      "DejaVuSans-Bold.ttf"],
    "DejaVu Serif":           ["DejaVuSerif.ttf",          "DejaVuSerif.ttf"],
    "DejaVu Serif Bold":      ["DejaVuSerif-Bold.ttf",     "DejaVuSerif-Bold.ttf"],
    "DejaVu Mono":            ["DejaVuSansMono.ttf",       "DejaVuSansMono.ttf"],
    "DejaVu Mono Bold":       ["DejaVuSansMono-Bold.ttf",  "DejaVuSansMono-Bold.ttf"],
}

FONT_CATS = {
    "🔤 Sans Serif":    [k for k in FONTS if any(x in k for x in ["Arial","Calibri","Tahoma","Verdana","Trebuchet","Segoe"])],
    "📜 Serif/Formal":  [k for k in FONTS if any(x in k for x in ["Times","Georgia","Palatino","Book","Garamond"])],
    "💻 Monospace":     [k for k in FONTS if any(x in k for x in ["Courier","Consolas","Lucida Console"])],
    "✨ Display":       [k for k in FONTS if any(x in k for x in ["Century","Impact","Franklin","Gill","Candara","Corbel","Rockwell"])],
    "🖋️ Script":       [k for k in FONTS if any(x in k for x in ["Brush","Handwriting","Calligraphy","Comic"])],
    "🛡️ Fallback":     [k for k in FONTS if "DejaVu" in k],
}

# ─────────────────────────────────────────────────────────────────
#  CORE HELPERS
# ─────────────────────────────────────────────────────────────────
def load_font(font_name: str, size: int) -> ImageFont.ImageFont:
    for path in FONTS.get(font_name, ["DejaVuSans-Bold.ttf"]):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def hex_to_rgba(h: str, alpha: int = 255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)

def generate_cert(name: str, template: bytes, cfg: dict) -> bytes:
    img   = Image.open(io.BytesIO(template)).convert("RGBA")
    w, h  = img.size
    font  = load_font(cfg["font"], cfg["size"])
    px    = int(w * cfg["x"] / 100)
    py    = int(h * cfg["y"] / 100)
    layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw  = ImageDraw.Draw(layer)
    bbox  = draw.textbbox((0, 0), name, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((px - tw // 2, py - th // 2), name,
              font=font, fill=hex_to_rgba(cfg["color"]))
    out = Image.alpha_composite(img, layer).convert("RGB")
    buf = io.BytesIO()
    out.save(buf, format="PNG", dpi=(300, 300))
    return buf.getvalue()

def cert_to_pdf(png: bytes, name: str) -> bytes:
    buf    = io.BytesIO()
    pw, ph = landscape(A4)
    c      = pdf_canvas.Canvas(buf, pagesize=(pw, ph))
    img    = Image.open(io.BytesIO(png)).convert("RGB")
    iw, ih = img.size
    sc     = min(pw / iw, ph / ih)
    nw, nh = iw * sc, ih * sc
    tmp    = io.BytesIO()
    img.save(tmp, format="PNG"); tmp.seek(0)
    c.drawImage(ImageReader(tmp), (pw - nw) / 2, (ph - nh) / 2, nw, nh, mask="auto")
    c.setFont("Helvetica-Bold", 9)
    c.setFillColorRGB(.5, .5, .5)
    c.drawCentredString(pw / 2, 14,
        f"{name}  |  {st.session_state.event_name}  |  {datetime.now().strftime('%Y-%m-%d')}")
    c.save()
    return buf.getvalue()

def make_qr(url: str) -> bytes:
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_H,
                       box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    buf = io.BytesIO()
    qr.make_image(fill_color="#0b132b", back_color="white").save(buf, format="PNG")
    return buf.getvalue()

def cur_cfg() -> dict:
    return {
        "x":     st.session_state.text_x,
        "y":     st.session_state.text_y,
        "size":  st.session_state.font_size,
        "color": st.session_state.text_color,
        "font":  st.session_state.selected_font,
    }

def build_excel(regs: list) -> bytes:
    wb  = openpyxl.Workbook()
    hf  = PatternFill("solid", fgColor="1E1B4B")
    hf2 = PatternFill("solid", fgColor="0B132B")
    hfn = XFont(bold=True, color="FFFFFF", size=12)
    bdr = Border(bottom=Side(style="thin", color="334466"))

    ws = wb.active
    ws.title = "Registrations"

    ws.merge_cells("A1:H1")
    t = ws["A1"]
    t.value = f"  {st.session_state.event_name} — Registration Data"
    t.font  = XFont(bold=True, color="FFD159", size=14)
    t.fill  = hf2
    t.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 34

    ws.merge_cells("A2:H2")
    info = ws["A2"]
    try:
        d = datetime.strptime(st.session_state.event_date, "%Y-%m-%d")
        day = d.strftime("%A")
    except Exception:
        day = ""
    info.value = (f"Date: {st.session_state.event_date}  ({day})  |  "
                  f"Venue: {st.session_state.event_venue}  |  "
                  f"Topic: {st.session_state.event_topic}  |  "
                  f"Organizer: {st.session_state.organizer}  |  "
                  f"Total: {len(regs)}")
    info.font = XFont(color="7ECEFD", size=10)
    info.fill = hf
    info.alignment = Alignment(horizontal="center")
    ws.row_dimensions[2].height = 18

    cols_info = [("#",5),("Full Name",28),("Roll No",16),
                 ("Department",24),("Batch",14),("Category",16),
                 ("Date",14),("Time",10)]
    for ci, (h, w) in enumerate(cols_info, 1):
        cell = ws.cell(row=3, column=ci, value=h)
        cell.font = hfn; cell.fill = hf
        cell.alignment = Alignment(horizontal="center")
        ws.column_dimensions[get_column_letter(ci)].width = w
    ws.row_dimensions[3].height = 22

    for ri, rec in enumerate(regs, 4):
        alt = PatternFill("solid", fgColor="0F1B35" if ri % 2 == 0 else "1A2550")
        vals = [ri-3, rec.get("name",""), rec.get("roll_no",""),
                rec.get("department",""), rec.get("batch",""),
                rec.get("category",""), rec.get("date",""), rec.get("time","")]
        for ci, val in enumerate(vals, 1):
            c = ws.cell(row=ri, column=ci, value=val)
            c.font = XFont(color="E0E0E0", size=11); c.fill = alt; c.border = bdr
            c.alignment = Alignment(
                horizontal="center" if ci in [1, 6, 7, 8] else "left",
                vertical="center")
        ws.row_dimensions[ri].height = 20

    ws2 = wb.create_sheet("Category Summary")
    ws2.merge_cells("A1:C1")
    t2 = ws2["A1"]
    t2.value = "Category-wise Summary"
    t2.font  = XFont(bold=True, color="FFD159", size=13)
    t2.fill  = hf2
    t2.alignment = Alignment(horizontal="center")
    ws2.row_dimensions[1].height = 28
    for ci, h in enumerate(["Category","Count","Members (Roll No)"], 1):
        c = ws2.cell(row=2, column=ci, value=h)
        c.font = hfn; c.fill = hf
        c.alignment = Alignment(horizontal="center")
    cats: dict = {}
    for rec in regs:
        cats.setdefault(rec.get("category","Other"), []).append(
            f"{rec.get('name','')} [{rec.get('roll_no','')}]")
    for ri, (cat, names) in enumerate(cats.items(), 3):
        ws2.cell(row=ri, column=1, value=cat).font = XFont(bold=True, color="FFD159")
        ws2.cell(row=ri, column=2, value=len(names)).font = XFont(color="E0E0E0")
        ws2.cell(row=ri, column=3, value=", ".join(names)).font = XFont(color="E0E0E0")
        for col in range(1, 4):
            ws2.cell(row=ri, column=col).fill = hf
    ws2.column_dimensions["A"].width = 20
    ws2.column_dimensions["B"].width = 10
    ws2.column_dimensions["C"].width = 80

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()

# ─────────────────────────────────────────────────────────────────
#  ROUTING
# ─────────────────────────────────────────────────────────────────
qp   = st.query_params
page = qp.get("page", "admin")

# ═════════════════════════════════════════════════════════════════
#  STUDENT FORM PAGE
# ═════════════════════════════════════════════════════════════════
if page == "form":
    event = qp.get("event", st.session_state.event_name).replace("%20", " ")
    cats  = qp.get("cats",  st.session_state.categories).replace("%20", " ").split(",")
    cats  = [c.strip() for c in cats if c.strip()]

    st.markdown(f"""
    <div style="text-align:center;padding:30px 0 10px;">
      <div style="font-size:3.5rem;">🎓</div>
      <h1 style="color:#ffd159;font-size:2rem;margin:8px 0;">{event}</h1>
      <p style="color:#7ecefd;font-size:1rem;">
        Registration Form — Apni details bharein
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<div class="card">', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        name   = st.text_input("👤 Full Name ✱",
                               placeholder="Muhammad Ali Khan")
        dept   = st.text_input("🏫 Department ✱",
                               placeholder="Computer Science")
    with c2:
        rollno = st.text_input("🔢 Roll No ✱",
                               placeholder="24-BSCS-45")
        batch  = st.text_input("📅 Batch / Year ✱",
                               placeholder="2024")

    category = st.selectbox("🏷️ Category — Choose option accordingly ✱", cats)

    st.markdown("---")
    submitted = st.button("✅  Jama Karein / Submit", use_container_width=True)

    if submitted:
        n = name.strip(); r = rollno.strip()
        d = dept.strip(); b = batch.strip()
        missing = ([f for f, v in
                   [("Full Name",n),("Roll No",r),("Department",d),("Batch",b)]
                   if not v])
        if missing:
            st.error("❌ Fill this field: **" + "  |  ".join(missing) + "**")
        else:
            now = datetime.now()
            st.session_state.registrations.append({
                "name": n, "roll_no": r, "department": d,
                "batch": b, "category": category,
                "event": event,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
            })
            st.markdown(f"""
            <div class="card-green">
              <h3 style="color:#2ecc71;text-align:center;margin:0 0 14px;">
                ✅ Registration Kamiyab Ho Gayi!
              </h3>
              <table style="width:100%;color:#c5d8f0;font-size:1.05rem;border-collapse:collapse;">
                <tr><td style="padding:5px 0;">👤 <b>Naam</b></td>
                    <td style="padding:5px 0;color:white;">{n}</td></tr>
                <tr><td style="padding:5px 0;">🔢 <b>Roll No</b></td>
                    <td style="padding:5px 0;color:white;">{r}</td></tr>
                <tr><td style="padding:5px 0;">🏫 <b>Department</b></td>
                    <td style="padding:5px 0;color:white;">{d}</td></tr>
                <tr><td style="padding:5px 0;">📅 <b>Batch</b></td>
                    <td style="padding:5px 0;color:white;">{b}</td></tr>
                <tr><td style="padding:5px 0;">🏷️ <b>Category</b></td>
                    <td style="padding:5px 0;color:white;">{category}</td></tr>
                <tr><td style="padding:5px 0;">🕐 <b>Time</b></td>
                    <td style="padding:5px 0;color:white;">{now.strftime('%H:%M:%S')}</td></tr>
              </table>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#7ecefd33;font-size:.8rem;margin-top:24px;">'
        'Developed by Abdul Samad — SBBU Nawabshah</p>',
        unsafe_allow_html=True)
    st.stop()

# ═════════════════════════════════════════════════════════════════
#  ADMIN PAGE
# ═════════════════════════════════════════════════════════════════
st.markdown("# 🎓 QR Certificate System")
st.markdown(
    '<p style="text-align:center;color:#7ecefd;">'
    'Abdul Samad | Shaheed Benazir Bhutto University Nawabshah</p>',
    unsafe_allow_html=True)
st.markdown("---")

# ── Auth ─────────────────────────────────────────────────────────
if not st.session_state.admin_auth:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Admin Login")
        pwd = st.text_input("Password", type="password")
        if st.button("🔓 Login", use_container_width=True):
            if pwd == st.session_state.admin_password:
                st.session_state.admin_auth = True
                st.rerun()
            else:
                st.error("❌ Galat password!")
        st.caption("Password is required!")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📋 Event Settings")
    st.session_state.event_name  = st.text_input("Event Name",          st.session_state.event_name)
    st.session_state.event_topic = st.text_input("Topic",               st.session_state.event_topic)
    st.session_state.event_date  = st.text_input("Date (YYYY-MM-DD)",   st.session_state.event_date)
    st.session_state.event_venue = st.text_input("Venue",               st.session_state.event_venue)
    st.session_state.organizer   = st.text_input("Organizer",           st.session_state.organizer)
    st.session_state.categories  = st.text_input("Categories (comma)",  st.session_state.categories)

    st.markdown("---")
    st.markdown("## 🎨 Certificate Text")
    st.session_state.font_size  = st.slider("Font Size",        20, 250, st.session_state.font_size)
    st.session_state.text_x    = st.slider("Horizontal % (←→)", 0, 100, st.session_state.text_x)
    st.session_state.text_y    = st.slider("Vertical %   (↑↓)", 0, 100, st.session_state.text_y)
    st.session_state.text_color= st.color_picker("Text Color",  st.session_state.text_color)

    st.markdown("---")
    st.markdown("## 🔤 Font")
    search_q = st.text_input("🔍 Font Search...", placeholder="e.g. bold, times, gothic")

    all_fonts = list(FONTS.keys())
    if search_q.strip():
        matched = [f for f in all_fonts if search_q.strip().lower() in f.lower()]
        if matched:
            st.caption(f"{len(matched)} fonts mile")
            idx = matched.index(st.session_state.selected_font) \
                  if st.session_state.selected_font in matched else 0
            st.session_state.selected_font = st.selectbox(
                "Results:", matched, index=idx, key="fs_search")
        else:
            st.warning("Koi font nahi mila")
    else:
        for cat_lbl, cat_fonts in FONT_CATS.items():
            if not cat_fonts:
                continue
            expand = "Arial" in cat_lbl or "Sans" in cat_lbl
            with st.expander(cat_lbl, expanded=expand):
                for fn in cat_fonts:
                    lbl = ("✅ " if st.session_state.selected_font == fn else "") + fn
                    if st.button(lbl, key=f"fb_{fn}", use_container_width=True):
                        st.session_state.selected_font = fn
                        st.rerun()

    st.markdown(f"**Selected:** `{st.session_state.selected_font}`")
    st.markdown("---")
    with st.expander("🔑 Change Password"):
        np_ = st.text_input("New Password", type="password")
        if st.button("Update") and np_:
            st.session_state.admin_password = np_
            st.success("✅ Updated!")
    if st.button("🚪 Logout"):
        st.session_state.admin_auth = False
        st.rerun()

# ── TABS ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔳 QR & Registration",
    "📊 Registered Data",
    "🖼️ Template & Preview",
    "🚀 Generate Certificates",
    "☁️ GitHub Guide",
])

# ═══════════════════════════════════════
#  TAB 1 — QR & Registration
# ═══════════════════════════════════════
with tab1:
    cl, cr = st.columns(2)

    with cl:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔳 QR Code Generate Karein")

        app_url = st.text_input(
            "🌐 Apni Deployed App URL",
            placeholder="https://yourname-appname.streamlit.app",
            help="Streamlit Cloud par deploy hone ke baad real URL paste karo")

        if st.button("🔳 QR Generate Karein", use_container_width=True):
            if not app_url.strip() or "your" in app_url.lower():
                st.error("❌ Real URL paste karo! 'your-app' placeholder nahi chalega.")
            else:
                ev   = st.session_state.event_name.replace(" ", "%20")
                cats = st.session_state.categories.replace(" ", "%20")
                url  = f"{app_url.rstrip('/')}/?page=form&event={ev}&cats={cats}"
                st.session_state.qr_url  = url
                st.session_state.qr_data = make_qr(url)
                st.success("✅ QR Code tayar!")

        if st.session_state.qr_data:
            st.image(st.session_state.qr_data, width=240,
                     caption="Yeh QR print karo → event mein lagao")
            st.code(st.session_state.qr_url, language=None)
            st.download_button("⬇️ QR PNG Download",
                data=st.session_state.qr_data,
                file_name="registration_qr.png", mime="image/png",
                use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📱 Student ka Experience")
        st.markdown("""
**QR Scan karne ke baad student dekhega:**

| Field | Example |
|-------|---------|
| 👤 Full Name | Muhammad Ali Khan |
| 🔢 Roll No | 24-BSCS-45 |
| 🏫 Department | Computer Science |
| 📅 Batch | 2024 |
| 🏷️ Category | Participant |

✅ Submit hote hi data yahan **Tab 2** mein dikh jata hai  
📊 Admin **Tab 2** se Excel download kar sakta hai  
🎓 **Tab 4** mein certificates generate hote hain
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ✏️ Manual Registration (Bina QR)")
        with st.form("manual_reg"):
            mc1, mc2 = st.columns(2)
            with mc1:
                mn = st.text_input("👤 Full Name")
                md = st.text_input("🏫 Department")
            with mc2:
                mr = st.text_input("🔢 Roll No")
                mb = st.text_input("📅 Batch")
            cat_list = [c.strip() for c in
                        st.session_state.categories.split(",") if c.strip()]
            mc = st.selectbox("🏷️ Category", cat_list)
            if st.form_submit_button("➕ Add Registration", use_container_width=True):
                if mn.strip() and mr.strip():
                    now = datetime.now()
                    st.session_state.registrations.append({
                        "name":mn.strip(),"roll_no":mr.strip(),
                        "department":md.strip(),"batch":mb.strip(),
                        "category":mc,"event":st.session_state.event_name,
                        "date":now.strftime("%Y-%m-%d"),
                        "time":now.strftime("%H:%M:%S"),
                    })
                    st.success(f"✅ {mn.strip()} add ho gaya!")
                    st.rerun()
                else:
                    st.error("Naam aur Roll No zaroori hain!")
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════
#  TAB 2 — Registered Data
# ═══════════════════════════════════════
with tab2:
    regs = st.session_state.registrations
    st.markdown("### 📊 Registered Data")

    cat_list = [c.strip() for c in st.session_state.categories.split(",") if c.strip()]
    m_cols   = st.columns(len(cat_list) + 1)
    m_cols[0].metric("Total", len(regs))
    for i, cat in enumerate(cat_list):
        m_cols[i+1].metric(cat, sum(1 for r in regs if r.get("category") == cat))

    st.markdown("---")

    if regs:
        df = pd.DataFrame(regs)
        rename = {"name":"Full Name","roll_no":"Roll No","department":"Department",
                  "batch":"Batch","category":"Category","event":"Event",
                  "date":"Date","time":"Time"}
        df = df.rename(columns={k:v for k,v in rename.items() if k in df.columns})

        # Filter by category
        filter_cat = st.selectbox("Category se filter karo:",
                                  ["All"] + cat_list, key="flt_cat")
        if filter_cat != "All":
            df_show = df[df["Category"] == filter_cat]
        else:
            df_show = df
        st.dataframe(df_show, use_container_width=True, height=380)

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            excel = build_excel(regs)
            fname = f"{st.session_state.event_name.replace(' ','_')}_Registrations.xlsx"
            st.download_button("📊 Excel Download",
                data=excel, file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with c2:
            txt = "\n".join(
                f"{r['name']} | {r['roll_no']} | {r['department']} | {r['batch']} | {r['category']}"
                for r in regs)
            st.download_button("📄 TXT Download",
                data=txt.encode(), file_name="registrations.txt",
                mime="text/plain", use_container_width=True)
        with c3:
            if st.button("🗑️ Sab Clear Karo", use_container_width=True):
                st.session_state.registrations = []
                st.rerun()
    else:
        st.info("📭 Koi registration nahi hua abhi. QR scan hone par yahan data aayega.")

# ═══════════════════════════════════════
#  TAB 3 — Template & Preview
# ═══════════════════════════════════════
with tab3:
    cl, cr = st.columns([1, 1])

    with cl:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🖼️ Certificate Template Upload")
        tpl = st.file_uploader("Template (.png/.jpg/.jpeg)",
                               type=["png","jpg","jpeg"])
        if tpl:
            st.session_state.template_bytes = tpl.read()
            img_tmp = Image.open(io.BytesIO(st.session_state.template_bytes))
            st.success(f"✅ {tpl.name}  —  {img_tmp.width}×{img_tmp.height}px")

        if st.session_state.template_bytes:
            st.image(st.session_state.template_bytes,
                     caption="Current Template", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with cr:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 👁️ Live Preview")
        st.info("💡 Sidebar se font, size, color, position adjust karo!")

        if st.session_state.template_bytes:
            st.markdown(
                f"**Font:** `{st.session_state.selected_font}` | "
                f"**Size:** `{st.session_state.font_size}` | "
                f"**Pos:** `({st.session_state.text_x}%, {st.session_state.text_y}%)` | "
                f"**Color:** `{st.session_state.text_color}`")

            prev_name = st.text_input("Preview naam:", value="Muhammad Ali Khan")
            png_prev  = generate_cert(prev_name, st.session_state.template_bytes, cur_cfg())
            st.image(png_prev, use_container_width=True, caption=f"Preview: {prev_name}")

            pa, pb = st.columns(2)
            with pa:
                st.download_button("⬇️ PNG", png_prev,
                    file_name=f"Preview_{prev_name}.png", mime="image/png",
                    use_container_width=True)
            with pb:
                st.download_button("⬇️ PDF", cert_to_pdf(png_prev, prev_name),
                    file_name=f"Preview_{prev_name}.pdf", mime="application/pdf",
                    use_container_width=True)
        else:
            st.warning("⚠️ Pehle template upload karo (left side)")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Preview All Registered Names ──
    if st.session_state.template_bytes and st.session_state.registrations:
        st.markdown("---")
        st.markdown("### 👁️ Sabke Certificates Preview Karo")
        names_all = [r["name"] for r in st.session_state.registrations]
        show_n    = st.slider("Kitne preview karein?",
                              1, min(len(names_all), 30), min(6, len(names_all)))
        per_row   = 3
        for i in range(0, show_n, per_row):
            row_n = names_all[i:i+per_row]
            cs    = st.columns(per_row)
            for ci, nm in enumerate(row_n):
                with cs[ci]:
                    pv = generate_cert(nm, st.session_state.template_bytes, cur_cfg())
                    st.image(pv, caption=nm, use_container_width=True)
                    st.download_button(f"⬇️ {nm[:16]}",
                        data=pv, file_name=f"{nm}.png",
                        mime="image/png", key=f"pv_{nm}_{i}_{ci}")

# ═══════════════════════════════════════
#  TAB 4 — Generate Certificates
# ═══════════════════════════════════════
with tab4:
    st.markdown("### 🚀 Certificates Generate Karein")

    if not st.session_state.template_bytes:
        st.markdown('<div class="card-warn">⚠️ Pehle Tab 3 mein template upload karo!</div>',
                    unsafe_allow_html=True)
    elif not st.session_state.registrations:
        st.markdown('<div class="card-warn">⚠️ Koi registered naam nahi hai. QR scan karwao ya Tab 1 mein manually add karo.</div>',
                    unsafe_allow_html=True)
    else:
        regs  = st.session_state.registrations
        names = [r["name"] for r in regs]

        # Stats
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Names",    len(names))
        c2.metric("Font",           st.session_state.selected_font[:14]+"..."
                                    if len(st.session_state.selected_font)>14
                                    else st.session_state.selected_font)
        c3.metric("Size",           st.session_state.font_size)
        c4.metric("Position",       f"{st.session_state.text_x}%, {st.session_state.text_y}%")

        st.markdown("---")

        # Format options
        fc1, fc2 = st.columns(2)
        with fc1:
            do_png = st.checkbox("✅ PNG Generate karo", value=True)
        with fc2:
            do_pdf = st.checkbox("✅ PDF Generate karo", value=True)

        if st.button(f"🚀 Generate All {len(names)} Certificates",
                     use_container_width=True):
            cfg_now = cur_cfg()
            prog    = st.progress(0)
            status  = st.empty()
            buf_zip = io.BytesIO()

            with zipfile.ZipFile(buf_zip, "w", zipfile.ZIP_DEFLATED) as zf:
                for i, rec in enumerate(regs):
                    nm = rec["name"]
                    cat= rec.get("category","Other")
                    status.markdown(
                        f"⏳ **{nm}** [{cat}]  ({i+1}/{len(regs)})")
                    png = generate_cert(nm, st.session_state.template_bytes, cfg_now)
                    if do_png:
                        zf.writestr(f"PNG/{cat}/{nm}.png", png)
                    if do_pdf:
                        zf.writestr(f"PDF/{cat}/{nm}.pdf", cert_to_pdf(png, nm))
                    prog.progress((i+1)/len(regs))

            status.success(f"✅ {len(regs)} certificates ready!")
            st.balloons()

            zname = f"{st.session_state.event_name.replace(' ','_')}_Certificates.zip"
            st.download_button(
                f"⬇️ Download All ({len(regs)}) — ZIP",
                data=buf_zip.getvalue(),
                file_name=zname, mime="application/zip",
                use_container_width=True)

            st.markdown("""
            <div class="card">
            📁 ZIP folder structure:<br>
            &nbsp;&nbsp;📂 <b>PNG/</b><br>
            &nbsp;&nbsp;&nbsp;&nbsp;📂 Participant/ → sab participant certificates<br>
            &nbsp;&nbsp;&nbsp;&nbsp;📂 Teacher/ → sab teacher certificates<br>
            &nbsp;&nbsp;&nbsp;&nbsp;📂 Speaker/ → ...<br>
            &nbsp;&nbsp;📂 <b>PDF/</b><br>
            &nbsp;&nbsp;&nbsp;&nbsp;📂 Participant/ → PDF format<br>
            &nbsp;&nbsp;&nbsp;&nbsp;📂 Teacher/ → ...
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════
#  TAB 5 — GitHub Guide
# ═══════════════════════════════════════
with tab5:
    st.markdown("""
<div class="card">

## ☁️ GitHub + Streamlit Cloud — Free Hosting

### Step 1 — GitHub par Repository banao
1. [github.com](https://github.com) → Login → **New Repository**
2. Name: `qr-certificate-system` → **Public** → Create

### Step 2 — Sirf 2 files upload karo
```
app.py
requirements.txt
```
Ya PowerShell se:
```bash
cd d:/Avalon.AI
git init
git add app.py requirements.txt
git commit -m "QR Certificate System"
git remote add origin https://github.com/USERNAME/qr-certificate-system.git
git push -u origin main
```

### Step 3 — Streamlit Cloud Deploy
1. [share.streamlit.io](https://share.streamlit.io) → GitHub se login
2. **New App** → Repo select → `app.py` → **Deploy**
3. ⏳ 2-3 minute mein live!

### Step 4 — Real URL copy karo
```
https://yourname-qr-certificate-system-app-xxxx.streamlit.app
```
Yeh URL **Tab 1 → QR Generate** mein paste karo → QR generate → Print karo ✅

### Update karne ka tarika (future mein)
```bash
cd d:/Avalon.AI
git add app.py
git commit -m "Update"
git push
```
Streamlit Cloud automatic update ho jata hai! 🚀

</div>
    """, unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#7ecefd66;font-size:.85rem;">'
    '© QR Certificate System | Abdul Samad | SBBU Nawabshah</p>',
    unsafe_allow_html=True)
