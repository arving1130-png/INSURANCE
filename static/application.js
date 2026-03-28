// ── Step navigation ──────────────────────────────────
let currentStep = 1;
const TOTAL_STEPS = 5;

function showStep(n) {
  document.querySelectorAll(".form-step").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".step-label").forEach((l, i) => {
    l.classList.toggle("active", i + 1 === n);
    l.classList.toggle("done", i + 1 < n);
  });
  document.getElementById(`step${n}`).classList.add("active");
  document.getElementById("progressBar").style.width = `${(n / TOTAL_STEPS) * 100}%`;
  window.scrollTo({ top: 0, behavior: "smooth" });
  currentStep = n;
}

function nextStep(from) {
  if (!validateStep(from)) return;
  if (from === 4) buildReviewSummary();
  showStep(from + 1);
}

function prevStep(from) {
  showStep(from - 1);
}

// ── Validation ────────────────────────────────────────
function validateStep(stepNum) {
  const step = document.getElementById(`step${stepNum}`);
  const required = step.querySelectorAll("[required]");
  let ok = true;
  let firstInvalid = null;

  required.forEach(el => {
    el.classList.remove("invalid");
    const val = el.value.trim();
    let fieldOk = true;

    if (el.type === "radio") {
      const name = el.name;
      const group = step.querySelectorAll(`input[name="${name}"]`);
      const checked = Array.from(group).some(r => r.checked);
      if (!checked) {
        fieldOk = false;
        // mark the container
        group.forEach(r => r.parentElement.style.borderColor = "#dc2626");
      } else {
        group.forEach(r => r.parentElement.style.borderColor = "");
      }
    } else if (el.type === "checkbox") {
      if (!el.checked) {
        fieldOk = false;
        el.parentElement.style.borderColor = "#dc2626";
      } else {
        el.parentElement.style.borderColor = "";
      }
    } else {
      if (!val) {
        fieldOk = false;
        el.classList.add("invalid");
      }
    }

    if (!fieldOk) {
      ok = false;
      if (!firstInvalid) firstInvalid = el;
    }
  });

  if (!ok && firstInvalid) {
    firstInvalid.focus();
    firstInvalid.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  return ok;
}

// ── Conditional show/hide ─────────────────────────────
function watchRadio(name, targetId, showValue) {
  document.querySelectorAll(`input[name="${name}"]`).forEach(r => {
    r.addEventListener("change", () => {
      const el = document.getElementById(targetId);
      if (!el) return;
      el.style.display = r.value === showValue && r.checked ? "grid" : "none";
      if (el.tagName === "DIV") el.style.display = r.value === showValue && r.checked ? "block" : "none";
    });
  });
}

watchRadio("sells_products",        "productsDetail",  "Yes");
watchRadio("has_additional_insureds","aiDetail",        "Yes");
watchRadio("has_prior_insurance",    "priorDetail",     "Yes");
watchRadio("has_claims",             "claimsDetail",    "Yes");
watchRadio("was_cancelled",          "cancelDetail",    "Yes");
watchRadio("pending_incidents",      "pendingDetail",   "Yes");

// ── Review Summary ────────────────────────────────────
function buildReviewSummary() {
  const form = document.getElementById("appForm");
  const data = new FormData(form);
  const get = k => data.get(k) || "—";

  const sections = [
    {
      title: "Business Information",
      rows: [
        ["Legal Name", get("legal_name")],
        ["DBA", get("dba") || "—"],
        ["Address", [get("street"), get("city"), get("state"), get("zip")].filter(Boolean).join(", ")],
        ["Contact", `${get("contact_name")} (${get("contact_title")})`],
        ["Phone", get("phone")],
        ["Email", get("email")],
        ["Entity Type", get("entity_type")],
        ["Years in Business", get("years_in_business")],
        ["Desired Effective Date", get("desired_effective")],
      ]
    },
    {
      title: "Business Operations",
      rows: [
        ["Industry", get("industry")],
        ["Operations", get("operations_desc")],
        ["Full-Time Employees", get("full_time_employees")],
        ["Part-Time Employees", get("part_time_employees") || "0"],
        ["Annual Revenue", get("annual_revenue")],
        ["Premises Ownership", get("premises_ownership")],
        ["Work at Customer Sites", get("work_offsite")],
        ["Sells Products", get("sells_products")],
        ["Uses Vehicles", get("uses_vehicles")],
        ["Handles Hazmat", get("hazmat")],
      ]
    },
    {
      title: "Coverage Selected",
      rows: [
        ["Per Occurrence Limit", get("per_occurrence")],
        ["General Aggregate", get("general_aggregate")],
        ["Products & Completed Ops", get("products_completed_ops")],
        ["Medical Payments", get("medical_payments") || "Not selected"],
        ["Deductible", get("deductible") || "Not selected"],
        ["Additional Insureds", get("has_additional_insureds")],
        ["Prior Insurance", get("has_prior_insurance")],
        ["Prior Carrier", get("prior_carrier") || "N/A"],
      ]
    },
    {
      title: "Loss History",
      rows: [
        ["Prior Claims (5 yrs)", get("has_claims")],
        ["Ever Cancelled", get("was_cancelled")],
        ["Known Incidents", get("pending_incidents")],
      ]
    }
  ];

  let html = "";
  sections.forEach(sec => {
    html += `<div class="review-section"><div class="review-section-title">${sec.title}</div><div class="review-rows">`;
    sec.rows.forEach(([label, val]) => {
      if (val && val !== "—") {
        html += `<div class="review-row"><span>${label}</span><strong>${escapeHtml(val)}</strong></div>`;
      }
    });
    html += "</div></div>";
  });

  document.getElementById("reviewSummary").innerHTML = html;

  // Pre-fill signature date
  const today = new Date().toISOString().split("T")[0];
  const sigDate = document.getElementById("signature_date");
  if (sigDate && !sigDate.value) sigDate.value = today;
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// ── Link from chat page ───────────────────────────────
// (Injected into nav via header-back; nothing extra needed here)

// ── Init ──────────────────────────────────────────────
showStep(1);

// Set min effective date to tomorrow
const effDate = document.getElementById("desired_effective");
if (effDate) {
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  effDate.min = tomorrow.toISOString().split("T")[0];
}
