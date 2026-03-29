"""
generate_pdf.py — Fillable CGL Application PDF
Generates an AcroForm (fillable) PDF using reportlab.
All text fields, checkboxes, and radio buttons are interactive form fields
that can be filled in and saved by the user.
"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

W, H = letter
NAVY   = colors.HexColor("#1e3a5f")
LGRAY  = colors.HexColor("#f0f4ff")
MGRAY  = colors.HexColor("#b0b8c8")
BLACK  = colors.black
WHITE  = colors.white
DKGRAY = colors.HexColor("#404040")

_field_counter = [0]


def _fid(prefix="f"):
    _field_counter[0] += 1
    return f"{prefix}_{_field_counter[0]}"


def new_page(c, page_num):
    """Draw page header and footer, return starting Y."""
    c.setFillColor(NAVY)
    c.rect(0, H - 0.65 * inch, W, 0.65 * inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(W / 2, H - 0.35 * inch, "COMMERCIAL GENERAL INSURANCE GROUP")
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.5)
    c.line(0.5 * inch, 0.45 * inch, W - 0.5 * inch, 0.45 * inch)
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Oblique", 7.5)
    c.drawCentredString(
        W / 2, 0.28 * inch,
        f"CGIG Confidential  |  500 Commerce Plaza, Hartford CT 06103  |  applications@cgig.com  |  Page {page_num}"
    )
    return H - 0.9 * inch


def section_bar(c, y, title, lm=0.5 * inch, rw=W - inch):
    c.setFillColor(NAVY)
    c.rect(lm, y - 0.02 * inch, rw, 0.22 * inch, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(lm + 0.1 * inch, y + 0.04 * inch, title)
    return y - 0.32 * inch


def field_line(c, y, label, lm=0.5 * inch, lw=1.8 * inch, rw=None, name=None):
    """Draw label and a single-line fillable text field."""
    if rw is None:
        rw = W - inch - lw
    fh = 0.17 * inch
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lm, y + 0.04 * inch, label + ":")
    c.acroForm.textfield(
        name=name or _fid("txt"),
        tooltip=label,
        x=lm + lw,
        y=y - fh + 0.02 * inch,
        width=rw,
        height=fh,
        borderStyle="underlined",
        borderColor=NAVY,
        fillColor=LGRAY,
        textColor=DKGRAY,
        fontSize=9,
        value="",
        forceBorder=True,
    )
    return y - 0.22 * inch


def two_fields(c, y, l1, l2, lm=0.5 * inch, half=3.6 * inch, n1=None, n2=None):
    """Draw two side-by-side fillable text fields."""
    fh = 0.17 * inch
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Bold", 8)

    # Field 1
    c.drawString(lm, y + 0.04 * inch, l1 + ":")
    w1 = half - 0.2 * inch - 1.5 * inch
    c.acroForm.textfield(
        name=n1 or _fid("txt"),
        tooltip=l1,
        x=lm + 1.5 * inch,
        y=y - fh + 0.02 * inch,
        width=w1,
        height=fh,
        borderStyle="underlined",
        borderColor=NAVY,
        fillColor=LGRAY,
        textColor=DKGRAY,
        fontSize=9,
        value="",
        forceBorder=True,
    )

    # Field 2
    x2 = lm + half
    c.drawString(x2, y + 0.04 * inch, l2 + ":")
    w2 = W - 0.5 * inch - x2 - 1.5 * inch
    c.acroForm.textfield(
        name=n2 or _fid("txt"),
        tooltip=l2,
        x=x2 + 1.5 * inch,
        y=y - fh + 0.02 * inch,
        width=w2,
        height=fh,
        borderStyle="underlined",
        borderColor=NAVY,
        fillColor=LGRAY,
        textColor=DKGRAY,
        fontSize=9,
        value="",
        forceBorder=True,
    )
    return y - 0.22 * inch


def checkbox_row(c, y, label, options, lm=0.5 * inch, prefix=None, radio=False):
    """
    Draw label with fillable checkbox (or radio) form fields.
    radio=True: mutually exclusive (radio group by same name).
    radio=False: independent checkboxes.
    """
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lm, y + 0.04 * inch, label + ":")

    x = lm + 2.0 * inch
    csize = 0.13 * inch
    group_name = prefix or _fid("radio")

    for i, opt in enumerate(options):
        if radio:
            c.acroForm.radio(
                name=group_name,
                tooltip=f"{label}: {opt}",
                value=opt,
                selected=False,
                x=x,
                y=y - 0.02 * inch,
                size=csize,
                buttonStyle="circle",
                borderColor=NAVY,
                fillColor=WHITE,
                textColor=NAVY,
                fieldFlags="noToggleToOff radio",
                forceBorder=True,
            )
        else:
            c.acroForm.checkbox(
                name=f"{group_name}_{i}",
                tooltip=f"{label}: {opt}",
                checked=False,
                x=x,
                y=y - 0.02 * inch,
                size=csize,
                buttonStyle="check",
                borderColor=NAVY,
                fillColor=WHITE,
                textColor=NAVY,
                forceBorder=True,
            )
        c.setFillColor(BLACK)
        c.setFont("Helvetica", 8)
        c.drawString(x + 0.17 * inch, y + 0.02 * inch, opt)
        x += len(opt) * 0.072 * inch + 0.35 * inch

    return y - 0.23 * inch


def text_area(c, y, n=3, lm=0.5 * inch, name=None):
    """Multi-line fillable text area."""
    area_h = n * 0.22 * inch
    c.acroForm.textfield(
        name=name or _fid("area"),
        tooltip="Enter text here",
        x=lm,
        y=y - area_h,
        width=W - inch,
        height=area_h,
        borderStyle="solid",
        borderColor=MGRAY,
        fillColor=LGRAY,
        textColor=DKGRAY,
        fontSize=9,
        fieldFlags="multiline",
        value="",
        forceBorder=True,
    )
    return y - area_h - 0.04 * inch


def notice_box(c, y, text, lm=0.5 * inch):
    c.setFillColor(LGRAY)
    c.setStrokeColor(MGRAY)
    c.roundRect(lm, y - 0.55 * inch, W - inch, 0.62 * inch, 4, fill=1, stroke=1)
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica", 7.5)
    words = text.split()
    line = ""
    lines = []
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, "Helvetica", 7.5) < (W - inch - 0.2 * inch):
            line = test
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    ty = y - 0.12 * inch
    for ln in lines:
        c.drawString(lm + 0.1 * inch, ty, ln)
        ty -= 0.13 * inch
    return y - 0.65 * inch


def build_pdf(output_path):
    """Build the fillable CGL application PDF and save to output_path."""
    _field_counter[0] = 0  # reset counter for repeatable field names

    c = canvas.Canvas(output_path, pagesize=letter)
    c.setTitle("CGIG — CGL Insurance Application (Fillable)")
    c.setAuthor("Commercial General Insurance Group")
    c.setSubject("Commercial General Liability Insurance Application")
    lm = 0.5 * inch
    sp = 0.1 * inch

    # ═══════════════════════════════════════════════════
    # PAGE 1
    # ═══════════════════════════════════════════════════
    y = new_page(c, 1)

    # Title block
    c.setFillColor(LGRAY)
    c.setStrokeColor(NAVY)
    c.roundRect(lm, y - 0.55 * inch, W - inch, 0.62 * inch, 6, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(W / 2, y - 0.22 * inch,
        "COMMERCIAL GENERAL LIABILITY (CGL) INSURANCE APPLICATION")
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, y - 0.42 * inch,
        "Fax completed form to 1-860-555-0199  ·  Email: applications@cgig.com  ·  Tel: 1-800-CGIG-NOW (244-4669)")
    y -= 0.72 * inch

    # ── Section 1: Applicant Info ──────────────────────
    y = section_bar(c, y, "SECTION 1 — APPLICANT / NAMED INSURED INFORMATION")
    y = field_line(c, y, "Legal Business Name", name="legal_business_name")
    y = field_line(c, y, "DBA / Trade Name (if applicable)", name="dba")
    y = two_fields(c, y, "Business Phone", "Business Email",
                   n1="business_phone", n2="business_email")
    y = field_line(c, y, "Mailing Address (Street, Suite)", name="mailing_address")
    y = two_fields(c, y, "City", "State / ZIP", n1="city", n2="state_zip")
    y = two_fields(c, y, "Primary Contact Name", "Contact Title",
                   n1="contact_name", n2="contact_title")
    y = two_fields(c, y, "Direct Phone", "Date Business Established",
                   n1="direct_phone", n2="date_established")
    y = two_fields(c, y, "Federal EIN / Tax ID", "Years Under Current Ownership",
                   n1="ein", n2="years_ownership")
    y = checkbox_row(c, y, "Entity Type",
                     ["Sole Proprietor", "Partnership", "LLC", "S-Corp", "C-Corp", "Non-Profit"],
                     prefix="entity_type", radio=True)
    y -= sp

    # ── Section 2: Business Operations ────────────────
    y = section_bar(c, y, "SECTION 2 — BUSINESS OPERATIONS")
    y = field_line(c, y, "Full Description of Operations", name="ops_line")
    y = text_area(c, y, n=2, name="ops_description")
    y = two_fields(c, y, "Primary NAICS / SIC Code", "Industry Classification",
                   n1="naics_code", n2="industry")
    y = two_fields(c, y, "Annual Gross Revenue ($)", "# Full-Time Employees",
                   n1="annual_revenue", n2="ft_employees")
    y = two_fields(c, y, "# Part-Time Employees", "# Subcontractors Used / Year",
                   n1="pt_employees", n2="subcontractors")
    y = field_line(c, y, "Business Website URL", name="website")
    y = checkbox_row(c, y, "Sell / Distribute Products?",
                     ["Yes", "No"], prefix="sell_products", radio=True)
    y = checkbox_row(c, y, "Work at Customer Locations?",
                     ["Yes", "No"], prefix="work_offsite", radio=True)
    y = checkbox_row(c, y, "Operate in Multiple States?",
                     ["Yes", "No"], prefix="multi_state", radio=True)
    y = field_line(c, y, "States of Operation", name="states_of_operation")
    y -= sp

    # ── Section 3: Coverage Requested ─────────────────
    y = section_bar(c, y, "SECTION 3 — COVERAGE REQUESTED")
    y = two_fields(c, y, "Desired Effective Date", "Desired Expiration Date",
                   n1="desired_eff_date", n2="desired_exp_date")
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lm, y + 0.04 * inch, "Coverage Limits Requested:")
    y -= 0.2 * inch
    y = two_fields(c, y, "Each Occurrence ($)", "General Aggregate ($)",
                   n1="per_occurrence", n2="aggregate")
    y = two_fields(c, y, "Products / Comp Ops Aggregate ($)", "Personal & Advertising Injury ($)",
                   n1="products_agg", n2="pers_adv_inj")
    y = two_fields(c, y, "Medical Expense — any one person ($)", "Damage to Rented Premises ($)",
                   n1="med_expense", n2="rented_premises")
    y = two_fields(c, y, "Deductible ($)", "Self-Insured Retention ($)",
                   n1="deductible", n2="sir")
    y = checkbox_row(c, y, "Additional Coverages",
                     ["Umbrella/Excess", "EPLI", "Cyber Liability", "Hired/Non-Owned Auto"],
                     prefix="add_coverage", radio=False)
    y = checkbox_row(c, y, "Additional Insureds Required?",
                     ["Yes", "No"], prefix="add_insured_req", radio=True)
    y = field_line(c, y, "If Yes — list Additional Insured names", name="add_insured_names")

    # ═══════════════════════════════════════════════════
    # PAGE 2
    # ═══════════════════════════════════════════════════
    c.showPage()
    y = new_page(c, 2)

    # ── Section 4: Claims History ──────────────────────
    y = section_bar(c, y, "SECTION 4 — LOSS & CLAIMS HISTORY (Prior 5 Years)")
    y = checkbox_row(c, y, "Any claims, losses, or incidents in past 5 years?",
                     ["Yes", "No"], prefix="has_claims", radio=True)
    c.setFillColor(DKGRAY)
    c.setFont("Helvetica", 8)
    c.drawString(lm, y + 0.04 * inch, "If Yes, provide details for each claim below:")
    y -= 0.22 * inch

    # Claims table with fillable cells
    col_widths = [0.9 * inch, 2.1 * inch, 1.0 * inch, 1.0 * inch, 1.0 * inch]
    headers = ["Date of Loss", "Description of Loss", "Amount Paid", "Amount Reserved", "Status"]
    row_h = 0.22 * inch

    # Header row
    x = lm
    for i, h in enumerate(headers):
        c.setFillColor(NAVY)
        c.rect(x, y - row_h, col_widths[i], row_h, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(x + col_widths[i] / 2, y - row_h + 0.06 * inch, h)
        x += col_widths[i]
    y -= row_h

    # Data rows — fillable cells
    for row_i in range(5):
        x = lm
        for col_i, cw in enumerate(col_widths):
            c.setStrokeColor(MGRAY)
            c.setLineWidth(0.4)
            c.rect(x, y - row_h, cw, row_h, fill=0, stroke=1)
            c.acroForm.textfield(
                name=f"claim_{row_i}_{col_i}",
                tooltip=f"{headers[col_i]} (claim {row_i + 1})",
                x=x + 0.02 * inch,
                y=y - row_h + 0.02 * inch,
                width=cw - 0.04 * inch,
                height=row_h - 0.04 * inch,
                borderStyle="solid",
                borderColor=colors.Color(0, 0, 0, 0),
                fillColor=LGRAY,
                textColor=DKGRAY,
                fontSize=7.5,
                value="",
                forceBorder=False,
            )
            x += cw
        y -= row_h
    y -= sp

    y = checkbox_row(c, y, "Has any insurer cancelled or non-renewed your policy?",
                     ["Yes", "No"], prefix="cancelled", radio=True)
    y = field_line(c, y, "If Yes — reason and insurer name", name="cancellation_reason")
    y = text_area(c, y, n=2, name="cancellation_detail")
    y -= sp

    # ── Section 5: Prior Insurance ─────────────────────
    y = section_bar(c, y, "SECTION 5 — PRIOR / CURRENT INSURANCE")
    y = field_line(c, y, "Current / Most Recent Insurance Company", name="current_insurer")
    y = two_fields(c, y, "Policy Number", "Policy Expiration Date",
                   n1="prior_policy_num", n2="prior_policy_exp")
    y = two_fields(c, y, "Each Occurrence Limit ($)", "Annual Premium Paid ($)",
                   n1="prior_occ_limit", n2="prior_premium")
    y = field_line(c, y, "Reason for Seeking New / Different Coverage", name="reason_seeking")
    y -= sp

    # ── Section 6: Additional Info ─────────────────────
    y = section_bar(c, y, "SECTION 6 — ADDITIONAL INFORMATION & REMARKS")
    y = text_area(c, y, n=5, name="additional_remarks")
    y -= sp

    # ── Section 7: Signature ───────────────────────────
    y = section_bar(c, y, "SECTION 7 — APPLICANT DECLARATION & SIGNATURE")
    disclaimer = (
        "The undersigned authorized representative of the applicant declares that, to the best of their "
        "knowledge and belief, the information provided in this application is true, accurate, and complete. "
        "The applicant understands that any misrepresentation, omission, or incorrect statement may result in "
        "rescission of any policy issued. Signing this application does not bind the company to issue a policy "
        "or the applicant to purchase coverage."
    )
    y = notice_box(c, y, disclaimer)
    y -= 0.05 * inch
    y = two_fields(c, y, "Authorized Signature", "Date Signed",
                   n1="signature", n2="date_signed")
    y = two_fields(c, y, "Printed Name", "Title / Position",
                   n1="printed_name", n2="title_position")
    y -= sp

    # Office Use Box
    c.setFillColor(colors.HexColor("#f5f5f5"))
    c.setStrokeColor(MGRAY)
    box_h = 0.95 * inch
    c.roundRect(lm, y - box_h, W - inch, box_h, 4, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(lm + 0.1 * inch, y - 0.15 * inch, "FOR OFFICE USE ONLY")
    y -= 0.3 * inch
    y = two_fields(c, y, "Policy Number Assigned", "Underwriter Name",
                   lm + 0.1 * inch, n1="office_policy_num", n2="office_underwriter")
    y = two_fields(c, y, "Quote Date", "Annual Premium Quoted ($)",
                   lm + 0.1 * inch, n1="office_quote_date", n2="office_premium")
    y = two_fields(c, y, "Application Status", "Producer / Agent Code",
                   lm + 0.1 * inch, n1="office_status", n2="office_agent_code")

    c.save()


if __name__ == "__main__":
    out = "/home/user/INSURANCE/CGL_Application_CGIG.pdf"
    build_pdf(out)
    print(f"Fillable PDF saved to: {out}")
