import os
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import anthropic
from dotenv import load_dotenv
import db as database

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cgig-dev-secret-2024")
CORS(app)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Initialise database on startup
database.init_db()

# Register Jinja2 custom filter
@app.template_filter('fromjson')
def fromjson_filter(value):
    try:
        return json.loads(value) if value else {}
    except Exception:
        return {}

# ── Customer chat system prompt ───────────────────────
CHAT_SYSTEM_PROMPT = """You are Alex, a friendly and knowledgeable customer service representative for **Commercial General Insurance Group (CGIG)**.

Your role is to assist customers with all their commercial general liability insurance needs. You are professional, empathetic, and always aim to resolve customer concerns efficiently.

## About Commercial General Insurance Group (CGIG)
- Founded in 1987, CGIG is a leading provider of commercial insurance solutions
- Specializes in General Liability, Property, Workers' Compensation, Commercial Auto, and Umbrella/Excess policies
- Serves small businesses, mid-market companies, and large enterprises across all industries
- Available Mon–Fri 8am–6pm EST; 24/7 emergency claims hotline: 1-800-CGIG-CLAIM
- Main office: 500 Commerce Plaza, Hartford, CT 06103
- Website: www.cgig.com | Email: support@cgig.com

## Products & Coverage
**Commercial General Liability (CGL)**
- Bodily injury & property damage liability
- Personal & advertising injury
- Medical payments
- Products & completed operations
- Limits from $300K to $10M+ per occurrence

**Commercial Property**
- Building & business personal property
- Business interruption / loss of income

**Workers' Compensation**
- Statutory benefits per state law

**Commercial Auto**
- Liability, collision, comprehensive

**Umbrella / Excess Liability**
- $1M–$25M limits over underlying policies

## Claims Process
1. Report claim immediately: 1-800-CGIG-CLAIM or claims@cgig.com
2. A claims adjuster contacts within 24 business hours
3. Provide: policy number, date of loss, description, photos/documents

## Tone Guidelines
- Always greet customers warmly and use their name if provided
- Be concise but thorough
- Never quote specific premiums — direct to a formal quote
- For urgent matters always recommend the 24/7 hotline
- End by asking if there's anything else you can help with"""

# ── AI policy review system prompt ───────────────────
REVIEW_SYSTEM_PROMPT = """You are an expert commercial insurance underwriter and quality control specialist at Commercial General Insurance Group (CGIG).

Your job is to review Commercial General Liability (CGL) policy records and identify:
1. Missing or incomplete required fields
2. Date logic errors (e.g. effective date after expiration date, bound date before quote date)
3. Coverage limit gaps or mismatches for the stated industry/risk
4. Inconsistencies between fields (e.g. contractor industry but no work_offsite flag)
5. Potential compliance issues
6. Mathematical errors in premium or commission
7. Any other quality issues

Respond ONLY with a valid JSON object in this exact structure:
{
  "summary": "One or two sentence overall assessment",
  "overall_severity": "low|medium|high",
  "issues": [
    {
      "field": "field_name_or_section",
      "issue": "Clear description of the problem",
      "severity": "low|medium|high",
      "suggestion": "Specific correction to make",
      "corrected_value": "The corrected value if applicable, otherwise null"
    }
  ],
  "recommendations": ["Actionable recommendation 1", "Recommendation 2"]
}

If no issues are found, return an empty issues array and overall_severity of "low".
Be specific and actionable. Flag real problems, not trivial style issues."""


# ════════════════════════════════════════════════════
# CUSTOMER CHAT
# ════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Invalid request"}), 400
    messages = data["messages"]
    for msg in messages:
        if "role" not in msg or "content" not in msg:
            return jsonify({"error": "Invalid message format"}), 400
        if msg["role"] not in ("user", "assistant"):
            return jsonify({"error": "Invalid role"}), 400
    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=CHAT_SYSTEM_PROMPT,
            messages=messages,
        )
        return jsonify({"reply": response.content[0].text})
    except anthropic.AuthenticationError:
        return jsonify({"error": "API authentication failed."}), 500
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit reached. Please try again shortly."}), 429
    except anthropic.APIError as e:
        return jsonify({"error": f"API error: {str(e)}"}), 500


# ════════════════════════════════════════════════════
# CGL APPLICATION
# ════════════════════════════════════════════════════

@app.route("/apply")
def apply():
    return render_template("application.html")


@app.route("/apply/submit", methods=["POST"])
def submit_application():
    form = request.form.to_dict()
    return render_template("confirmation.html", form=form)


# ════════════════════════════════════════════════════
# MANAGEMENT DASHBOARD
# ════════════════════════════════════════════════════

@app.route("/dashboard")
def dashboard():
    stats = database.get_stats()
    return render_template("dashboard.html", **stats)


# ════════════════════════════════════════════════════
# POLICIES
# ════════════════════════════════════════════════════

@app.route("/policies")
def policies():
    search = request.args.get("q", "")
    status_filter = request.args.get("status", "")
    type_filter = request.args.get("type", "")
    policies_list = database.get_policies(search, status_filter, type_filter)
    return render_template("policies.html",
                           policies=policies_list,
                           search=search,
                           status_filter=status_filter,
                           type_filter=type_filter)


@app.route("/policy/<int:pid>")
def policy_detail(pid):
    policy = database.get_policy(pid)
    if not policy:
        flash("Policy not found.", "error")
        return redirect(url_for("policies"))
    policy_tasks = database.get_tasks(policy_id=pid)
    reviews = database.get_reviews(pid)
    extra = json.loads(policy.get("extra_data") or "{}")
    return render_template("policy_detail.html",
                           policy=policy,
                           tasks=policy_tasks,
                           reviews=reviews,
                           extra=extra)


@app.route("/policy/<int:pid>/edit", methods=["POST"])
def policy_edit(pid):
    allowed = [
        "insured_name", "dba", "policy_type", "status",
        "effective_date", "expiration_date", "bound_date",
        "premium", "commission_rate", "deductible",
        "per_occurrence", "aggregate", "products_agg",
        "agent_name", "underwriter", "contact_name",
        "contact_email", "contact_phone", "street",
        "city", "state", "zip", "entity_type",
        "industry", "employees", "annual_revenue", "notes"
    ]
    data = {k: request.form.get(k, "") for k in allowed if request.form.get(k) is not None}
    database.update_policy(pid, data)
    flash("Policy updated successfully.", "success")
    return redirect(url_for("policy_detail", pid=pid))


@app.route("/policy/<int:pid>/delete", methods=["POST"])
def policy_delete(pid):
    database.delete_policy(pid)
    flash("Policy deleted.", "info")
    return redirect(url_for("policies"))


@app.route("/policy/new", methods=["GET"])
def policy_new():
    templates = database.get_templates()
    template_id = request.args.get("template")
    selected_tpl = None
    if template_id:
        selected_tpl = database.get_template(int(template_id))
    return render_template("policy_new.html",
                           templates=templates,
                           selected_tpl=selected_tpl)


@app.route("/policy/create", methods=["POST"])
def policy_create():
    allowed = [
        "insured_name", "dba", "policy_type", "status",
        "effective_date", "expiration_date", "quote_date",
        "premium", "commission_rate", "deductible",
        "per_occurrence", "aggregate", "products_agg",
        "agent_name", "underwriter", "contact_name",
        "contact_email", "contact_phone", "street",
        "city", "state", "zip", "entity_type",
        "industry", "employees", "annual_revenue", "notes"
    ]
    data = {k: request.form.get(k, "") for k in allowed if request.form.get(k) is not None}
    data["extra_data"] = "{}"
    pid = database.create_policy(data)
    flash("Policy created successfully.", "success")
    return redirect(url_for("policy_detail", pid=pid))


# ════════════════════════════════════════════════════
# AI POLICY REVIEW
# ════════════════════════════════════════════════════

@app.route("/policy/<int:pid>/ai-review", methods=["POST"])
def ai_review(pid):
    policy = database.get_policy(pid)
    if not policy:
        return jsonify({"error": "Policy not found"}), 404

    extra = json.loads(policy.get("extra_data") or "{}")
    policy_text = json.dumps({**policy, **extra}, indent=2, default=str)

    prompt = f"""Please review this insurance policy record and identify any issues, errors, or improvements needed:

{policy_text}

Return your analysis as a JSON object following the specified structure."""

    try:
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=REVIEW_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[-1].text  # last block is text after thinking

        # Parse the JSON response
        import re
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {"summary": raw, "overall_severity": "low", "issues": [], "recommendations": []}

        issues_count = len(result.get("issues", []))
        severity = result.get("overall_severity", "low")
        database.save_review(pid, issues_count, severity, raw, result.get("issues", []))

        return jsonify(result)

    except anthropic.APIError as e:
        return jsonify({"error": f"AI review failed: {str(e)}"}), 500
    except (json.JSONDecodeError, Exception) as e:
        return jsonify({"error": f"Could not parse AI response: {str(e)}"}), 500


@app.route("/policy/<int:pid>/apply-correction", methods=["POST"])
def apply_correction(pid):
    data = request.get_json()
    field = data.get("field")
    value = data.get("value")
    if not field or value is None:
        return jsonify({"error": "Missing field or value"}), 400
    # Only update known policy columns (security guard)
    allowed_fields = {
        "insured_name", "dba", "status", "effective_date", "expiration_date",
        "premium", "commission_rate", "deductible", "per_occurrence", "aggregate",
        "products_agg", "agent_name", "underwriter", "contact_name",
        "contact_email", "contact_phone", "notes"
    }
    if field not in allowed_fields:
        return jsonify({"error": "Field not editable via correction"}), 400
    database.update_policy(pid, {field: value})
    return jsonify({"ok": True})


# ════════════════════════════════════════════════════
# TASKS
# ════════════════════════════════════════════════════

@app.route("/tasks")
def tasks():
    status_filter = request.args.get("status", "")
    priority_filter = request.args.get("priority", "")
    all_tasks = database.get_tasks(status_filter=status_filter, priority_filter=priority_filter)
    policies_list = database.get_policies()
    return render_template("tasks.html",
                           tasks=all_tasks,
                           policies=policies_list,
                           status_filter=status_filter,
                           priority_filter=priority_filter)


@app.route("/tasks/create", methods=["POST"])
def task_create():
    data = {
        "title": request.form.get("title", "").strip(),
        "description": request.form.get("description", "").strip(),
        "task_type": request.form.get("task_type", "General"),
        "due_date": request.form.get("due_date", ""),
        "priority": request.form.get("priority", "Medium"),
        "status": "Pending",
        "assigned_to": request.form.get("assigned_to", "Unassigned"),
    }
    pid = request.form.get("policy_id")
    if pid:
        data["policy_id"] = int(pid)
    database.create_task(data)
    flash("Task created.", "success")
    return redirect(url_for("tasks"))


@app.route("/tasks/<int:tid>/status", methods=["POST"])
def task_status(tid):
    new_status = request.form.get("status", "Pending")
    update = {"status": new_status}
    if new_status == "Completed":
        from datetime import datetime
        update["completed_at"] = datetime.now().isoformat(sep=" ", timespec="seconds")
    database.update_task(tid, update)
    # Support AJAX
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True})
    return redirect(request.referrer or url_for("tasks"))


@app.route("/tasks/<int:tid>/delete", methods=["POST"])
def task_delete(tid):
    database.delete_task(tid)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True})
    return redirect(url_for("tasks"))


# ════════════════════════════════════════════════════
# TEMPLATES
# ════════════════════════════════════════════════════

@app.route("/templates")
def templates():
    type_filter = request.args.get("type", "")
    tpl_list = database.get_templates(type_filter)
    return render_template("policy_templates.html",
                           templates=tpl_list,
                           type_filter=type_filter)


@app.route("/templates/create", methods=["POST"])
def template_create():
    defaults_raw = request.form.get("defaults", "{}")
    try:
        json.loads(defaults_raw)
    except json.JSONDecodeError:
        defaults_raw = "{}"
    data = {
        "name": request.form.get("name", "").strip(),
        "policy_type": request.form.get("policy_type", "CGL"),
        "description": request.form.get("description", "").strip(),
        "defaults": defaults_raw,
    }
    database.create_template(data)
    flash("Template created.", "success")
    return redirect(url_for("templates"))


@app.route("/templates/<int:tid>/edit", methods=["POST"])
def template_edit(tid):
    defaults_raw = request.form.get("defaults", "{}")
    try:
        json.loads(defaults_raw)
    except json.JSONDecodeError:
        defaults_raw = "{}"
    data = {
        "name": request.form.get("name", "").strip(),
        "policy_type": request.form.get("policy_type", "CGL"),
        "description": request.form.get("description", "").strip(),
        "defaults": defaults_raw,
    }
    database.update_template(tid, data)
    flash("Template updated.", "success")
    return redirect(url_for("templates"))


@app.route("/templates/<int:tid>/delete", methods=["POST"])
def template_delete(tid):
    database.delete_template(tid)
    flash("Template deleted.", "info")
    return redirect(url_for("templates"))


@app.route("/api/template/<int:tid>")
def api_template(tid):
    tpl = database.get_template(tid)
    if not tpl:
        return jsonify({}), 404
    defaults = json.loads(tpl.get("defaults") or "{}")
    return jsonify({"template": tpl, "defaults": defaults})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
