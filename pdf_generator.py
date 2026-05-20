from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
import io
from datetime import datetime

BLUE_DARK  = HexColor('#1F4E79')
BLUE_MED   = HexColor('#2E75B6')
BLUE_LIGHT = HexColor('#BDD7EE')
GREEN_DARK = HexColor('#375623')
GREEN_MED  = HexColor('#538135')
RED_DARK   = HexColor('#C00000')
RED_MED    = HexColor('#FF0000')
GRAY_DARK  = HexColor('#404040')
GRAY_MED   = HexColor('#808080')
GRAY_LIGHT = HexColor('#D9D9D9')
WHITE = white
BLACK = black

def ct(c, text, cx, cy, font="Helvetica-Bold", size=11, color=WHITE):
    c.setFont(font, size)
    c.setFillColor(color)
    w = c.stringWidth(text, font, size)
    c.drawString(cx - w/2, cy, text)

def ov(c, cx, cy, rx, ry, fill, stroke=None, sw=1.5):
    c.saveState()
    c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke); c.setLineWidth(sw)
    else:
        c.setStrokeColor(fill)
    c.ellipse(cx-rx, cy-ry, cx+rx, cy+ry, fill=1, stroke=1 if stroke else 0)
    c.restoreState()

def arrow_right(c, x1, y, x2, color, w=2):
    c.saveState()
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(w)
    c.line(x1, y, x2-8, y)
    p = c.beginPath()
    p.moveTo(x2,y); p.lineTo(x2-10,y+5); p.lineTo(x2-10,y-5); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def arrow_left(c, x1, y, x2, color, w=2):
    c.saveState()
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(w)
    c.line(x1, y, x2+8, y)
    p = c.beginPath()
    p.moveTo(x2,y); p.lineTo(x2+10,y+5); p.lineTo(x2+10,y-5); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def arrow_down(c, x, y1, y2, color, w=2):
    c.saveState()
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(w)
    c.line(x, y1, x, y2+8)
    p = c.beginPath()
    p.moveTo(x,y2); p.lineTo(x-5,y2+10); p.lineTo(x+5,y2+10); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def amount_box(c, text, cx, cy, text_color):
    c.setFont("Helvetica-Bold", 14)
    w = c.stringWidth(text, "Helvetica-Bold", 14)
    box_w = w + 20
    box_h = 24
    c.setFillColor(WHITE)
    c.rect(cx - box_w/2, cy - 6, box_w, box_h, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.drawString(cx - w/2, cy + 2, text)

def bent_arrow(c, x1, y1, x2, y2, color, w=2):
    c.saveState()
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(w)
    c.line(x1, y1, x1, y2)
    c.line(x1, y2, x2-8, y2)
    p = c.beginPath()
    p.moveTo(x2, y2); p.lineTo(x2-10, y2+5); p.lineTo(x2-10, y2-5); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def draw_header(c, width, height, title, client_name, quarter):
    c.setFillColor(BLUE_DARK)
    c.rect(0, height-70, width, 70, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 18); c.setFillColor(WHITE)
    c.drawString(40, height-35, title)
    c.setFont("Helvetica", 11); c.setFillColor(BLUE_LIGHT)
    c.drawString(40, height-52, "Windbrook Solutions  |  Financial Planning")
    c.setFont("Helvetica-Bold", 14); c.setFillColor(WHITE)
    tw = c.stringWidth(client_name, "Helvetica-Bold", 14)
    c.drawString(width-tw-40, height-38, client_name)
    c.setFont("Helvetica", 11); c.setFillColor(BLUE_LIGHT)
    tw2 = c.stringWidth(quarter, "Helvetica", 11)
    c.drawString(width-tw2-40, height-54, quarter)

def draw_footer(c, width):
    c.setFillColor(BLUE_DARK)
    c.rect(0, 0, width, 30, fill=1, stroke=0)
    c.setFont("Helvetica", 8); c.setFillColor(WHITE)
    c.drawString(40, 10, "Windbrook Solutions  |  Confidential  |  For Client Use Only")
    ds = datetime.now().strftime("%B %d, %Y")
    tw = c.stringWidth(ds, "Helvetica", 8)
    c.drawString(width-tw-40, 10, ds)

def acct_oval(c, cx, cy, acc, date_str, rx=63, ry=50):
    ov(c, cx, cy, rx, ry, WHITE, BLACK, 1.5)
    ct(c, "ACCT #", cx, cy+28, font="Helvetica", size=7, color=BLACK)
    ct(c, acc['account_type'], cx, cy+16, font="Helvetica-Bold", size=9, color=BLACK)
    ct(c, f"${acc['balance']:,.2f}", cx, cy+3,
       font="Helvetica-Bold", size=9, color=BLACK)
    ct(c, f"a/o {date_str}", cx, cy-10, font="Helvetica", size=7, color=BLACK)
    
    ov(c, cx, cy-30, 20, 13, WHITE, BLACK, 1)
    cash = acc.get('balance', 0) * 0.02
    ct(c, f"${cash:,.0f}", cx, cy-28, font="Helvetica", size=6, color=BLACK)
    ct(c, "Cash", cx, cy-36, font="Helvetica", size=6, color=BLACK)

def place_grid(c, accounts, zone_cx, zone_w, zone_top, zone_h,
               date_str, rx=63, ry=50):
    n = len(accounts)
    if n == 0: return
    max_per_row = max(1, int(zone_w / (rx*2 + 25)))
    rows = [accounts[i:i+max_per_row] for i in range(0, n, max_per_row)]
    rh = zone_h / len(rows)
    for ri, row in enumerate(rows):
        rn = len(row)
        sp = min(zone_w / (rn+1), rx*2+30)
        sx = zone_cx - sp*(rn-1)/2
        cy = zone_top - rh*ri - rh/2
        for ai, acc in enumerate(row):
            acct_oval(c, sx + sp*ai, cy, acc, date_str, rx, ry)


# ── SACS ─────────────────────────────────────────────────────

def generate_sacs_pdf(client, sacs_data, private_reserve_balance):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    quarter = f"Q{(datetime.now().month-1)//3+1} {datetime.now().year}"

    draw_header(c, width, height, "Simple Automated Cashflow System (SACS)", client['name'], quarter)
    draw_footer(c, width)

    CX = width / 2
    r = 60
    y1 = 450
    y2 = 300
    y3 = 130

    inflow_cx = CX - 180
    outflow_cx = CX + 180
    reserve_cx = CX
    fica_cx = CX - 160
    inv_cx = CX + 160

    # Green Entrance Arrow
    c.saveState()
    c.setStrokeColor(GREEN_MED); c.setFillColor(GREEN_MED); c.setLineWidth(3)
    c.line(inflow_cx - 60, y1 + 50, inflow_cx - 45, y1 + 35)
    p = c.beginPath()
    p.moveTo(inflow_cx - 40, y1 + 30); p.lineTo(inflow_cx - 35, y1 + 45); p.lineTo(inflow_cx - 50, y1 + 40); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()
    c.setFont("Helvetica-Bold", 16); c.setFillColor(GREEN_MED)
    c.drawString(inflow_cx - 80, y1 + 60, "$")

    # INFLOW
    ov(c, inflow_cx, y1, r, r, GREEN_MED, GREEN_DARK, 2)
    ct(c, "INFLOW", inflow_cx, y1 + 25, size=13, color=WHITE)
    amount_box(c, f"${sacs_data['inflow']:,.0f}", inflow_cx, y1 - 5, GREEN_MED)
    ct(c, "$1,000 Floor", inflow_cx, y1 - 35, font="Helvetica", size=8, color=WHITE)

    # OUTFLOW
    ov(c, outflow_cx, y1, r, r, RED_DARK, HexColor('#800000'), 2)
    ct(c, "OUTFLOW", outflow_cx, y1 + 25, size=13, color=WHITE)
    amount_box(c, f"${sacs_data['outflow']:,.0f}", outflow_cx, y1 - 5, RED_DARK)
    ct(c, "$1,000 Floor", outflow_cx, y1 - 35, font="Helvetica", size=8, color=WHITE)

    # RED ARROW (Inflow -> Outflow)
    ax1 = inflow_cx + r + 5
    ax2 = outflow_cx - r - 5
    arrow_right(c, ax1, y1, ax2, RED_MED, 3)
    c.setFont("Helvetica-Bold", 10); c.setFillColor(RED_MED)
    red_text = f"x = ${sacs_data['outflow']:,.0f}/month*"
    c.drawString(CX - c.stringWidth(red_text, "Helvetica-Bold", 10)/2, y1 + 8, red_text)
    c.setFont("Helvetica-Bold", 7); c.setFillColor(BLACK)
    black_text = "Automated transfer on the 28th"
    c.drawString(CX - c.stringWidth(black_text, "Helvetica-Bold", 7)/2, y1 - 12, black_text)

    # Bent Blue Arrow (Inflow -> Reserve)
    bx1 = inflow_cx
    by1 = y1 - r - 5
    bx2 = reserve_cx - r - 5
    by2 = y2
    bent_arrow(c, bx1, by1, bx2, by2, BLUE_MED, 3)
    c.setFont("Helvetica-Bold", 10); c.setFillColor(BLUE_MED)
    c.drawString(inflow_cx + 15, y2 - 15, f"${sacs_data['excess']:,.0f}/mo*")

    # PRIVATE RESERVE
    ov(c, reserve_cx, y2, r, r, BLUE_MED, BLUE_DARK, 2)
    ct(c, "PRIVATE", reserve_cx, y2 + 25, size=13, color=WHITE)
    ct(c, "RESERVE", reserve_cx, y2 + 10, size=13, color=WHITE)
    amount_box(c, f"${sacs_data['excess']:,.0f}", reserve_cx, y2 - 15, BLUE_MED)

    # Vertical Dotted Line
    c.saveState()
    c.setStrokeColor(BLACK); c.setLineWidth(2.5); c.setDash(5, 5)
    c.line(CX, 235, CX, 225) # Upper section
    c.line(CX, 195, CX, 142) # Lower section: descends to y = 142.
    c.restoreState()
    
    c.setFont("Helvetica-Bold", 10); c.setFillColor(BLACK)
    ct(c, "Monthly Cashflow", CX, 215, font="Helvetica-Bold", size=10, color=BLACK)
    ct(c, "Simple Automated Cashflow System (SACS)", CX, 203, font="Helvetica-Bold", size=10, color=BLACK)

    # FICA ACCOUNT
    ov(c, fica_cx, y3, r, r, BLUE_LIGHT, BLUE_MED, 2)
    ct(c, "FICA", fica_cx, y3 + 25, size=13, color=WHITE)
    ct(c, "ACCOUNT", fica_cx, y3 + 10, size=13, color=WHITE)
    amount_box(c, f"${private_reserve_balance:,.0f}", fica_cx, y3 - 15, BLUE_MED)
    ct(c, "X6 Monthly Expenses + Deductibles", fica_cx, y3 - r - 15, font="Helvetica-Bold", size=8, color=BLACK)

    # INVESTMENT ACCOUNT
    ov(c, inv_cx, y3, r, r, BLUE_DARK, HexColor('#0F2D4A'), 2)
    ct(c, "INVESTMENT", inv_cx, y3 + 25, size=13, color=WHITE)
    ct(c, "ACCOUNT", inv_cx, y3 + 10, size=13, color=WHITE)
    
    investment_bal = client.get('investment_balance', 0) or 0
    il = f"${investment_bal:,.0f}+" if investment_bal > 0 else "Enter Balance"
    
    amount_box(c, il, inv_cx, y3 - 15, BLUE_DARK)
    ct(c, "Remainder", inv_cx, y3 - r - 15, font="Helvetica-Bold", size=8, color=BLACK)

    # SEPARATE ARROWS (FICA <-> Investment)
    # 1. Arrow from FICA to Investment (Up, pointing to the right)
    arrow_right(c, fica_cx + r + 15, y3 + 12, inv_cx - r - 15, BLUE_MED, 2.5)
    
    # 2. Arrow from Investment to FICA (Down, pointing left using new function)
    arrow_left(c, inv_cx - r - 15, y3 - 12, fica_cx + r + 15, BLUE_MED, 2.5)

    # Bottom Text
    ct(c, "LONG TERM CASHFLOW", CX, 60, font="Helvetica-Bold", size=11, color=BLACK)
    ct(c, "(Magnifies Private Reserve Cashflow)", CX, 45, font="Helvetica-Bold", size=10, color=BLUE_MED)

    c.save(); buffer.seek(0)
    return buffer


# ── TCC ──────────────────────────────────────────────────────

def generate_tcc_pdf(client, tcc_data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)
    quarter  = f"Q{(datetime.now().month-1)//3+1} {datetime.now().year}"
    date_str = datetime.now().strftime("%m/%d/%Y")
    has_partner = bool(client.get('has_partner') and client.get('name_partner'))

    draw_header(c, width, height, "Total Client Chart (TCC)",
                client['name'], quarter)
    draw_footer(c, width)

    M  = 28
    CT = height - 75
    CB = 35
    CX = width / 2
    MID_Y = CT - 210  

    # ── BACKGROUND LINES FIRST ───────────────────────────────
    c.setStrokeColor(GREEN_MED); c.setLineWidth(2.5)
    c.rect(M, CB, width-M*2, CT-CB, fill=0, stroke=1)
    c.line(M, MID_Y, width-M, MID_Y)
    if has_partner:
        c.line(CX, CT, CX, CB)

    # ── NAME / DATE ──────────────────────────────────────────
    c.setFont("Helvetica", 8); c.setFillColor(BLACK)
    c.drawString(M+6, CT-13, f"NAME: {client['name']}")
    c.drawString(M+6, CT-24, f"DATE: {date_str}")

    # ── TOP ZONE (GRAND TOTAL & LIABILITIES SUMMARY) ─────────
    GT_CY = CT - 20
    LIAB_CY = CT - 60

    c.setFillColor(GRAY_DARK); c.setStrokeColor(BLACK); c.setLineWidth(1)
    c.rect(CX-62, GT_CY-14, 124, 28, fill=1, stroke=1)
    ct(c, "GRAND TOTAL", CX, GT_CY+6, size=9, color=WHITE)
    ct(c, f"${tcc_data['grand_total']:,.2f}", CX, GT_CY-8, size=9, color=WHITE)

    c.setFillColor(GRAY_LIGHT); c.setStrokeColor(BLACK); c.setLineWidth(1)
    c.rect(CX-62, LIAB_CY-12, 124, 24, fill=1, stroke=1)
    ct(c, f"Liabilities: ${tcc_data['liabilities']:,.2f}",
       CX, LIAB_CY+4, font="Helvetica-Bold", size=8, color=BLACK)
    ct(c, f"a/o {date_str}", CX, LIAB_CY-8, font="Helvetica", size=7, color=BLACK)

    # ── TOP ZONE (CLIENT OVALS & RETIREMENT TOTALS) ──────────
    CLIENT_CY = CT - 60

    def client_oval(cx, cy, name, age, dob, ssn):
        ov(c, cx, cy, 50, 36, GREEN_MED, GREEN_DARK, 2)
        ct(c, name.split()[0], cx, cy+14, size=10, color=WHITE)
        ct(c, f"Age {age or ''}", cx, cy+2, font="Helvetica", size=8, color=WHITE)
        ct(c, f"DOB {dob or ''}", cx, cy-9, font="Helvetica", size=7, color=WHITE)
        ct(c, f"SSN ***{ssn or 'XXXX'}", cx, cy-20, font="Helvetica", size=7, color=WHITE)

    def ret_box(cx, cy, label, amount):
        c.setFillColor(GRAY_DARK); c.setStrokeColor(BLACK); c.setLineWidth(1)
        c.rect(cx-52, cy-14, 104, 28, fill=1, stroke=1)
        ct(c, label, cx, cy+7, size=7, color=WHITE)
        ct(c, f"${amount:,.2f}", cx, cy-6, size=8, color=WHITE)

    if has_partner:
        c1_oval_cx = CX - 130
        c2_oval_cx = CX + 130
        c1_box_cx  = M + 65
        c2_box_cx  = width - M - 65

        client_oval(c1_oval_cx, CLIENT_CY, client['name'], client.get('age'), client.get('dob'), client.get('ssn_last4'))
        client_oval(c2_oval_cx, CLIENT_CY, client['name_partner'], client.get('age_partner'), client.get('dob_partner'), client.get('ssn_last4_partner'))
        ret_box(c1_box_cx, CLIENT_CY, "Client 1 Retirement Only", tcc_data['client1_retirement'])
        ret_box(c2_box_cx, CLIENT_CY, "Client 2 Retirement Only", tcc_data['client2_retirement'])
    else:
        c1_oval_cx = CX - 130
        ret_box_cx = M + 65

        client_oval(c1_oval_cx, CLIENT_CY, client['name'], client.get('age'), client.get('dob'), client.get('ssn_last4'))
        ret_box(ret_box_cx, CLIENT_CY, "Retirement Total", tcc_data['client1_retirement'])

    # ── MIDDLE ZONE (RETIREMENT ACCOUNTS) ────────────────────
    c.setFont("Helvetica-Bold", 9); c.setFillColor(GREEN_MED)
    c.drawString(M+5, MID_Y+5, "RETIREMENT")
    rtw = c.stringWidth("RETIREMENT", "Helvetica-Bold", 9)
    c.drawString(width-M-rtw-5, MID_Y+5, "RETIREMENT")

    RET_TOP = CT - 110
    RET_H   = 90

    c1_ret = [a for a in tcc_data['retirement_accounts'] if a['owner']=='client1']
    c2_ret = [a for a in tcc_data['retirement_accounts'] if a['owner']!='client1']

    if has_partner:
        place_grid(c, c1_ret, CX/2, CX-M-15, RET_TOP, RET_H, date_str, rx=55, ry=42)
        place_grid(c, c2_ret, CX+(width-M-CX)/2, width-M-CX-15, RET_TOP, RET_H, date_str, rx=55, ry=42)
    else:
        all_ret = c1_ret + c2_ret
        place_grid(c, all_ret, CX, width-M*2-40, RET_TOP, RET_H, date_str, rx=55, ry=42)

    # ── BOTTOM ZONE (NON-RETIREMENT LABELS) ──────────────────
    c.setFont("Helvetica-Bold", 9); c.setFillColor(BLACK)
    c.drawString(M+5, MID_Y-12, "NON")
    c.drawString(M+5, MID_Y-22, "RETIREMENT")
    nrtw = c.stringWidth("RETIREMENT", "Helvetica-Bold", 9)
    c.drawString(width-M-nrtw-5, MID_Y-12, "NON")
    c.drawString(width-M-nrtw-5, MID_Y-22, "RETIREMENT")

    # ── BOTTOM ZONE (NON-RETIREMENT ACCOUNTS) ────────────────
    NR_TOP = MID_Y - 50
    NR_H   = MID_Y - CB - 70

    LEFT_CX = M + (CX-M)*0.28
    LEFT_W  = (CX-M)*0.50
    RIGHT_CX = width - M - (CX-M)*0.28
    RIGHT_W  = (CX-M)*0.50

    nr_all = tcc_data['non_retirement_accounts']
    if has_partner:
        nr_left  = [a for a in nr_all if a['owner'] in ('client1','joint')]
        nr_right = [a for a in nr_all if a['owner'] == 'client2']
        if not nr_right and len(nr_left) > 2:
            half = max(1, len(nr_all)//2)
            nr_left = nr_all[:half]; nr_right = nr_all[half:]
    else:
        half = max(1, len(nr_all)//2)
        nr_left = nr_all[:half]; nr_right = nr_all[half:]

    place_grid(c, nr_left,  LEFT_CX,  LEFT_W,  NR_TOP, NR_H, date_str, rx=55, ry=42)
    place_grid(c, nr_right, RIGHT_CX, RIGHT_W, NR_TOP, NR_H, date_str, rx=55, ry=42)

    # ── BOTTOM ZONE (TRUST OVAL & LIABILITIES) ───────────────
    trust_accts = tcc_data['trust_accounts']
    trust_cy = MID_Y - 60

    if trust_accts:
        ov(c, CX, trust_cy, 70, 48, WHITE, BLACK, 1.5)
        n1 = client['name'].split()[0]
        if has_partner:
            n2 = client['name_partner'].split()[0]
            ct(c, f"{n1} and {n2} Family", CX, trust_cy+12, font="Helvetica", size=7, color=BLACK)
        else:
            ct(c, f"{n1} Family", CX, trust_cy+12, font="Helvetica", size=7, color=BLACK)
        ct(c, "Trust", CX, trust_cy+2, font="Helvetica", size=7, color=BLACK)
        ct(c, f"${trust_accts[0]['balance']:,.0f}", CX, trust_cy-10, font="Helvetica-Bold", size=9, color=BLACK)
        ct(c, f"a/o {date_str}", CX, trust_cy-22, font="Helvetica", size=6, color=BLACK)

    liab_accts = tcc_data['liability_accounts']
    if liab_accts:
        ll_w   = 168
        row_h  = 13
        ll_h   = 13 + len(liab_accts) * row_h
        
        available_top = (trust_cy - 50) if trust_accts else (MID_Y - 40)
        available_bottom = CB + 35 
        
        max_allowed_h = available_top - available_bottom - 10
        if ll_h + 12 > max_allowed_h:
            available_space = max_allowed_h - 25
            row_h = max(8, available_space / max(1, len(liab_accts)))
            ll_h = 13 + len(liab_accts) * row_h
            
        available_center_y = (available_top + available_bottom) / 2
        ll_top = available_center_y + (ll_h / 2) - 6

        c.setFillColor(GRAY_LIGHT); c.setStrokeColor(BLACK); c.setLineWidth(1)
        c.rect(CX-ll_w/2, ll_top-ll_h, ll_w, ll_h+12, fill=1, stroke=1)
        ct(c, "Liabilities:", CX, ll_top+2, font="Helvetica-Bold", size=8, color=BLACK)
        
        for i, acc in enumerate(liab_accts):
            yp = ll_top - 10 - i * row_h
            c.setFont("Helvetica", 7); c.setFillColor(BLACK)
            nm = acc['account_type'][:14]
            bv = f"${acc['balance']:,.2f}"
            c.drawString(CX-ll_w/2+6, yp, nm)
            btw = c.stringWidth(bv, "Helvetica", 7)
            c.drawString(CX+ll_w/2-btw-6, yp, bv)

    # ── NON RETIREMENT TOTAL ─────────────────────────────────
    nrt_cy = CB + 22
    c.setFillColor(GRAY_DARK); c.setStrokeColor(BLACK); c.setLineWidth(1)
    c.rect(CX-105, nrt_cy-11, 210, 22, fill=1, stroke=1)
    ct(c, f"NON RETIREMENT TOTAL   ${tcc_data['non_retirement']:,.2f}",
       CX, nrt_cy, font="Helvetica-Bold", size=9, color=WHITE)

    c.save(); buffer.seek(0)
    return buffer