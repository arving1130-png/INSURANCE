"""
db.py — SQLite database layer for CGIG Policy Management
"""
import sqlite3
import json
import os
from datetime import date, datetime, timedelta
import random
import string

DB_PATH = os.path.join(os.path.dirname(__file__), "insurance.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS policies (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_number    TEXT UNIQUE NOT NULL,
        insured_name     TEXT NOT NULL,
        dba              TEXT,
        policy_type      TEXT NOT NULL,
        status           TEXT NOT NULL DEFAULT 'Quote',
        effective_date   TEXT,
        expiration_date  TEXT,
        quote_date       TEXT,
        bound_date       TEXT,
        premium          REAL DEFAULT 0,
        commission_rate  REAL DEFAULT 10,
        deductible       TEXT DEFAULT 'None',
        per_occurrence   TEXT,
        aggregate        TEXT,
        products_agg     TEXT,
        agent_name       TEXT,
        underwriter      TEXT,
        contact_name     TEXT,
        contact_email    TEXT,
        contact_phone    TEXT,
        street           TEXT,
        city             TEXT,
        state            TEXT,
        zip              TEXT,
        entity_type      TEXT,
        industry         TEXT,
        employees        INTEGER DEFAULT 0,
        annual_revenue   TEXT,
        notes            TEXT DEFAULT '',
        extra_data       TEXT DEFAULT '{}',
        created_at       TEXT DEFAULT (datetime('now')),
        updated_at       TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        title            TEXT NOT NULL,
        description      TEXT DEFAULT '',
        task_type        TEXT DEFAULT 'General',
        due_date         TEXT,
        priority         TEXT DEFAULT 'Medium',
        status           TEXT DEFAULT 'Pending',
        policy_id        INTEGER REFERENCES policies(id) ON DELETE SET NULL,
        assigned_to      TEXT DEFAULT 'Unassigned',
        created_at       TEXT DEFAULT (datetime('now')),
        completed_at     TEXT
    );

    CREATE TABLE IF NOT EXISTS policy_templates (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        name             TEXT NOT NULL,
        policy_type      TEXT NOT NULL,
        description      TEXT DEFAULT '',
        defaults         TEXT DEFAULT '{}',
        created_at       TEXT DEFAULT (datetime('now')),
        updated_at       TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS ai_reviews (
        id               INTEGER PRIMARY KEY AUTOINCREMENT,
        policy_id        INTEGER NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
        created_at       TEXT DEFAULT (datetime('now')),
        issues_count     INTEGER DEFAULT 0,
        severity         TEXT DEFAULT 'low',
        ai_response      TEXT DEFAULT '',
        corrections      TEXT DEFAULT '[]'
    );
    """)

    # Seed only if empty
    row = c.execute("SELECT COUNT(*) FROM policies").fetchone()
    if row[0] == 0:
        _seed(c)

    conn.commit()
    conn.close()


def _seed(c):
    today = date.today()

    templates = [
        ("CGL Standard — Small Business", "CGL", "General liability for retail, offices, and service businesses under $2M revenue.",
         json.dumps({"per_occurrence": "$1,000,000", "aggregate": "$2,000,000", "products_agg": "$2,000,000",
                     "deductible": "None", "commission_rate": 12})),
        ("CGL Contractor", "CGL", "Coverage for general and specialty contractors with completed operations.",
         json.dumps({"per_occurrence": "$1,000,000", "aggregate": "$2,000,000", "products_agg": "$2,000,000",
                     "deductible": "$1,000", "commission_rate": 10})),
        ("CGL Restaurant & Hospitality", "CGL", "Includes liquor liability endorsement for food service and bar operations.",
         json.dumps({"per_occurrence": "$1,000,000", "aggregate": "$2,000,000", "products_agg": "$2,000,000",
                     "deductible": "None", "commission_rate": 11})),
        ("CGL Professional Services", "CGL", "Technology, consulting, and professional service firms.",
         json.dumps({"per_occurrence": "$1,000,000", "aggregate": "$2,000,000", "products_agg": "$1,000,000",
                     "deductible": "$500", "commission_rate": 12})),
        ("Commercial Property — Building", "Property", "Building and business personal property with business interruption.",
         json.dumps({"deductible": "$2,500", "commission_rate": 10})),
        ("Workers Compensation", "WC", "Statutory workers comp with employer's liability.",
         json.dumps({"deductible": "None", "commission_rate": 8})),
        ("Business Owner Policy (BOP)", "BOP", "Combined CGL + Property for small to mid-size businesses.",
         json.dumps({"per_occurrence": "$1,000,000", "aggregate": "$2,000,000", "deductible": "$500", "commission_rate": 11})),
    ]
    c.executemany(
        "INSERT INTO policy_templates (name, policy_type, description, defaults) VALUES (?,?,?,?)",
        templates
    )

    policies = [
        {
            "policy_number": "CGIG-CGL-2024-0001",
            "insured_name": "Riverside Construction LLC",
            "dba": "",
            "policy_type": "CGL",
            "status": "Active",
            "effective_date": str(today - timedelta(days=120)),
            "expiration_date": str(today + timedelta(days=245)),
            "quote_date": str(today - timedelta(days=135)),
            "bound_date": str(today - timedelta(days=121)),
            "premium": 4800.00,
            "commission_rate": 10.0,
            "deductible": "$1,000",
            "per_occurrence": "$1,000,000",
            "aggregate": "$2,000,000",
            "products_agg": "$2,000,000",
            "agent_name": "Sarah Mitchell",
            "underwriter": "James Harmon",
            "contact_name": "Mike Rivera",
            "contact_email": "mike@riversideconstruction.com",
            "contact_phone": "(860) 555-0112",
            "street": "45 Industrial Blvd",
            "city": "Hartford",
            "state": "CT",
            "zip": "06103",
            "entity_type": "LLC",
            "industry": "General Contractor",
            "employees": 18,
            "annual_revenue": "$1,000,001 – $2,500,000",
            "notes": "Strong renewal candidate. No claims in 3 years.",
            "extra_data": json.dumps({"uses_vehicles": "Yes", "work_offsite": "Yes", "hazmat": "No"}),
        },
        {
            "policy_number": "CGIG-CGL-2024-0002",
            "insured_name": "Main Street Diner Inc.",
            "dba": "Mama Rosa's Kitchen",
            "policy_type": "CGL",
            "status": "Active",
            "effective_date": str(today - timedelta(days=60)),
            "expiration_date": str(today + timedelta(days=305)),
            "quote_date": str(today - timedelta(days=75)),
            "bound_date": str(today - timedelta(days=61)),
            "premium": 3200.00,
            "commission_rate": 11.0,
            "deductible": "None",
            "per_occurrence": "$1,000,000",
            "aggregate": "$2,000,000",
            "products_agg": "$2,000,000",
            "agent_name": "David Chen",
            "underwriter": "Lisa Park",
            "contact_name": "Rosa Delgado",
            "contact_email": "rosa@mamarosas.com",
            "contact_phone": "(860) 555-0247",
            "street": "88 Main Street",
            "city": "New Haven",
            "state": "CT",
            "zip": "06510",
            "entity_type": "S-Corporation",
            "industry": "Restaurant / Food Service",
            "employees": 12,
            "annual_revenue": "$250,001 – $500,000",
            "notes": "Liquor liability endorsement included. Slip-and-fall claim filed 2022, closed $8,500.",
            "extra_data": json.dumps({"liquor_liability": "Yes", "sells_products": "Yes", "hazmat": "No"}),
        },
        {
            "policy_number": "CGIG-CGL-2024-0003",
            "insured_name": "TechForward Consulting Group",
            "dba": "",
            "policy_type": "CGL",
            "status": "Pending Renewal",
            "effective_date": str(today - timedelta(days=340)),
            "expiration_date": str(today + timedelta(days=25)),
            "quote_date": str(today - timedelta(days=355)),
            "bound_date": str(today - timedelta(days=341)),
            "premium": 2100.00,
            "commission_rate": 12.0,
            "deductible": "$500",
            "per_occurrence": "$1,000,000",
            "aggregate": "$2,000,000",
            "products_agg": "$1,000,000",
            "agent_name": "Sarah Mitchell",
            "underwriter": "James Harmon",
            "contact_name": "Alan Torres",
            "contact_email": "alan.torres@techforward.io",
            "contact_phone": "(860) 555-0398",
            "street": "200 Tech Park Drive, Suite 400",
            "city": "Stamford",
            "state": "CT",
            "zip": "06902",
            "entity_type": "C-Corporation",
            "industry": "IT / Technology Services",
            "employees": 35,
            "annual_revenue": "$1,000,001 – $2,500,000",
            "notes": "Renewal due soon. Send renewal packet. No claims.",
            "extra_data": json.dumps({"work_offsite": "Yes", "sells_products": "No", "hazmat": "No"}),
        },
        {
            "policy_number": "CGIG-CGL-2024-0004",
            "insured_name": "Green Valley Landscaping",
            "dba": "Green Valley Outdoor Services",
            "policy_type": "CGL",
            "status": "Active",
            "effective_date": str(today - timedelta(days=200)),
            "expiration_date": str(today + timedelta(days=165)),
            "quote_date": str(today - timedelta(days=210)),
            "bound_date": str(today - timedelta(days=201)),
            "premium": 1950.00,
            "commission_rate": 10.0,
            "deductible": "None",
            "per_occurrence": "$500,000",
            "aggregate": "$1,000,000",
            "products_agg": "$1,000,000",
            "agent_name": "David Chen",
            "underwriter": "Lisa Park",
            "contact_name": "Carlos Green",
            "contact_email": "carlos@greenvalleyls.com",
            "contact_phone": "(860) 555-0519",
            "street": "12 Farm Road",
            "city": "Glastonbury",
            "state": "CT",
            "zip": "06033",
            "entity_type": "LLC",
            "industry": "Landscaping / Lawn Care",
            "employees": 8,
            "annual_revenue": "$250,001 – $500,000",
            "notes": "Seasonal business. Peak season March–October.",
            "extra_data": json.dumps({"uses_vehicles": "Yes", "work_offsite": "Yes", "hazmat": "Yes"}),
        },
        {
            "policy_number": "CGIG-CGL-2023-0098",
            "insured_name": "Blue Ridge Medical Supplies",
            "dba": "",
            "policy_type": "CGL",
            "status": "Expired",
            "effective_date": str(today - timedelta(days=400)),
            "expiration_date": str(today - timedelta(days=35)),
            "quote_date": str(today - timedelta(days=415)),
            "bound_date": str(today - timedelta(days=401)),
            "premium": 5600.00,
            "commission_rate": 10.0,
            "deductible": "$2,500",
            "per_occurrence": "$2,000,000",
            "aggregate": "$4,000,000",
            "products_agg": "$4,000,000",
            "agent_name": "Sarah Mitchell",
            "underwriter": "James Harmon",
            "contact_name": "Patricia Blue",
            "contact_email": "pblue@blueridgemedical.com",
            "contact_phone": "(860) 555-0622",
            "street": "500 Medical Center Way",
            "city": "Bridgeport",
            "state": "CT",
            "zip": "06604",
            "entity_type": "C-Corporation",
            "industry": "Wholesale / Distributor",
            "employees": 42,
            "annual_revenue": "$5,000,001 – $10,000,000",
            "notes": "Did not renew — moved to competitor. Follow up Q2.",
            "extra_data": json.dumps({"sells_products": "Yes", "hazmat": "No"}),
        },
        {
            "policy_number": "CGIG-CGL-2024-0007",
            "insured_name": "Summit Property Management",
            "dba": "",
            "policy_type": "CGL",
            "status": "Quote",
            "effective_date": str(today + timedelta(days=15)),
            "expiration_date": str(today + timedelta(days=380)),
            "quote_date": str(today - timedelta(days=5)),
            "bound_date": None,
            "premium": 3750.00,
            "commission_rate": 11.0,
            "deductible": "$1,000",
            "per_occurrence": "$1,000,000",
            "aggregate": "$2,000,000",
            "products_agg": "$2,000,000",
            "agent_name": "David Chen",
            "underwriter": "Lisa Park",
            "contact_name": "Jennifer Summit",
            "contact_email": "jsummit@summitpm.com",
            "contact_phone": "(860) 555-0744",
            "street": "300 Commercial Street",
            "city": "Waterbury",
            "state": "CT",
            "zip": "06702",
            "entity_type": "LLC",
            "industry": "Real Estate",
            "employees": 15,
            "annual_revenue": "$1,000,001 – $2,500,000",
            "notes": "Quote sent 5 days ago. Follow up needed.",
            "extra_data": json.dumps({"work_offsite": "Yes", "sells_products": "No", "hazmat": "No"}),
        },
    ]

    for p in policies:
        cols = ", ".join(p.keys())
        placeholders = ", ".join("?" for _ in p)
        c.execute(f"INSERT INTO policies ({cols}) VALUES ({placeholders})", list(p.values()))

    # Get policy IDs for task FKs
    today_str = str(today)
    tomorrow_str = str(today + timedelta(days=1))
    next_week_str = str(today + timedelta(days=7))
    next_2week_str = str(today + timedelta(days=14))

    tasks = [
        ("Follow up: TechForward Renewal Quote",
         "Renewal is due in 25 days. Send renewal packet and confirm coverage requirements.",
         "Renewal", today_str, "High", "Pending", 3, "Sarah Mitchell"),
        ("Call Riverside Construction re: COI Request",
         "Client needs updated Certificate of Insurance for new subcontract. Policy CGIG-CGL-2024-0001.",
         "Certificate", today_str, "High", "Pending", 1, "Sarah Mitchell"),
        ("Send Summit Property Quote Follow-Up",
         "Quote was sent 5 days ago. Call or email to discuss and answer questions.",
         "Sales", today_str, "Medium", "Pending", 6, "David Chen"),
        ("Process Green Valley Endorsement — Add vehicle",
         "Insured wants to add a new pickup truck to the policy. Collect VIN and update.",
         "Endorsement", tomorrow_str, "Medium", "Pending", 4, "David Chen"),
        ("Blue Ridge — Outreach for Re-quote",
         "Policy expired last month. Reach out to see if they're open to re-quoting with CGIG.",
         "Sales", next_week_str, "Low", "Pending", 5, "Sarah Mitchell"),
        ("Prepare Weekly Renewal Report",
         "Compile list of all policies expiring in next 60 days for management review.",
         "Admin", next_week_str, "Medium", "Pending", None, "Unassigned"),
        ("Main Street Diner — Annual Review Call",
         "Conduct annual coverage review. Discuss revenue growth and any new exposure.",
         "Renewal", next_2week_str, "Low", "Pending", 2, "David Chen"),
        ("Update policy files: Q4 audit",
         "Verify all active policy documents are complete and correctly filed in the system.",
         "Admin", next_2week_str, "Medium", "Pending", None, "Unassigned"),
    ]

    c.executemany(
        """INSERT INTO tasks (title, description, task_type, due_date, priority, status, policy_id, assigned_to)
           VALUES (?,?,?,?,?,?,?,?)""",
        tasks
    )


# ── Policy CRUD ──────────────────────────────────────

def get_policies(search="", status_filter="", type_filter=""):
    conn = get_conn()
    q = "SELECT * FROM policies WHERE 1=1"
    params = []
    if search:
        q += " AND (insured_name LIKE ? OR policy_number LIKE ? OR contact_name LIKE ?)"
        s = f"%{search}%"
        params += [s, s, s]
    if status_filter:
        q += " AND status = ?"
        params.append(status_filter)
    if type_filter:
        q += " AND policy_type = ?"
        params.append(type_filter)
    q += " ORDER BY updated_at DESC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_policy(pid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM policies WHERE id=?", (pid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_policy(data: dict):
    conn = get_conn()
    # Generate policy number
    ptype = data.get("policy_type", "CGL")[:3].upper()
    year = date.today().year
    suffix = "".join(random.choices(string.digits, k=4))
    pnum = f"CGIG-{ptype}-{year}-{suffix}"
    data["policy_number"] = pnum
    data.setdefault("extra_data", "{}")
    data.setdefault("created_at", datetime.now().isoformat(sep=" ", timespec="seconds"))
    data.setdefault("updated_at", datetime.now().isoformat(sep=" ", timespec="seconds"))

    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    conn.execute(f"INSERT INTO policies ({cols}) VALUES ({placeholders})", list(data.values()))
    pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return pid


def update_policy(pid, data: dict):
    data["updated_at"] = datetime.now().isoformat(sep=" ", timespec="seconds")
    conn = get_conn()
    set_clause = ", ".join(f"{k}=?" for k in data)
    conn.execute(f"UPDATE policies SET {set_clause} WHERE id=?", list(data.values()) + [pid])
    conn.commit()
    conn.close()


def delete_policy(pid):
    conn = get_conn()
    conn.execute("DELETE FROM policies WHERE id=?", (pid,))
    conn.commit()
    conn.close()


# ── Tasks CRUD ───────────────────────────────────────

def get_tasks(status_filter="", priority_filter="", policy_id=None, due_today=False):
    conn = get_conn()
    q = """SELECT t.*, p.insured_name, p.policy_number
           FROM tasks t
           LEFT JOIN policies p ON t.policy_id = p.id
           WHERE 1=1"""
    params = []
    if status_filter:
        q += " AND t.status=?"
        params.append(status_filter)
    if priority_filter:
        q += " AND t.priority=?"
        params.append(priority_filter)
    if policy_id:
        q += " AND t.policy_id=?"
        params.append(policy_id)
    if due_today:
        today_str = str(date.today())
        q += " AND (t.due_date <= ? OR t.due_date IS NULL)"
        params.append(today_str)
    q += " ORDER BY CASE t.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END, t.due_date ASC"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task(tid):
    conn = get_conn()
    row = conn.execute(
        "SELECT t.*, p.insured_name FROM tasks t LEFT JOIN policies p ON t.policy_id=p.id WHERE t.id=?",
        (tid,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_task(data: dict):
    conn = get_conn()
    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    conn.execute(f"INSERT INTO tasks ({cols}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    conn.close()


def update_task(tid, data: dict):
    conn = get_conn()
    set_clause = ", ".join(f"{k}=?" for k in data)
    conn.execute(f"UPDATE tasks SET {set_clause} WHERE id=?", list(data.values()) + [tid])
    conn.commit()
    conn.close()


def delete_task(tid):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id=?", (tid,))
    conn.commit()
    conn.close()


# ── Templates ────────────────────────────────────────

def get_templates(type_filter=""):
    conn = get_conn()
    q = "SELECT * FROM policy_templates"
    params = []
    if type_filter:
        q += " WHERE policy_type=?"
        params.append(type_filter)
    q += " ORDER BY policy_type, name"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_template(tid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM policy_templates WHERE id=?", (tid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_template(data: dict):
    conn = get_conn()
    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    data["created_at"] = now
    data["updated_at"] = now
    cols = ", ".join(data.keys())
    placeholders = ", ".join("?" for _ in data)
    conn.execute(f"INSERT INTO policy_templates ({cols}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    conn.close()


def update_template(tid, data: dict):
    data["updated_at"] = datetime.now().isoformat(sep=" ", timespec="seconds")
    conn = get_conn()
    set_clause = ", ".join(f"{k}=?" for k in data)
    conn.execute(f"UPDATE policy_templates SET {set_clause} WHERE id=?", list(data.values()) + [tid])
    conn.commit()
    conn.close()


def delete_template(tid):
    conn = get_conn()
    conn.execute("DELETE FROM policy_templates WHERE id=?", (tid,))
    conn.commit()
    conn.close()


# ── AI Reviews ───────────────────────────────────────

def save_review(policy_id, issues_count, severity, ai_response, corrections):
    conn = get_conn()
    conn.execute(
        "INSERT INTO ai_reviews (policy_id, issues_count, severity, ai_response, corrections) VALUES (?,?,?,?,?)",
        (policy_id, issues_count, severity, ai_response, json.dumps(corrections))
    )
    conn.commit()
    conn.close()


def get_reviews(policy_id):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM ai_reviews WHERE policy_id=? ORDER BY created_at DESC LIMIT 10",
        (policy_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Dashboard stats ──────────────────────────────────

def get_stats():
    conn = get_conn()
    today = str(date.today())
    in_30 = str(date.today() + timedelta(days=30))

    stats = {}
    stats["active"] = conn.execute("SELECT COUNT(*) FROM policies WHERE status='Active'").fetchone()[0]
    stats["pending_renewal"] = conn.execute(
        "SELECT COUNT(*) FROM policies WHERE status IN ('Active','Pending Renewal') AND expiration_date BETWEEN ? AND ?",
        (today, in_30)
    ).fetchone()[0]
    stats["open_tasks"] = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status != 'Completed'"
    ).fetchone()[0]
    result = conn.execute(
        "SELECT COALESCE(SUM(premium),0) FROM policies WHERE status='Active'"
    ).fetchone()[0]
    stats["total_premium"] = result

    stats["recent_policies"] = [dict(r) for r in conn.execute(
        "SELECT * FROM policies ORDER BY updated_at DESC LIMIT 6"
    ).fetchall()]

    stats["today_tasks"] = [dict(r) for r in conn.execute(
        """SELECT t.*, p.insured_name FROM tasks t
           LEFT JOIN policies p ON t.policy_id=p.id
           WHERE t.status != 'Completed' AND (t.due_date <= ? OR t.due_date IS NULL)
           ORDER BY CASE t.priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END
           LIMIT 8""",
        (today,)
    ).fetchall()]

    stats["expiring_soon"] = [dict(r) for r in conn.execute(
        """SELECT * FROM policies
           WHERE status IN ('Active','Pending Renewal')
           AND expiration_date BETWEEN ? AND ?
           ORDER BY expiration_date ASC LIMIT 8""",
        (today, in_30)
    ).fetchall()]

    stats["quotes"] = conn.execute("SELECT COUNT(*) FROM policies WHERE status='Quote'").fetchone()[0]
    conn.close()
    return stats
