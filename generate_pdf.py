from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

W, H = letter
NAVY   = colors.HexColor("#1e3a5f")
LGRAY  = colors.HexColor("#f0f4ff")
MGRAY  = colors.HexColor("#b0b8c8")
BLACK  = colors.black
WHITE  = colors.white
DKGRAY = colors.HexColor("#404040")

OUT = "/home/user/INSURANCE/CGL_Application_CGIG.pdf"

def new_page(c, page_num):
    """Draw header and footer, return starting Y."""
    # Header
    c.setFillColor(NAVY)
    c.rect(0, H - 0.65*inch, W, 0.65*inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W/2, H - 0.35*inch, "COMMERCIAL GENERAL INSURANCE GROUP")
    # Footer
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.5)
    c.line(0.5*inch, 0.45*inch, W - 0.5*inch, 0.45*inch)
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(W/2, 0.28*inch, f"CGIG Confidential  |  500 Commerce Plaza, Hartford CT 06103  |  applications@cgig.com  |  Page {page_num}")
    return H - 0.9*inch

def section_bar(c, y, title, lm=0.5*inch, rw=W-inch):
    c.setFillColor(NAVY)
    c.rect(lm, y - 0.02*inch, rw, 0.22*inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(lm + 0.1*inch, y + 0.04*inch, title)
    return y - 0.32*inch

def field_line(c, y, label, lm=0.5*inch, lw=1.8*inch, rw=W-inch-1.8*inch):
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lm, y + 0.04*inch, label + ":")
    c.setStrokeColor(MGRAY)
    c.setLineWidth(0.5)
    c.line(lm + lw, y, lm + lw + rw, y)
    return y - 0.22*inch

def two_fields(c, y, l1, l2, lm=0.5*inch, half=3.6*inch):
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lm, y + 0.04*inch, l1 + ":")
    c.setStrokeColor(MGRAY)
    c.setLineWidth(0.5)
    c.line(lm + 1.5*inch, y, lm + half - 0.2*inch, y)
    x2 = lm + half
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x2, y + 0.04*inch, l2 + ":")
    c.line(x2 + 1.5*inch, y, W - 0.5*inch, y)
    return y - 0.22*inch

def checkbox_row(c, y, label, options, lm=0.5*inch):
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lm, y + 0.04*inch, label + ":")
    x = lm + 2.0*inch
    for opt in options:
        c.setStrokeColor(NAVY)
        c.setLineWidth(0.6)
        c.rect(x, y - 0.01*inch, 0.13*inch, 0.13*inch, fill=0, stroke=1)
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 8)
        c.drawString(x + 0.17*inch, y + 0.02*inch, opt)
        x += len(opt) * 0.072*inch + 0.35*inch
    return y - 0.23*inch

def blank_lines(c, y, n=3, lm=0.5*inch):
    c.setStrokeColor(MGRAY)
    c.setLineWidth(0.5)
    for _ in range(n):
        c.line(lm, y, W - 0.5*inch, y)
        y -= 0.22*inch
    return y

def notice_box(c, y, text, lm=0.5*inch):
    c.setFillColor(LGRAY)
    c.setStrokeColor(MGRAY)
    c.roundRect(lm, y - 0.55*inch, W - inch, 0.62*inch, 4, fill=1, stroke=1)
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica", 7.5)
    # wrap manually
    words = text.split()
    line = ""
    lines = []
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 7.5) < (W - inch - 0.2*inch):
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    ty = y - 0.12*inch
    for ln in lines:
        c.drawString(lm + 0.1*inch, ty, ln)
        ty -= 0.13*inch
    return y - 0.65*inch

# ─────────────────────────────────────────────────────────────────────────────
c = canvas.Canvas(OUT, pagesize=letter)
c.setTitle("CGIG — CGL Insurance Application")
lm = 0.5 * inch
sp = 0.1 * inch

# ═══ PAGE 1 ═══════════════════════════════════════════════════════════════
page = 1
y = new_page(c, page)

# Title block
c.setFillColor(LGRAY)
c.setStrokeColor(NAVY)
c.roundRect(lm, y - 0.55*inch, W - inch, 0.62*inch, 6, fill=1, stroke=1)
c.setFillColor(NAVY)
c.setFont("Helvetica-Bold", 12)
c.drawCentredString(W/2, y - 0.22*inch, "COMMERCIAL GENERAL LIABILITY (CGL) INSURANCE APPLICATION")
c.setFillColor(DKGRAY)
c.setFont("Helvetica", 8)
c.drawCentredString(W/2, y - 0.42*inch, "Fax completed form to 1-860-555-0199  ·  Email: applications@cgig.com  ·  Tel: 1-800-CGIG-NOW (244-4669)")
y -= 0.72*inch

# Section 1
y = section_bar(c, y, "SECTION 1 — APPLICANT / NAMED INSURED INFORMATION")
y = field_line(c, y, "Legal Business Name")
y = field_line(c, y, "DBA / Trade Name (if applicable)")
y = two_fields(c, y, "Business Phone", "Business Email")
y = field_line(c, y, "Mailing Address (Street, Suite)")
y = two_fields(c, y, "City", "State / ZIP")
y = two_fields(c, y, "Primary Contact Name", "Contact Title")
y = two_fields(c, y, "Direct Phone", "Date Business Established")
y = two_fields(c, y, "Federal EIN / Tax ID", "Years Under Current Ownership")
y = checkbox_row(c, y, "Entity Type", ["Sole Proprietor", "Partnership", "LLC", "S-Corp", "C-Corp", "Non-Profit"])
y -= sp

# Section 2
y = section_bar(c, y, "SECTION 2 — BUSINESS OPERATIONS")
y = field_line(c, y, "Full Description of Operations")
y = blank_lines(c, y, 2)
y = two_fields(c, y, "Primary NAICS / SIC Code", "Industry Classification")
y = two_fields(c, y, "Annual Gross Revenue ($)", "# Full-Time Employees")
y = two_fields(c, y, "# Part-Time Employees", "# Subcontractors Used / Year")
y = field_line(c, y, "Business Website URL")
y = checkbox_row(c, y, "Sell / Distribute Products?", ["Yes", "No"])
y = checkbox_row(c, y, "Work at Customer Locations?", ["Yes", "No"])
y = checkbox_row(c, y, "Operate in Multiple States?", ["Yes", "No"])
y = field_line(c, y, "States of Operation")
y -= sp

# Section 3
y = section_bar(c, y, "SECTION 3 — COVERAGE REQUESTED")
y = two_fields(c, y, "Desired Effective Date", "Desired Expiration Date")
c.setFillColor(NAVY)
c.setFont("Helvetica-Bold", 8)
c.drawString(lm, y + 0.04*inch, "Coverage Limits Requested:")
y -= 0.2*inch
y = two_fields(c, y, "Each Occurrence ($)", "General Aggregate ($)")
y = two_fields(c, y, "Products / Comp Ops Aggregate ($)", "Personal & Advertising Injury ($)")
y = two_fields(c, y, "Medical Expense — any one person ($)", "Damage to Rented Premises ($)")
y = two_fields(c, y, "Deductible ($)", "Self-Insured Retention ($)")
y = checkbox_row(c, y, "Additional Coverages", ["Umbrella/Excess", "EPLI", "Cyber Liability", "Hired/Non-Owned Auto"])
y = checkbox_row(c, y, "Additional Insureds Required?", ["Yes", "No"])
y = field_line(c, y, "If Yes — list Additional Insured names")

# ═══ PAGE 2 ═══════════════════════════════════════════════════════════════
c.showPage()
page += 1
y = new_page(c, page)

# Section 4
y = section_bar(c, y, "SECTION 4 — LOSS & CLAIMS HISTORY (Prior 5 Years)")
y = checkbox_row(c, y, "Any claims, losses, or incidents in past 5 years?", ["Yes", "No"])
c.setFillColor(DKGRAY)
c.setFont("Helvetica", 8)
c.drawString(lm, y + 0.04*inch, "If Yes, provide details for each claim below:")
y -= 0.22*inch

# Claims table
col_w = [0.9*inch, 2.1*inch, 1.0*inch, 1.0*inch, 1.0*inch]
headers = ["Date of Loss", "Description of Loss", "Amount Paid", "Amount Reserved", "Status"]
row_h = 0.22*inch
# header row
x = lm
c.setFillColor(NAVY)
c.setFont("Helvetica-Bold", 7.5)
for i, h in enumerate(headers):
    c.setFillColor(NAVY)
    c.rect(x, y - row_h, col_w[i], row_h, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.drawCentredString(x + col_w[i]/2, y - row_h + 0.06*inch, h)
    x += col_w[i]
y -= row_h
# data rows
c.setStrokeColor(MGRAY)
c.setLineWidth(0.4)
for _ in range(5):
    x = lm
    for w in col_w:
        c.rect(x, y - row_h, w, row_h, fill=0, stroke=1)
        x += w
    y -= row_h
y -= sp

y = checkbox_row(c, y, "Has any insurer cancelled or non-renewed your policy?", ["Yes", "No"])
y = field_line(c, y, "If Yes — reason and insurer name")
y = blank_lines(c, y, 2)
y -= sp

# Section 5
y = section_bar(c, y, "SECTION 5 — PRIOR / CURRENT INSURANCE")
y = field_line(c, y, "Current / Most Recent Insurance Company")
y = two_fields(c, y, "Policy Number", "Policy Expiration Date")
y = two_fields(c, y, "Each Occurrence Limit ($)", "Annual Premium Paid ($)")
y = field_line(c, y, "Reason for Seeking New / Different Coverage")
y -= sp

# Section 6
y = section_bar(c, y, "SECTION 6 — ADDITIONAL INFORMATION & REMARKS")
y = blank_lines(c, y, 5)
y -= sp

# Section 7 — Signature
y = section_bar(c, y, "SECTION 7 — APPLICANT DECLARATION & SIGNATURE")
disclaimer = ("The undersigned authorized representative of the applicant declares that, to the best of their knowledge and belief, "
              "the information provided in this application is true, accurate, and complete. The applicant understands that any "
              "misrepresentation, omission, or incorrect statement may result in rescission of any policy issued. Signing this "
              "application does not bind the company to issue a policy or the applicant to purchase coverage.")
y = notice_box(c, y, disclaimer)
y -= 0.05*inch
y = two_fields(c, y, "Authorized Signature", "Date Signed")
y = two_fields(c, y, "Printed Name", "Title / Position")
y -= sp

# Office Use Box
c.setFillColor(colors.HexColor("#f5f5f5"))
c.setStrokeColor(MGRAY)
box_h = 0.95*inch
c.roundRect(lm, y - box_h, W - inch, box_h, 4, fill=1, stroke=1)
c.setFillColor(NAVY)
c.setFont("Helvetica-Bold", 8)
c.drawString(lm + 0.1*inch, y - 0.15*inch, "FOR OFFICE USE ONLY")
y -= 0.3*inch
y = two_fields(c, y, "Policy Number Assigned", "Underwriter Name", lm + 0.1*inch)
y = two_fields(c, y, "Quote Date", "Annual Premium Quoted ($)", lm + 0.1*inch)
y = two_fields(c, y, "Application Status", "Producer / Agent Code", lm + 0.1*inch)

c.save()
print(f"PDF saved to: {OUT}")
