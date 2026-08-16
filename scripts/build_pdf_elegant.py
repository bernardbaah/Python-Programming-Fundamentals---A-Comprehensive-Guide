"""
Elegant redesign — Python Programming Fundamentals (Interior)
Bernard Baah / Filly Coder · AI Future Series
Amazon KDP 8.5 × 11 in
"""
import json, os, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib import colors

# ── Palette ──────────────────────────────────────────────────────────────────
NAVY   = HexColor('#0a1628')
SLATE  = HexColor('#1e3a5f')
GOLD   = HexColor('#c9a84c')
GOLD2  = HexColor('#e8d49c')
LGRAY  = HexColor('#f2f5fa')
MGRAY  = HexColor('#dce3ee')
DGRAY  = HexColor('#4a4a4a')
CGRAY  = HexColor('#888888')
DCODE  = HexColor('#111827')
LCODE  = HexColor('#e2e8f0')
W      = white
B      = black

# ── Page geometry ─────────────────────────────────────────────────────────────
PW, PH = letter
ML = MR = 1.0 * inch
MT = 1.1 * inch   # top margin (leaves room for running header)
MB = 0.9 * inch   # bottom margin (leaves room for footer)
TW = PW - ML - MR   # text width = 6.5 in

# ── Global state for running headers ─────────────────────────────────────────
class _State:
    chapter_num   = 0
    chapter_title = ""
S = _State()

# ── Page callbacks ────────────────────────────────────────────────────────────
def _draw_page(canvas, doc):
    canvas.saveState()
    pg = canvas.getPageNumber()

    # ── Running header ──
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(CGRAY)
    if pg > 2:   # skip title + TOC pages
        if pg % 2 == 0:   # left page
            canvas.drawString(ML, PH - 0.62*inch, 'PYTHON PROGRAMMING FUNDAMENTALS')
        else:             # right page
            if S.chapter_title:
                label = f'CHAPTER {S.chapter_num}  ·  {S.chapter_title.upper()}'
                canvas.drawRightString(PW - MR, PH - 0.62*inch, label[:60])
    # Hair rule under header
    canvas.setStrokeColor(MGRAY)
    canvas.setLineWidth(0.4)
    canvas.line(ML, PH - 0.68*inch, PW - MR, PH - 0.68*inch)

    # ── Footer ──
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(0.75)
    canvas.line(ML, MB - 0.22*inch, PW - MR, MB - 0.22*inch)
    canvas.setFont('Helvetica', 9)
    canvas.setFillColor(DGRAY)
    canvas.drawCentredString(PW / 2, MB - 0.44*inch, str(pg))

    canvas.restoreState()

# ── Flowables ─────────────────────────────────────────────────────────────────
class _StateMarker(Flowable):
    """Zero-height marker that updates the running-header state."""
    def __init__(self, num, title):
        Flowable.__init__(self)
        self.num, self.title = num, title
        self.width = self.height = 0
    def draw(self):
        S.chapter_num   = self.num
        S.chapter_title = self.title

class ChapterBanner(Flowable):
    """Full-width navy chapter opener banner."""
    H = 2.6 * inch

    def __init__(self, num, title):
        Flowable.__init__(self)
        self.num   = num
        self.title = title
        self.width = TW
        self.height = self.H

    def draw(self):
        c = self.canv
        h = self.H
        w = self.width

        # Navy background
        c.setFillColor(NAVY)
        c.rect(0, 0, w, h, fill=1, stroke=0)

        # Ghost large chapter number (right side, subtle)
        c.setFillColor(colors.Color(1, 1, 1, alpha=0.10))
        c.setFont('Helvetica-Bold', 130)
        c.drawRightString(w - 4, -18, str(self.num))

        # "CHAPTER N" label in gold near the top
        c.setFillColor(GOLD)
        c.setFont('Helvetica', 10)
        c.drawString(6, h - 28, f'CHAPTER  {self.num}')

        # Thin gold rule
        c.setStrokeColor(GOLD)
        c.setLineWidth(1)
        c.line(6, h - 36, w - 6, h - 36)

        # Chapter title — wrap if long
        c.setFillColor(W)
        c.setFont('Helvetica-Bold', 22)
        title = self.title
        # Simple word-wrap at ~28 chars per line
        words = title.split()
        lines, cur = [], []
        for word in words:
            if sum(len(x)+1 for x in cur) + len(word) > 30 and cur:
                lines.append(' '.join(cur))
                cur = [word]
            else:
                cur.append(word)
        if cur:
            lines.append(' '.join(cur))

        y = h - 68
        for line in lines[:3]:
            c.drawString(8, y, line)
            y -= 30

        # Gold bottom rule
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.line(0, 1, w, 1)

class GoldRule(Flowable):
    """Thin gold horizontal rule."""
    def __init__(self, width=TW, thickness=0.8):
        Flowable.__init__(self)
        self.width = width
        self._thick = thickness
        self.height = self._thick + 4

    def draw(self):
        self.canv.setStrokeColor(GOLD)
        self.canv.setLineWidth(self._thick)
        self.canv.line(0, 2, self.width, 2)

# ── Paragraph styles ──────────────────────────────────────────────────────────
_body_base = dict(fontName='Times-Roman', fontSize=11, leading=17,
                  spaceAfter=7, alignment=TA_JUSTIFY)

S_body   = ParagraphStyle('body',   **_body_base)
S_body1  = ParagraphStyle('body1',  firstLineIndent=0.22*inch, **_body_base)  # with indent
S_bullet = ParagraphStyle('bullet', leftIndent=18, firstLineIndent=0,
                           spaceBefore=2, spaceAfter=3,
                           fontName='Times-Roman', fontSize=11, leading=16,
                           alignment=TA_LEFT)
S_h2     = ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=13,
                           leading=18, textColor=NAVY,
                           spaceBefore=18, spaceAfter=4)
S_h3     = ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=11,
                           leading=16, textColor=SLATE,
                           spaceBefore=12, spaceAfter=3)
S_cap    = ParagraphStyle('cap', fontName='Helvetica-Oblique', fontSize=9,
                           leading=13, textColor=CGRAY,
                           spaceAfter=12, alignment=TA_CENTER)
S_toc    = ParagraphStyle('toc', fontName='Times-Roman', fontSize=11,
                           leading=20, textColor=DGRAY)
S_toc_h  = ParagraphStyle('toch', fontName='Helvetica-Bold', fontSize=10,
                           leading=14, textColor=GOLD, spaceBefore=8)
S_title  = ParagraphStyle('title', fontName='Helvetica-Bold', fontSize=30,
                           leading=38, textColor=NAVY, alignment=TA_CENTER, spaceAfter=10)
S_sub    = ParagraphStyle('sub', fontName='Helvetica', fontSize=15,
                           leading=22, textColor=SLATE, alignment=TA_CENTER, spaceAfter=10)
S_auth   = ParagraphStyle('auth', fontName='Helvetica-Bold', fontSize=13,
                           leading=20, textColor=B, alignment=TA_CENTER, spaceAfter=6)
S_series = ParagraphStyle('series', fontName='Helvetica-Oblique', fontSize=11,
                           leading=16, textColor=GOLD, alignment=TA_CENTER)
S_cs_lbl = ParagraphStyle('cslbl', fontName='Helvetica-Bold', fontSize=8,
                           leading=12, textColor=GOLD,
                           spaceBefore=0, spaceAfter=3,
                           charSpace=2)
S_cs_ttl = ParagraphStyle('csttl', fontName='Helvetica-Bold', fontSize=11,
                           leading=15, textColor=NAVY, spaceAfter=6)
S_cs_bod = ParagraphStyle('csbod', fontName='Times-Roman', fontSize=10,
                           leading=15, textColor=DGRAY, alignment=TA_JUSTIFY)
S_fig_ttl= ParagraphStyle('figttl', fontName='Helvetica-Bold', fontSize=9,
                           leading=13, textColor=LCODE, spaceAfter=4)
S_fig_bod= ParagraphStyle('figbod', fontName='Courier', fontSize=9,
                           leading=14, textColor=LCODE)
S_tbl_h  = ParagraphStyle('tblh', fontName='Helvetica-Bold', fontSize=9,
                           leading=13, textColor=W)
S_tbl_c  = ParagraphStyle('tblc', fontName='Times-Roman', fontSize=9,
                           leading=13, textColor=DGRAY)
S_tbl_cap= ParagraphStyle('tblcap', fontName='Helvetica-BoldOblique', fontSize=10,
                           leading=14, textColor=NAVY,
                           spaceBefore=14, spaceAfter=5)
S_ch_lbl = ParagraphStyle('chlbl', fontName='Helvetica', fontSize=10,
                           leading=14, textColor=GOLD, spaceAfter=2)

# ── New section styles ────────────────────────────────────────────────────────
S_ex_hdr  = ParagraphStyle('exhdr', fontName='Helvetica-Bold', fontSize=12,
                            leading=16, textColor=NAVY, spaceBefore=18, spaceAfter=4)
S_ex_q    = ParagraphStyle('exq',   fontName='Helvetica-Bold', fontSize=10,
                            leading=14, textColor=SLATE, spaceBefore=8, spaceAfter=2)
S_ex_hint = ParagraphStyle('exhnt', fontName='Times-Italic', fontSize=9,
                            leading=13, textColor=CGRAY, spaceAfter=3,
                            leftIndent=14)
S_diff    = ParagraphStyle('diff',  fontName='Helvetica-Bold', fontSize=8,
                            leading=12, textColor=GOLD, spaceAfter=6)
S_kc_hdr  = ParagraphStyle('kchdr', fontName='Helvetica-Bold', fontSize=12,
                            leading=16, textColor=NAVY, spaceBefore=18, spaceAfter=6)
S_kc_term = ParagraphStyle('kcterm',fontName='Helvetica-Bold', fontSize=10,
                            leading=14, textColor=SLATE, spaceAfter=2)
S_kc_def  = ParagraphStyle('kcdef', fontName='Times-Roman', fontSize=10,
                            leading=15, textColor=DGRAY, spaceAfter=6,
                            leftIndent=12)
S_sum_hdr = ParagraphStyle('sumhdr',fontName='Helvetica-Bold', fontSize=12,
                            leading=16, textColor=NAVY, spaceBefore=18, spaceAfter=6)
S_sum_bod = ParagraphStyle('sumbod',fontName='Times-Italic', fontSize=11,
                            leading=17, textColor=DGRAY,
                            alignment=TA_JUSTIFY, spaceAfter=7)

# ── Helpers ────────────────────────────────────────────────────────────────────
def esc(t):
    return str(t).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

_ARTIFACT_LINES = {
    'python programming fundamentals',
    'a comprehensive guide',
    'bernard baah',
    'filly coder',
    'filly coder · ai future series',
}

def sanitize(t):
    t = t.replace('\x00', '')
    t = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', t)
    return t

def clean_lines(lines):
    """Remove source-PDF running-header/footer artifacts."""
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append('')          # preserve paragraph separators
            continue
        low = stripped.lower()
        if low in _ARTIFACT_LINES:
            continue
        if re.match(r'^\d{1,3}$', stripped):   # bare page numbers
            continue
        out.append(stripped)
    return out

def make_image_elem(path, caption, max_w=5.4*inch):
    elems = []
    if path and os.path.exists(path):
        try:
            from PIL import Image as PILImage
            im = PILImage.open(path)
            iw, ih = im.size
            aspect = ih / iw
            w = min(max_w, 5.4*inch)
            h = w * aspect
            if h > 3.8*inch:
                h = 3.8*inch; w = h / aspect
            img = Image(path, width=w, height=h)
            img.hAlign = 'CENTER'
            elems.append(Spacer(1, 6))
            elems.append(img)
            elems.append(Paragraph(esc(caption), S_cap))
        except Exception as e:
            print(f"  img skip {path}: {e}")
    return elems

def make_table_elem(caption, headers, rows):
    elems = []
    if not headers:
        return elems
    elems.append(Paragraph(esc(caption), S_tbl_cap))
    ncols = len(headers)
    col_w = TW / ncols
    td = [[Paragraph(esc(str(h)), S_tbl_h) for h in headers]]
    for row in rows:
        td.append([Paragraph(esc(str(v)), S_tbl_c) for v in list(row)[:ncols]])
    tbl = Table(td, colWidths=[col_w]*ncols, repeatRows=1)
    tbl.setStyle(TableStyle([
        # Header
        ('BACKGROUND',    (0,0), (-1,0),  NAVY),
        ('TEXTCOLOR',     (0,0), (-1,0),  W),
        # Zebra
        ('ROWBACKGROUNDS',(0,1),(-1,-1),  [W, LGRAY]),
        # Grid
        ('GRID',          (0,0), (-1,-1), 0.3, MGRAY),
        ('LINEABOVE',     (0,0), (-1,0),  1.5, NAVY),
        ('LINEBELOW',     (0,-1),(-1,-1), 1,   GOLD),
        # Padding
        ('TOPPADDING',    (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING',   (0,0), (-1,-1), 7),
        ('RIGHTPADDING',  (0,0), (-1,-1), 7),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ]))
    elems.append(tbl)
    elems.append(Spacer(1, 10))
    return elems

def make_case_study(title, body):
    """Gold left-border case study box — multi-row so it can split across pages."""
    body_paras = [p.strip() for p in body.split('\n') if p.strip()] or [body.strip()]
    # Build rows: each paragraph is its own row so ReportLab can paginate
    rows = [
        ['', Paragraph('CASE STUDY', S_cs_lbl)],
        ['', Paragraph(esc(title), S_cs_ttl)],
    ] + [['', Paragraph(esc(p), S_cs_bod)] for p in body_paras]

    tbl = Table(rows, colWidths=[0.18*inch, TW - 0.18*inch])
    n = len(rows) - 1
    tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (0,-1),  GOLD),
        ('BACKGROUND',   (1,0), (1,-1),  LGRAY),
        ('BOX',          (0,0), (-1,-1), 0.3, MGRAY),
        # Left gold stripe: no padding
        ('LEFTPADDING',  (0,0), (0,-1),  0),
        ('RIGHTPADDING', (0,0), (0,-1),  0),
        ('TOPPADDING',   (0,0), (0,-1),  0),
        ('BOTTOMPADDING',(0,0), (0,-1),  0),
        # Content column padding
        ('LEFTPADDING',  (1,0), (1,-1),  14),
        ('RIGHTPADDING', (1,0), (1,-1),  12),
        ('TOPPADDING',   (1,0), (1,0),   10),   # first row top
        ('BOTTOMPADDING',(1,n), (1,n),   12),   # last row bottom
        ('TOPPADDING',   (1,1), (1,-1),  3),
        ('BOTTOMPADDING',(1,0), (1,-2),  3),
        ('VALIGN',       (0,0), (-1,-1), 'TOP'),
    ]))
    return [tbl, Spacer(1, 12)]

def make_figure(title, content):
    """Dark code/diagram box — multi-row so it can split across pages."""
    lines = [l for l in content.split('\n') if l.strip()]
    rows = [[Paragraph(esc(title), S_fig_ttl)]] + \
           [[Paragraph(esc(l), S_fig_bod)] for l in lines]

    tbl = Table(rows, colWidths=[TW])
    n = len(rows) - 1
    tbl.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), DCODE),
        ('LINEABOVE',    (0,0), (-1,0),  2.5, GOLD),
        ('LEFTPADDING',  (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING',   (0,0), (0,0),   10),
        ('BOTTOMPADDING',(0,n), (0,n),   12),
        ('TOPPADDING',   (0,1), (-1,-1), 1),
        ('BOTTOMPADDING',(0,0), (-1,-2), 1),
    ]))
    return [tbl, Spacer(1, 10)]

def merge_into_paragraphs(text):
    """
    Merge the line-by-line PDF-extracted text into logical paragraphs.
    Blank lines in the source mark paragraph boundaries.
    Returns a list of paragraph strings.
    """
    raw_lines = clean_lines(text.split('\n'))
    paras, current = [], []
    for line in raw_lines:
        if line == '':
            if current:
                paras.append(' '.join(current))
                current = []
        else:
            current.append(line)
    if current:
        paras.append(' '.join(current))
    return paras

def split_text(text, max_chars=2400):
    """Split merged paragraphs into render chunks."""
    paras = merge_into_paragraphs(text)
    chunks, cur, clen = [], [], 0
    for p in paras:
        if clen + len(p) > max_chars and cur:
            chunks.append(cur); cur, clen = [], 0
        cur.append(p); clen += len(p)
    if cur: chunks.append(cur)
    return chunks

# ── Load data ─────────────────────────────────────────────────────────────────
with open('book_data/chapters_text.json') as f:
    raw = json.load(f)
ch_text = raw['chapters']

ch_data = {}
for n in range(1, 26):
    p = f'book_data/chapter_{n:02d}.json'
    if os.path.exists(p):
        with open(p) as f:
            ch_data[n] = json.load(f)
print(f'Loaded {len(ch_data)} chapters')

try:
    from PIL import Image as _PIL
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print('PIL not found — images will be skipped')

# ── Build story ───────────────────────────────────────────────────────────────
story = []

# ── Title page ────────────────────────────────────────────────────────────────
story += [
    Spacer(1, 2.2*inch),
    Paragraph('Python Programming<br/>Fundamentals', S_title),
    Spacer(1, 0.1*inch),
    GoldRule(width=2.8*inch),   # centered-ish via centering tbl below
    Spacer(1, 0.2*inch),
    Paragraph('A Comprehensive Guide', S_sub),
    Spacer(1, 0.35*inch),
    Paragraph('Bernard Baah', S_auth),
    PageBreak(),
]

# ── Table of Contents ──────────────────────────────────────────────────────────
story += [
    Paragraph('TABLE OF CONTENTS', ParagraphStyle('toch2',
        fontName='Helvetica-Bold', fontSize=14, leading=20,
        textColor=NAVY, spaceAfter=6)),
    GoldRule(),
    Spacer(1, 14),
]
parts = {
    1:  'Part I: Python Foundations',
    6:  'Part II: Intermediate Python',
    13: 'Part III: Advanced Topics',
    17: 'Part IV: Web, Data & Machine Learning',
}
for n in range(1, 26):
    if n in parts:
        story.append(Paragraph(parts[n], S_toc_h))
    title = ch_data[n]['title'] if n in ch_data else f'Chapter {n}'
    story.append(Paragraph(f'Chapter {n} — {title}', S_toc))
story.append(PageBreak())

# ── Chapters ───────────────────────────────────────────────────────────────────
CH_TITLES = {
    1:'Introduction to Python', 2:'Getting Started',
    3:'Variables and Data Types', 4:'Control Structures',
    5:'Functions', 6:'Modules and Libraries',
    7:'File Handling', 8:'Exception Handling',
    9:'Data Structures', 10:'Object-Oriented Programming: Basics',
    11:'Object-Oriented Programming: Advanced Concepts',
    12:'Error Handling and Debugging',
    13:'Working with Files and Directories (Part 2)',
    14:'Introduction to Testing',
    15:'Introduction to Modules and Packages',
    16:'Advanced Modules and Packages',
    17:'Working with External APIs',
    18:'Introduction to Web Development with Flask',
    19:'Intermediate Flask Development',
    20:'Introduction to Data Visualization with Matplotlib',
    21:'Advanced Data Visualization with Seaborn',
    22:'Introduction to Machine Learning with scikit-learn',
    23:'Web Scraping with Python',
    24:'Python Automation',
    25:'Conclusion and Next Steps',
}

for ch_num in range(1, 26):
    ch   = ch_data.get(ch_num, {})
    title     = ch.get('title', CH_TITLES.get(ch_num, f'Chapter {ch_num}'))
    images    = ch.get('images', [])
    tables    = ch.get('tables', [])
    css       = ch.get('case_studies', [])
    figs      = ch.get('text_figures', [])
    exercises = ch.get('exercises', [])
    kc        = ch.get('key_concepts', [])
    summary   = ch.get('chapter_summary', '')
    orig      = sanitize(ch_text.get(str(ch_num), ''))

    print(f'  Ch {ch_num}: {title}  | {len(images)} imgs, {len(tables)} tbl, {len(css)} cs, {len(exercises)} ex')

    story.append(_StateMarker(ch_num, title))
    story.append(ChapterBanner(ch_num, title))
    story.append(Spacer(1, 18))

    chunks = split_text(orig, max_chars=1600)
    n_chunks = max(len(chunks), 1)

    # Calculate even distribution intervals
    img_interval = max(1, n_chunks // max(len(images), 1))
    tbl_interval = max(1, n_chunks // max(len(tables), 1))
    img_i = tbl_i = 0
    first_para = True

    for ci, chunk in enumerate(chunks):
        for line in chunk:
            line = line.strip()
            if not line: continue
            s = esc(line)
            if re.match(r'^(CHAPTER\s+\d+)', line, re.I): continue
            elif re.match(r'^\d+\.\d+\s+\S', line) or (len(line) < 65 and line.upper() == line and len(line) > 5):
                story.append(Paragraph(s, S_h2))
                story.append(GoldRule(width=TW, thickness=0.5))
                first_para = True
            elif line.startswith(('▪','•','-','–')):
                story.append(Paragraph('• ' + esc(line.lstrip('▪•-– ').strip()), S_bullet))
            else:
                st = S_body if first_para else S_body1
                story.append(Paragraph(s, st))
                first_para = False

        # Strategic image placement: evenly spaced
        if HAS_PIL and img_i < len(images) and (ci + 1) % img_interval == 0:
            img  = images[img_i]
            path = img.get('path', img) if isinstance(img, dict) else img
            cap  = img.get('caption', f'Figure {ch_num}.{img_i+1}') if isinstance(img, dict) else f'Figure {ch_num}.{img_i+1}'
            story.extend(make_image_elem(path, cap))
            img_i += 1

        # Strategic table placement: evenly spaced
        if tbl_i < len(tables) and (ci + 1) % tbl_interval == 0:
            t = tables[tbl_i]
            try:
                story.extend(make_table_elem(t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
                tbl_i += 1
            except Exception as e:
                print(f'    tbl err: {e}')

        # Case study after every ~4 chunks
        if css and (ci + 1) % max(1, n_chunks // len(css)) == 0:
            cs_i = (ci + 1) // max(1, n_chunks // len(css)) - 1
            if 0 <= cs_i < len(css):
                story.extend(make_case_study(css[cs_i].get('title',''), css[cs_i].get('body','')))

    # Remaining images (any not placed during body)
    if HAS_PIL:
        while img_i < len(images):
            img  = images[img_i]
            path = img.get('path', img) if isinstance(img, dict) else img
            cap  = img.get('caption', f'Figure {ch_num}.{img_i+1}') if isinstance(img, dict) else f'Figure {ch_num}.{img_i+1}'
            story.extend(make_image_elem(path, cap))
            img_i += 1

    # Remaining tables
    while tbl_i < len(tables):
        t = tables[tbl_i]
        try:
            story.extend(make_table_elem(t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
        except Exception as e:
            print(f'    tbl err: {e}')
        tbl_i += 1

    # Text figures
    for fig in figs:
        story.extend(make_figure(fig.get('title','Figure'), fig.get('content','')))

    # ── Key Concepts ──────────────────────────────────────────────────────────
    if kc:
        story.append(Paragraph('Key Concepts', S_kc_hdr))
        story.append(GoldRule(width=TW, thickness=0.5))
        story.append(Spacer(1, 6))
        for item in kc:
            term = item.get('term', '')
            defn = item.get('definition', '')
            if term:
                story.append(Paragraph(esc(term), S_kc_term))
            if defn:
                story.append(Paragraph(esc(defn), S_kc_def))

    # ── Exercises ─────────────────────────────────────────────────────────────
    if exercises:
        story.append(Paragraph('Practice Exercises', S_ex_hdr))
        story.append(GoldRule(width=TW, thickness=0.5))
        story.append(Spacer(1, 6))
        for i, ex in enumerate(exercises, 1):
            diff  = ex.get('difficulty', '')
            q     = ex.get('question', '')
            hint  = ex.get('hint', '')
            if q:
                story.append(Paragraph(f'{i}.  {esc(q)}', S_ex_q))
            if diff:
                story.append(Paragraph(f'Difficulty: {esc(diff)}', S_diff))
            if hint:
                story.append(Paragraph(f'Hint: {esc(hint)}', S_ex_hint))

    # ── Chapter Summary ───────────────────────────────────────────────────────
    if summary:
        story.append(Paragraph('Chapter Summary', S_sum_hdr))
        story.append(GoldRule(width=TW, thickness=0.5))
        story.append(Spacer(1, 6))
        for para in summary.split('\n\n') if '\n\n' in summary else [summary]:
            para = para.strip()
            if para:
                story.append(Paragraph(esc(para), S_sum_bod))

    story.append(PageBreak())

# ── Render ────────────────────────────────────────────────────────────────────
OUT = 'book_data/Python_Fundamentals_Interior.pdf'
doc = SimpleDocTemplate(
    OUT, pagesize=letter,
    leftMargin=ML, rightMargin=MR,
    topMargin=MT,  bottomMargin=MB,
    title='Python Programming Fundamentals',
    author='Bernard Baah',
)
doc.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
sz = os.path.getsize(OUT) / 1e6
print(f'\n✓ PDF → {OUT}  ({sz:.1f} MB)')
