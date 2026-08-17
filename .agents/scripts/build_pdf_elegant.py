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
DCODE  = HexColor('#1a2332')   # code block body background
LCODE  = HexColor('#e2e8f0')   # code text colour
DHDR   = HexColor('#0d1a2a')   # code block header strip
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
S_fig_ttl= ParagraphStyle('figttl', fontName='Helvetica-Bold', fontSize=8.5,
                           leading=12, textColor=GOLD, spaceAfter=0,
                           spaceBefore=0)
S_fig_bod= ParagraphStyle('figbod', fontName='Courier', fontSize=9.5,
                           leading=15, textColor=HexColor('#d4e0f0'))
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

def make_ref_strip(caption, headers, rows):
    """
    Reference strip — same data as a table but no grid.
    First column bold navy, subsequent columns regular gray.
    Thin horizontal rules between rows, gold bottom accent. No vertical lines.
    Used when the global table budget is exhausted.
    """
    if not rows:
        return []

    CAP_S  = ParagraphStyle('rs_cap',  fontName='Helvetica-BoldOblique', fontSize=8,
                            leading=11, textColor=NAVY, spaceAfter=4)
    KEY_S  = ParagraphStyle('rs_key',  fontName='Helvetica-Bold', fontSize=8.5,
                            leading=12, textColor=NAVY)
    VAL_S  = ParagraphStyle('rs_val',  fontName='Helvetica',      fontSize=8.5,
                            leading=12, textColor=HexColor('#333333'))
    HDR_S  = ParagraphStyle('rs_hdr',  fontName='Helvetica-Bold', fontSize=7.5,
                            leading=10, textColor=HexColor('#666666'))

    ncols  = max(len(headers), max((len(r) for r in rows), default=1))
    ncols  = min(ncols, 5)   # cap at 5 columns to avoid overflow
    col_w  = TW / ncols

    td = []
    # Optional muted header row
    if headers:
        td.append([Paragraph(esc(str(h))[:40], HDR_S) for h in list(headers)[:ncols]])
    for row in rows:
        cells = list(row)[:ncols]
        while len(cells) < ncols:
            cells.append('')
        r = [Paragraph(esc(str(cells[0]))[:80], KEY_S)]
        r += [Paragraph(esc(str(c))[:120], VAL_S) for c in cells[1:]]
        td.append(r)

    if not td:
        return []

    tbl = Table(td, colWidths=[col_w] * ncols, repeatRows=(1 if headers else 0))
    n = len(td) - 1
    hdr_rows = 1 if headers else 0

    style_cmds = [
        # Zebra: cream / white (no header counted)
        ('ROWBACKGROUNDS', (0, hdr_rows), (-1, -1), [W, HexColor('#fef9ed')]),
        # Muted header background
        ('BACKGROUND',     (0, 0), (-1, hdr_rows - 1), HexColor('#f0f0f0')) if headers else ('FONT', (0,0),(0,0), 'Helvetica', 8),
        # Thin horizontal rules between rows only
        ('LINEBELOW',      (0, 0), (-1, -2), 0.3, HexColor('#dddddd')),
        # Gold bottom accent
        ('LINEBELOW',      (0, n), (-1, n),  1.0, GOLD),
        # No vertical lines — no BOX, no GRID
        ('TOPPADDING',     (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING',  (0, 0), (-1, -1), 5),
        ('LEFTPADDING',    (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',   (0, 0), (-1, -1), 6),
        ('VALIGN',         (0, 0), (-1, -1), 'TOP'),
    ]
    tbl.setStyle(TableStyle(style_cmds))

    elems = []
    if caption:
        elems.append(Paragraph(esc(caption), CAP_S))
    elems += [tbl, Spacer(1, 10)]
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

def make_callout_box(concepts, max_items=4):
    """
    Slate left-stripe callout panel listing key concepts (term + brief definition).
    Distinct from the gold case-study stripe so the two elements read differently.
    """
    if not concepts:
        return []
    items = concepts[:max_items]

    SLATE_STRIPE = HexColor('#1e3a5f')
    BG           = HexColor('#edf2fa')
    LABEL_S = ParagraphStyle('cb_lbl', fontName='Helvetica-Bold', fontSize=7,
                             leading=9, textColor=GOLD, spaceAfter=0)
    TERM_S  = ParagraphStyle('cb_term', fontName='Helvetica-Bold', fontSize=9.5,
                             leading=13, textColor=HexColor('#0a1628'), spaceAfter=1)
    DEF_S   = ParagraphStyle('cb_def',  fontName='Helvetica',  fontSize=8.8,
                             leading=13, textColor=HexColor('#333333'), spaceAfter=6)

    STRIPE_W = 0.18 * inch
    BODY_W   = TW - STRIPE_W

    rows = [['', Paragraph('💡  KEY CONCEPTS AT A GLANCE', LABEL_S)]]
    for item in items:
        term = item.get('term', '')
        defn = item.get('definition', '')
        # Truncate long definitions to keep the box compact
        if len(defn) > 180:
            defn = defn[:177] + '…'
        if term:
            rows.append(['', Paragraph(esc(term), TERM_S)])
        if defn:
            rows.append(['', Paragraph(esc(defn), DEF_S)])

    n = len(rows) - 1
    tbl = Table(rows, colWidths=[STRIPE_W, BODY_W])
    tbl.setStyle(TableStyle([
        # Left slate stripe
        ('BACKGROUND',    (0,0), (0,-1),  SLATE_STRIPE),
        ('LEFTPADDING',   (0,0), (0,-1),  0),
        ('RIGHTPADDING',  (0,0), (0,-1),  0),
        ('TOPPADDING',    (0,0), (0,-1),  0),
        ('BOTTOMPADDING', (0,0), (0,-1),  0),
        # Content column
        ('BACKGROUND',    (1,0), (1,-1),  BG),
        ('BOX',           (0,0), (-1,-1), 0.4, MGRAY),
        ('LEFTPADDING',   (1,0), (1,-1),  14),
        ('RIGHTPADDING',  (1,0), (1,-1),  12),
        ('TOPPADDING',    (1,0), (1,0),   10),
        ('BOTTOMPADDING', (1,n), (1,n),   12),
        ('TOPPADDING',    (1,1), (1,-1),  3),
        ('BOTTOMPADDING', (1,0), (1,-2),  3),
        ('VALIGN',        (0,0), (-1,-1), 'TOP'),
    ]))
    return [tbl, Spacer(1, 12)]


def make_process_panel(title, headers, rows):
    """
    Numbered process / how-it-works panel.
    Navy header bar + numbered steps; each table row becomes one step.
    Step title = first cell; description = remaining cells joined.
    """
    if not rows:
        return []

    HDR_S  = ParagraphStyle('pp_hdr',  fontName='Helvetica-Bold', fontSize=9,
                             leading=12, textColor=white)
    NUM_S  = ParagraphStyle('pp_num',  fontName='Helvetica-Bold', fontSize=14,
                             leading=17, textColor=GOLD, alignment=TA_CENTER)
    STEP_S = ParagraphStyle('pp_step', fontName='Helvetica-Bold', fontSize=9.5,
                             leading=13, textColor=HexColor('#0a1628'))
    DESC_S = ParagraphStyle('pp_desc', fontName='Helvetica',  fontSize=8.8,
                             leading=13, textColor=HexColor('#444444'))

    NUM_W  = 0.42 * inch
    BODY_W = TW - NUM_W

    # Header row spanning full width
    hdr_tbl = Table(
        [[Paragraph(f'  ⚙  HOW IT WORKS: {esc(title.upper())}', HDR_S)]],
        colWidths=[TW]
    )
    hdr_tbl.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), NAVY),
        ('LEFTPADDING',   (0,0), (-1,-1), 10),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))

    step_rows = []
    for i, row in enumerate(rows, 1):
        cells = [str(c).strip() for c in row if str(c).strip()]
        if not cells:
            continue
        step_title = cells[0]
        step_desc  = '  ·  '.join(cells[1:]) if len(cells) > 1 else ''
        step_title = step_title[:90] + ('…' if len(step_title) > 90 else '')
        step_desc  = step_desc[:200] + ('…' if len(step_desc) > 200 else '')

        bg = HexColor('#f5f7fb') if i % 2 == 0 else white
        content_cell = [Paragraph(esc(step_title), STEP_S)]
        if step_desc:
            content_cell.append(Paragraph(esc(step_desc), DESC_S))

        step_rows.append([Paragraph(str(i), NUM_S), content_cell])

    if not step_rows:
        return []

    body_tbl = Table(step_rows, colWidths=[NUM_W, BODY_W])
    n = len(step_rows) - 1
    bg_cmds = []
    for idx in range(len(step_rows)):
        bg = HexColor('#f5f7fb') if idx % 2 == 0 else white
        bg_cmds.append(('BACKGROUND', (0,idx), (-1,idx), bg))

    body_tbl.setStyle(TableStyle([
        *bg_cmds,
        ('BOX',           (0,0), (-1,-1), 0.4, MGRAY),
        ('LINEBELOW',     (0,0), (-1,-2), 0.3, MGRAY),
        ('LINEBELOW',     (0,n), (-1,n),  1.0, GOLD),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 10),
        ('TOPPADDING',    (0,0), (-1,-1), 7),
        ('BOTTOMPADDING', (0,0), (-1,-1), 7),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
    ]))

    return [hdr_tbl, body_tbl, Spacer(1, 12)]


# ── Box-drawing → ASCII fallback (Courier lacks these glyphs) ────────────────
_BOX_MAP = str.maketrans({
    '┌':'+-', '┐':'-+', '└':'+-', '┘':'-+',
    '├':'+-', '┤':'-+', '┬':'+-', '┴':'+-', '┼':'+',
    '─':'-',  '━':'-',  '═':'=',
    '│':'|',  '║':'|',
    '▲':'^',  '▼':'v',  '△':'^', '▽':'v',
    '◄':'<',  '►':'>',  '←':'<', '→':'>',
    '↑':'^',  '↓':'v',  '↗':'/', '↘':'\\',
    '⟶':'->','⟵':'<-',
    '≠':'!=', '≤':'<=', '≥':'>=',
    '✓':'OK', '✗':'X',  '•':'-',
})

def _fix_code(text: str) -> str:
    """Translate box-drawing / special chars to Courier-safe ASCII."""
    return text.translate(_BOX_MAP)


def make_figure(title, content):
    """
    Elegant cream-and-white code block with gold accents.
    Header: warm cream (#fef9ed), macOS dots, title in navy, Python label.
    Body:   white (#ffffff), code in dark navy — high contrast for print.
    Border: 0.8 pt gold box + 2.5 pt gold top-accent + 0.5 pt gold rule separator.
    Body is a separate Table so long blocks paginate naturally.
    """
    # Sanitize box-drawing chars that Courier can't render
    content = _fix_code(content)
    lines   = content.split('\n')
    if not lines:
        lines = ['']

    # ── Palette ──────────────────────────────────────────────────────────
    HDR_BG  = HexColor('#fef9ed')   # warm cream header
    BODY_BG = HexColor('#ffffff')   # white body
    CODE_FG = HexColor('#1a2744')   # dark navy code text (print-safe on white)
    LABEL_C = HexColor('#9b7e3a')   # warm muted gold for "Python" label
    BORDER  = GOLD                  # gold border everywhere

    # ── Paragraph styles ─────────────────────────────────────────────────
    DOTS_S = ParagraphStyle('fig_dots', fontName='Helvetica', fontSize=9,
                            leading=12, textColor=NAVY)
    TTL_S  = ParagraphStyle('fig_ttl',  fontName='Helvetica-Bold', fontSize=9,
                            leading=12, textColor=NAVY)
    LANG_S = ParagraphStyle('fig_lang', fontName='Helvetica-BoldOblique', fontSize=7.5,
                            leading=12, textColor=LABEL_C, alignment=TA_RIGHT)
    COD    = ParagraphStyle('fig_cod',  fontName='Courier', fontSize=9.5,
                            leading=15, textColor=CODE_FG)
    COD_BL = ParagraphStyle('fig_bl',   fontName='Courier', fontSize=9.5,
                            leading=5,  textColor=CODE_FG)

    # ── Header: dots | title | Python ────────────────────────────────────
    DOTS_W  = 0.68 * inch
    LANG_W  = 0.60 * inch
    TITLE_W = TW - DOTS_W - LANG_W

    dots_xml = (
        '<font color="#e0483a">●</font>'   # red — slightly warmer on cream
        '  <font color="#d4a017">●</font>'  # amber
        '  <font color="#27ae60">●</font>'  # green
    )

    hdr = Table(
        [[Paragraph(dots_xml, DOTS_S),
          Paragraph(esc(title[:65]), TTL_S),
          Paragraph('Python', LANG_S)]],
        colWidths=[DOTS_W, TITLE_W, LANG_W]
    )
    hdr.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), HDR_BG),
        ('LEFTPADDING',   (0,0), (0, 0),  12),
        ('LEFTPADDING',   (1,0), (2, 0),  6),
        ('RIGHTPADDING',  (2,0), (2, 0),  12),
        ('RIGHTPADDING',  (0,0), (1, 0),  4),
        ('TOPPADDING',    (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 9),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        # Gold top accent + gold left/right borders
        ('LINEABOVE',     (0,0), (-1, 0), 2.5, BORDER),
        ('LINEBEFORE',    (0,0), (-1,-1), 0.8, BORDER),
        ('LINEAFTER',     (0,0), (-1,-1), 0.8, BORDER),
        # Thin gold separator at bottom of header
        ('LINEBELOW',     (0,0), (-1,-1), 0.5, BORDER),
    ]))

    # ── Body ─────────────────────────────────────────────────────────────
    body_rows = []
    for line in lines:
        if not line.strip():
            body_rows.append([Paragraph('', COD_BL)])
        else:
            body_rows.append([Paragraph(esc(line), COD)])
    if not body_rows:
        body_rows = [[Paragraph('', COD)]]

    body = Table(body_rows, colWidths=[TW])
    nb   = len(body_rows) - 1
    body.setStyle(TableStyle([
        ('BACKGROUND',    (0,0),  (-1,-1), BODY_BG),
        ('LEFTPADDING',   (0,0),  (-1,-1), 18),
        ('RIGHTPADDING',  (0,0),  (-1,-1), 14),
        ('TOPPADDING',    (0,0),  (0, 0),  10),
        ('TOPPADDING',    (0,1),  (-1,-1), 1),
        ('BOTTOMPADDING', (0,0),  (-1,-2), 1),
        ('BOTTOMPADDING', (0,nb), (-1,nb), 10),
        # Gold left / right / bottom borders
        ('LINEBEFORE',    (0,0),  (-1,-1), 0.8, BORDER),
        ('LINEAFTER',     (0,0),  (-1,-1), 0.8, BORDER),
        ('LINEBELOW',     (0,-1), (-1,-1), 0.8, BORDER),
    ]))

    # Header kept together; body pageinates freely
    return [Spacer(1, 10), KeepTogether([hdr]), body, Spacer(1, 14)]

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

# ── Book-wide table budget — max 15 real grid tables across all 25 chapters ───
MAX_BOOK_TABLES = 15
_book_tables_used = 0   # incremented each time a real table is placed

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
    Paragraph('Second Edition', S_sub),
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
    ch        = ch_data.get(ch_num, {})
    title     = ch.get('title', CH_TITLES.get(ch_num, f'Chapter {ch_num}'))
    images    = ch.get('images', [])
    tables    = ch.get('tables', [])
    css       = ch.get('case_studies', [])
    figs      = ch.get('text_figures', [])
    exercises = ch.get('exercises', [])
    kc        = ch.get('key_concepts', [])
    summary   = ch.get('chapter_summary', '')
    orig      = sanitize(ch_text.get(str(ch_num), ''))

    # ── Only 2 stock photos per chapter: first and middle of the array ─────
    photo_pool = [img for img in images if isinstance(img, dict)]
    photos_2   = []
    if photo_pool:
        photos_2.append(photo_pool[0])
    if len(photo_pool) > 1:
        photos_2.append(photo_pool[len(photo_pool)//2])

    # ── Generated chart for this chapter ────────────────────────────────────
    chart_path = f'book_data/images/charts/ch{ch_num:02d}_chart.png'
    has_chart  = os.path.exists(chart_path)

    # ── Limit to 2 real tables; derive callout + process panel from remaining ──
    tables_2   = tables[:2]          # only these rendered as actual tables
    proc_src   = tables[2] if len(tables) > 2 else None   # → numbered process panel
    # (tables[3] dropped — content covered by key_concepts callout + process panel)

    print(f'  Ch {ch_num}: {title}  | 2 photos, chart={has_chart}, '
          f'2 tbl, 1 callout, {"1 proc" if proc_src else "0 proc"}, {len(css)} cs')

    story.append(_StateMarker(ch_num, title))
    story.append(ChapterBanner(ch_num, title))
    story.append(Spacer(1, 18))

    chunks   = split_text(orig, max_chars=1600)
    n_chunks = max(len(chunks), 1)

    # ── Placement triggers (chunk indices, 0-based) ──────────────────────
    # Spread 7 elements: tbl1 · photo1 · callout · chart · tbl2 · photo2 · process
    tbl1_at     = max(0, n_chunks // 5 - 1)                       # ~1/5
    photo1_at   = max(tbl1_at + 1, n_chunks // 3 - 1)             # ~1/3
    callout_at  = max(photo1_at + 1, n_chunks * 2 // 5)           # ~2/5
    chart_at    = max(callout_at + 1, n_chunks // 2)              # ~1/2
    tbl2_at     = max(chart_at + 1, n_chunks * 3 // 5)            # ~3/5
    photo2_at   = max(tbl2_at + 1, n_chunks * 2 // 3)             # ~2/3
    process_at  = max(photo2_at + 1, n_chunks * 4 // 5)           # ~4/5
    cs_every    = max(1, n_chunks // max(len(css), 1))

    # Minimum chunk gap between any two images (photo or chart)
    # so they never land back-to-back regardless of chapter length
    min_img_gap  = max(2, n_chunks // 6)
    last_img_ci  = -9999   # chunk index when last image was placed

    photo_placed   = [False, False]
    chart_placed   = False
    tbl1_placed    = False
    tbl2_placed    = False
    callout_placed = False
    process_placed = False
    cs_placed      = set()
    first_para     = True

    for ci, chunk in enumerate(chunks):
        for line in chunk:
            line = line.strip()
            if not line: continue
            s = esc(line)
            if re.match(r'^(CHAPTER\s+\d+)', line, re.I):
                continue
            elif re.match(r'^\d+\.\d+\s+\S', line) or \
                 (len(line) < 65 and line.upper() == line and len(line) > 5):
                story.append(Paragraph(s, S_h2))
                story.append(GoldRule(width=TW, thickness=0.5))
                first_para = True
            elif line.startswith(('▪', '•', '-', '–')):
                story.append(Paragraph(
                    '• ' + esc(line.lstrip('▪•-– ').strip()), S_bullet))
            else:
                story.append(Paragraph(s, S_body if first_para else S_body1))
                first_para = False

        # ── Table 1 at ~1/5 — real table only if book budget allows ─────────
        if not tbl1_placed and ci >= tbl1_at and tables_2:
            t = tables_2[0]
            if _book_tables_used < MAX_BOOK_TABLES:
                try:
                    story.extend(make_table_elem(
                        t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
                    _book_tables_used += 1
                except Exception as e:
                    print(f'    tbl1 err: {e}')
                    story.extend(make_ref_strip(
                        t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
            else:
                story.extend(make_ref_strip(
                    t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
            tbl1_placed = True

        # ── Photo 1 at ~1/3 — respect min gap ────────────────────────────
        if (HAS_PIL and not photo_placed[0] and ci >= photo1_at
                and photos_2 and ci - last_img_ci >= min_img_gap):
            img = photos_2[0]
            story.extend(make_image_elem(img.get('path',''),
                                         img.get('caption', f'Figure {ch_num}.1')))
            photo_placed[0] = True
            last_img_ci = ci

        # ── Callout box at ~2/5 (key concepts) ───────────────────────────
        if not callout_placed and ci >= callout_at and kc:
            story.extend(make_callout_box(kc, max_items=4))
            callout_placed = True

        # ── Matplotlib chart at ~1/2 — respect min gap ───────────────────
        if (HAS_PIL and not chart_placed and has_chart and ci >= chart_at
                and ci - last_img_ci >= min_img_gap):
            caption = f'Figure {ch_num}.C: {title} — Key Concepts Visualised'
            story.extend(make_image_elem(chart_path, caption, max_w=5.8*inch))
            chart_placed = True
            last_img_ci = ci

        # ── Reference strip at ~3/5 (tbl2 slot — always ref_strip, no grid) ──
        if not tbl2_placed and ci >= tbl2_at and len(tables_2) > 1:
            t = tables_2[1]
            story.extend(make_ref_strip(
                t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
            tbl2_placed = True

        # ── Photo 2 at ~2/3 — respect min gap ────────────────────────────
        if (HAS_PIL and not photo_placed[1] and ci >= photo2_at
                and len(photos_2) > 1 and ci - last_img_ci >= min_img_gap):
            img = photos_2[1]
            story.extend(make_image_elem(img.get('path',''),
                                         img.get('caption', f'Figure {ch_num}.2')))
            photo_placed[1] = True
            last_img_ci = ci

        # ── Numbered process panel at ~4/5 ───────────────────────────────
        if not process_placed and ci >= process_at and proc_src:
            story.extend(make_process_panel(
                proc_src.get('caption', title),
                proc_src.get('headers', []),
                proc_src.get('rows', [])))
            process_placed = True

        # ── Case study: one every cs_every chunks ─────────────────────────
        cs_slot = (ci + 1) // cs_every - 1
        if css and (ci + 1) % cs_every == 0 and 0 <= cs_slot < len(css) \
                and cs_slot not in cs_placed:
            story.extend(make_case_study(
                css[cs_slot].get('title',''), css[cs_slot].get('body','')))
            cs_placed.add(cs_slot)

    # ── Flush anything not yet placed (very short chapters) ───────────────
    if not tbl1_placed and tables_2:
        t = tables_2[0]
        if _book_tables_used < MAX_BOOK_TABLES:
            try:
                story.extend(make_table_elem(t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
                _book_tables_used += 1
            except:
                story.extend(make_ref_strip(t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
        else:
            story.extend(make_ref_strip(t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
    if not callout_placed and kc:
        story.extend(make_callout_box(kc, max_items=4))
    if not tbl2_placed and len(tables_2) > 1:
        t = tables_2[1]
        story.extend(make_ref_strip(t.get('caption',''), t.get('headers',[]), t.get('rows',[])))
    if not process_placed and proc_src:
        story.extend(make_process_panel(
            proc_src.get('caption', title),
            proc_src.get('headers', []),
            proc_src.get('rows', [])))

    # ── Any remaining case studies ────────────────────────────────────────
    for ci2, cs in enumerate(css):
        if ci2 not in cs_placed:
            story.extend(make_case_study(cs.get('title',''), cs.get('body','')))

    # ── Chart / photos not yet placed (very short chapters) ───────────────
    if HAS_PIL and not photo_placed[0] and photos_2:
        story.extend(make_image_elem(photos_2[0].get('path',''),
                                     photos_2[0].get('caption','')))
    if HAS_PIL and not chart_placed and has_chart:
        story.extend(make_image_elem(chart_path,
            f'Figure {ch_num}.C: {title} — Key Concepts Visualised',
            max_w=5.8*inch))
    if HAS_PIL and not photo_placed[1] and len(photos_2) > 1:
        story.extend(make_image_elem(photos_2[1].get('path',''),
                                     photos_2[1].get('caption','')))

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

# ── Auto-sync to GitHub ───────────────────────────────────────────────────────
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
try:
    from sync_to_github import sync as _sync_gh
    _sync_gh()
except Exception as _e:
    print(f'\n⚠  GitHub sync skipped: {_e}')
