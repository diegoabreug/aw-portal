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

def arrow_down(c, x, y1, y2, color, w=2):
    c.saveState()
    c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(w)
    c.line(x, y1, x, y2+8)
    p = c.beginPath()
    p.moveTo(x,y2); p.lineTo(x-5,y2+10); p.lineTo(x+5,y2+10); p.close()
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
    ov(c, cx, cy-27, 19, 12, WHITE, BLACK, 1)
    cash = acc.get('balance', 0) * 0.02
    ct(c, f"${cash:,.0f}", cx, cy-31, font="Helvetica", size=6, color=BLACK)
    ct(c, "Cash", cx, cy-41, font="Helvetica", size=6, color=BLACK)

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

    draw_header(c, width, height,
                "Simple Automated Cashflow System (SACS)", client['name'], quarter)
    draw_footer(c, width)

    inflow_cx = width*0.22; outflow_cx = width*0.78
    reserve_cx = width*0.50; top_cy = height-230; reserve_cy = height-430; r=92

    ov(c, inflow_cx, top_cy, r, r, GREEN_MED, GREEN_DARK, 3)
    ct(c, "INFLOW", inflow_cx, top_cy+33, size=14, color=WHITE)
    ct(c, f"${sacs_data['inflow']:,.0f}", inflow_cx, top_cy+8,
       font="Helvetica-Bold", size=17, color=WHITE)
    ct(c, "per month", inflow_cx, top_cy-14, font="Helvetica", size=9, color=WHITE)
    ct(c, "$1,000 Floor", inflow_cx, top_cy-r-16,
       font="Helvetica", size=8, color=GRAY_DARK)

    ov(c, outflow_cx, top_cy, r, r, RED_DARK, HexColor('#800000'), 3)
    ct(c, "OUTFLOW", outflow_cx, top_cy+33, size=14, color=WHITE)
    ct(c, f"${sacs_data['outflow']:,.0f}", outflow_cx, top_cy+8,
       font="Helvetica-Bold", size=17, color=WHITE)
    ct(c, "per month", outflow_cx, top_cy-14, font="Helvetica", size=9, color=WHITE)
    ct(c, "$1,000 Floor", outflow_cx, top_cy-r-16,
       font="Helvetica", size=8, color=GRAY_DARK)

    ax1=inflow_cx+r+5; ax2=outflow_cx-r-5; ay=top_cy+10
    arrow_right(c, ax1, ay, ax2, RED_MED, 2.5)
    mx=(ax1+ax2)/2
    c.setFont("Helvetica-Bold",9); c.setFillColor(RED_MED)
    lb=f"X = ${sacs_data['outflow']:,.0f}/month"
    c.drawString(mx-c.stringWidth(lb,"Helvetica-Bold",9)/2, ay+8, lb)
    c.setFont("Helvetica",8); c.setFillColor(GRAY_DARK)
    sb="Automated transfer on the 28th"
    c.drawString(mx-c.stringWidth(sb,"Helvetica",8)/2, ay-6, sb)

    px1=outflow_cx; px2=reserve_cx
    py_top=top_cy-r-5; py_mid=(top_cy-r+reserve_cy+r)/2
    c.setStrokeColor(BLUE_MED); c.setLineWidth(2.5)
    c.line(px1,py_top,px1,py_mid); c.line(px1,py_mid,px2,py_mid)
    arrow_down(c, px2, py_mid, reserve_cy+r+5, BLUE_MED, 2.5)
    excess=sacs_data['excess']
    c.setFont("Helvetica-Bold",9); c.setFillColor(BLUE_MED)
    el=f"${excess:,.0f}/mo excess"
    c.drawString(px2+8, py_mid-14, el)

    ov(c, reserve_cx, reserve_cy, r, r, BLUE_MED, BLUE_DARK, 3)
    ct(c, "PRIVATE", reserve_cx, reserve_cy+30, size=13, color=WHITE)
    ct(c, "RESERVE", reserve_cx, reserve_cy+13, size=13, color=WHITE)
    ct(c, f"${excess:,.0f}", reserve_cx, reserve_cy-8,
       font="Helvetica-Bold", size=16, color=WHITE)
    ct(c, "monthly excess", reserve_cx, reserve_cy-26,
       font="Helvetica", size=8, color=WHITE)
    ml="MONTHLY CASHFLOW"
    c.setFont("Helvetica-Bold",11); c.setFillColor(GRAY_DARK)
    c.drawString(reserve_cx-c.stringWidth(ml,"Helvetica-Bold",11)/2,
                 reserve_cy-r-20, ml)

    c.showPage()

    # Page 2
    draw_header(c, width, height,
                "Simple Automated Cashflow System (SACS)", client['name'], quarter)
    draw_footer(c, width)
    c.setFont("Helvetica-Bold",12); c.setFillColor(GRAY_DARK)
    c.drawString(40, height-100, "Simple Automated Cashflow System (SACS)")
    c.setStrokeColor(GRAY_MED); c.setLineWidth(1); c.setDash(4,4)
    c.line(width/2, height-115, width/2, height-420); c.setDash()

    fcx=width*0.30; fcy=height-270; frx=108; fry=98
    icx=width*0.68; icy=height-265; irx=118; iry=108

    ov(c, fcx, fcy, frx, fry, BLUE_LIGHT, BLUE_MED, 2)
    ct(c, "FICA", fcx, fcy+28, size=13, color=BLUE_DARK)
    ct(c, "ACCOUNT", fcx, fcy+11, size=13, color=BLUE_DARK)
    c.setFillColor(WHITE); c.setStrokeColor(BLUE_MED); c.setLineWidth(1)
    c.rect(fcx-52, fcy-14, 104, 22, fill=1, stroke=1)
    ct(c, f"${private_reserve_balance:,.0f}", fcx, fcy-8,
       font="Helvetica-Bold", size=11, color=BLUE_DARK)
    ct(c, "6X Monthly Expenses + Deductibles", fcx, fcy-fry-16,
       font="Helvetica", size=8, color=GRAY_DARK)

    ov(c, icx, icy, irx, iry, BLUE_DARK, HexColor('#0F2D4A'), 2)
    ct(c, "INVESTMENT", icx, icy+30, size=13, color=WHITE)
    ct(c, "ACCOUNT", icx, icy+13, size=13, color=WHITE)
    c.setFillColor(WHITE); c.setStrokeColor(BLUE_LIGHT); c.setLineWidth(1)
    c.rect(icx-56, icy-13, 112, 22, fill=1, stroke=1)
    schwab = client.get('schwab_balance', 0) or 0
    il = f"${schwab:,.0f}+" if schwab > 0 else "Enter Balance"
    ct(c, il, icx, icy-6, font="Helvetica-Bold", size=11, color=BLUE_DARK)
    ct(c, "Remainder", icx, icy-iry-16, font="Helvetica", size=8, color=GRAY_DARK)

    ay3=fcy+5
    arrow_right(c, fcx+frx+5, ay3, icx-irx-5, BLUE_MED, 2)
    arrow_right(c, icx-irx-5, ay3-13, fcx+frx+5, BLUE_MED, 2)

    lt="LONG TERM  CASHFLOW"
    c.setFont("Helvetica-Bold",12); c.setFillColor(GRAY_DARK)
    c.drawString(width/2-c.stringWidth(lt,"Helvetica-Bold",12)/2, height-445, lt)
    s2="(Magnified Private Reserve Cashflow)"
    c.setFont("Helvetica",10); c.setFillColor(BLUE_MED)
    c.drawString(width/2-c.stringWidth(s2,"Helvetica",10)/2, height-460, s2)

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

    # ── Fixed Y rows for top zone ─────────────────────────────
    # Row heights ensure nothing overlaps
    GT_CY     = CT - 22          # Grand Total box
    CLIENT_CY = CT - 75          # Client ovals
    LIAB_CY   = CT - 125         # Liabilities summary
    MID_Y     = CT - 178         # Horizontal divider

    # Retirement zone (between MID_Y and ret bottom)
    RET_TOP   = MID_Y - 10
    RET_BOT   = MID_Y - 175
    RET_H     = RET_TOP - RET_BOT

    # Bottom zone
    BOT_TOP   = RET_BOT - 5
    BOT_BOT   = CB + 38
    BOT_H     = BOT_TOP - BOT_BOT

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

    # ── GRAND TOTAL BOX — always top center ──────────────────
    c.setFillColor(GRAY_DARK); c.setStrokeColor(BLACK); c.setLineWidth(1)
    c.rect(CX-62, GT_CY-14, 124, 28, fill=1, stroke=1)
    ct(c, "GRAND TOTAL", CX, GT_CY+6, size=9, color=WHITE)
    ct(c, f"${tcc_data['grand_total']:,.2f}", CX, GT_CY-8, size=9, color=WHITE)

    # ── LIABILITIES SUMMARY — always below grand total ────────
    c.setFillColor(GRAY_LIGHT); c.setStrokeColor(BLACK); c.setLineWidth(1)
    c.rect(CX-62, LIAB_CY-12, 124, 24, fill=1, stroke=1)
    ct(c, f"Liabilities: ${tcc_data['liabilities']:,.2f}",
       CX, LIAB_CY+4, font="Helvetica-Bold", size=8, color=BLACK)
    ct(c, f"a/o {date_str}", CX, LIAB_CY-8,
       font="Helvetica", size=7, color=BLACK)

    # ── CLIENT OVALS + RETIREMENT TOTAL BOXES ────────────────
    def client_oval(cx, cy, name, age, dob, ssn):
        ov(c, cx, cy, 50, 36, GREEN_MED, GREEN_DARK, 2)
        ct(c, name.split()[0], cx, cy+14, size=10, color=WHITE)
        ct(c, f"Age {age or ''}", cx, cy+2,
           font="Helvetica", size=8, color=WHITE)
        ct(c, f"DOB {dob or ''}", cx, cy-9,
           font="Helvetica", size=7, color=WHITE)
        ct(c, f"SSN ***{ssn or 'XXXX'}", cx, cy-20,
           font="Helvetica", size=7, color=WHITE)

    def ret_box(cx, cy, label, amount):
        c.setFillColor(GRAY_DARK); c.setStrokeColor(BLACK); c.setLineWidth(1)
        c.rect(cx-52, cy-14, 104, 28, fill=1, stroke=1)
        ct(c, label, cx, cy+7, size=7, color=WHITE)
        ct(c, f"${amount:,.2f}", cx, cy-6, size=8, color=WHITE)

    if has_partner:
        # COUPLE — ovals on left/right quarters, boxes on outer edges
        # Left quarter center: CX * 0.35 (far left of center)
        # Right quarter center: CX + (width-M-CX)*0.65 (far right of center)
        c1_oval_cx = CX * 0.35
        c2_oval_cx = CX + (width-M-CX) * 0.65
        c1_box_cx  = M + 58
        c2_box_cx  = width - M - 58

        client_oval(c1_oval_cx, CLIENT_CY,
                    client['name'], client.get('age'),
                    client.get('dob'), client.get('ssn_last4'))
        client_oval(c2_oval_cx, CLIENT_CY,
                    client['name_partner'], client.get('age_partner'),
                    client.get('dob_partner'), client.get('ssn_last4_partner'))
        ret_box(c1_box_cx, CLIENT_CY,
                "Client 1 Retirement Only", tcc_data['client1_retirement'])
        ret_box(c2_box_cx, CLIENT_CY,
                "Client 2 Retirement Only", tcc_data['client2_retirement'])
    else:
        # SINGLE — client oval in LEFT quadrant, ret box further left
        # Grand Total + Liabilities stay at center
        # Client oval at ~25% of width
        c1_oval_cx = width * 0.25
        ret_box_cx = M + 65

        client_oval(c1_oval_cx, CLIENT_CY,
                    client['name'], client.get('age'),
                    client.get('dob'), client.get('ssn_last4'))
        ret_box(ret_box_cx, CLIENT_CY,
                "Retirement Total", tcc_data['client1_retirement'])

    # ── RETIREMENT LABELS ─────────────────────────────────────
    c.setFont("Helvetica-Bold", 9); c.setFillColor(GREEN_MED)
    c.drawString(M+5, MID_Y+5, "RETIREMENT")
    rtw = c.stringWidth("RETIREMENT", "Helvetica-Bold", 9)
    c.drawString(width-M-rtw-5, MID_Y+5, "RETIREMENT")

    # ── RETIREMENT ACCOUNT OVALS ─────────────────────────────
    c1_ret = [a for a in tcc_data['retirement_accounts'] if a['owner']=='client1']
    c2_ret = [a for a in tcc_data['retirement_accounts'] if a['owner']!='client1']

    if has_partner:
        place_grid(c, c1_ret, CX/2, CX-M-15,
                   RET_TOP, RET_H, date_str)
        place_grid(c, c2_ret, CX+(width-M-CX)/2, width-M-CX-15,
                   RET_TOP, RET_H, date_str)
    else:
        all_ret = c1_ret + c2_ret
        place_grid(c, all_ret, CX, width-M*2-40,
                   RET_TOP, RET_H, date_str)

    # ── NON-RETIREMENT LABELS ─────────────────────────────────
    c.setFont("Helvetica-Bold", 9); c.setFillColor(BLACK)
    c.drawString(M+5, BOT_TOP-14, "NON")
    c.drawString(M+5, BOT_TOP-25, "RETIREMENT")
    nrtw = c.stringWidth("RETIREMENT", "Helvetica-Bold", 9)
    c.drawString(width-M-nrtw-5, BOT_TOP-14, "NON")
    c.drawString(width-M-nrtw-5, BOT_TOP-25, "RETIREMENT")

    # ── BOTTOM ZONE ───────────────────────────────────────────
    # Left col: non-ret left accounts
    # Center: Trust oval + Liabilities list
    # Right col: non-ret right accounts
    LEFT_CX = M + (CX-M)*0.28
    LEFT_W  = (CX-M)*0.50
    RIGHT_CX = width - M - (CX-M)*0.28
    RIGHT_W  = (CX-M)*0.50

    nr_all = tcc_data['non_retirement_accounts']
    if has_partner:
        nr_left  = [a for a in nr_all if a['owner'] in ('client1','joint')]
        nr_right = [a for a in nr_all if a['owner'] == 'client2']
        if not nr_right:
            half = max(1, len(nr_all)//2)
            nr_left = nr_all[:half]; nr_right = nr_all[half:]
    else:
        half = max(1, len(nr_all)//2)
        nr_left = nr_all[:half]; nr_right = nr_all[half:]

    NR_TOP = BOT_TOP - 30
    NR_H   = BOT_H - 55

    place_grid(c, nr_left,  LEFT_CX,  LEFT_W,  NR_TOP, NR_H, date_str, rx=60, ry=48)
    place_grid(c, nr_right, RIGHT_CX, RIGHT_W, NR_TOP, NR_H, date_str, rx=60, ry=48)

    # ── TRUST OVAL — fixed upper center of bottom zone ────────
    trust_accts = tcc_data['trust_accounts']
    trust_cy = BOT_TOP - BOT_H * 0.22

    if trust_accts:
        ov(c, CX, trust_cy, 76, 54, WHITE, BLACK, 1.5)
        n1 = client['name'].split()[0]
        if has_partner:
            n2 = client['name_partner'].split()[0]
            ct(c, f"{n1} and", CX, trust_cy+19,
               font="Helvetica", size=8, color=BLACK)
            ct(c, f"{n2} Family", CX, trust_cy+7,
               font="Helvetica", size=8, color=BLACK)
        else:
            ct(c, f"{n1}", CX, trust_cy+13,
               font="Helvetica", size=8, color=BLACK)
            ct(c, "Family", CX, trust_cy+1,
               font="Helvetica", size=8, color=BLACK)
        ct(c, "Trust", CX, trust_cy-11,
           font="Helvetica", size=8, color=BLACK)
        ct(c, f"${trust_accts[0]['balance']:,.0f}", CX, trust_cy-23,
           font="Helvetica-Bold", size=9, color=BLACK)
        ct(c, f"a/o {date_str}", CX, trust_cy-35,
           font="Helvetica", size=7, color=BLACK)

    # ── LIABILITIES LIST — fixed below trust ──────────────────
    liab_accts = tcc_data['liability_accounts']
    if liab_accts:
        ll_top = (trust_cy - 62) if trust_accts else (BOT_TOP - BOT_H*0.55)
        ll_w   = 168
        ll_h   = 13 + len(liab_accts)*13
        # ensure it doesn't go below NON RETIREMENT TOTAL
        min_y = CB + 42
        if ll_top - ll_h < min_y:
            ll_top = min_y + ll_h

        c.setFillColor(GRAY_LIGHT); c.setStrokeColor(BLACK); c.setLineWidth(1)
        c.rect(CX-ll_w/2, ll_top-ll_h, ll_w, ll_h+12, fill=1, stroke=1)
        ct(c, "Liabilities:", CX, ll_top+2,
           font="Helvetica-Bold", size=8, color=BLACK)
        for i, acc in enumerate(liab_accts):
            yp = ll_top - 10 - i*13
            c.setFont("Helvetica", 7); c.setFillColor(BLACK)
            nm = acc['account_type'][:14]
            bv = f"${acc['balance']:,.2f}"
            c.drawString(CX-ll_w/2+6, yp, nm)
            btw = c.stringWidth(bv, "Helvetica", 7)
            c.drawString(CX+ll_w/2-btw-6, yp, bv)

    # ── NON RETIREMENT TOTAL — always at very bottom ──────────
    nrt_cy = CB + 22
    c.setFillColor(GRAY_DARK); c.setStrokeColor(BLACK); c.setLineWidth(1)
    c.rect(CX-105, nrt_cy-11, 210, 22, fill=1, stroke=1)
    ct(c, f"NON RETIREMENT TOTAL   ${tcc_data['non_retirement']:,.2f}",
       CX, nrt_cy, font="Helvetica-Bold", size=9, color=WHITE)

    c.save(); buffer.seek(0)
    return buffer