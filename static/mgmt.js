/* mgmt.js — Management app interactivity */

// ── Modal helpers ──────────────────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('active'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('active'); document.body.style.overflow = ''; }
}
// Close on backdrop click
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-overlay') && e.target.classList.contains('active')) {
    e.target.classList.remove('active');
    document.body.style.overflow = '';
  }
});
// Close on Escape
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.active').forEach(function(m) {
      m.classList.remove('active');
    });
    document.body.style.overflow = '';
  }
});

// ── Edit form toggle (policy detail) ──────────────────────────────────────
function toggleEdit() {
  const form   = document.getElementById('editForm');
  const header = document.querySelector('.detail-header-card');
  const info   = document.querySelector('.info-sections');
  if (!form) return;
  const showing = form.style.display !== 'none';
  form.style.display   = showing ? 'none'  : 'block';
  if (header) header.style.display = showing ? ''     : 'none';
  if (info)   info.style.display   = showing ? ''     : 'none';
  if (!showing) form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Task completion (policy detail inline check button) ───────────────────
function completeTask(taskId, btn) {
  if (btn.classList.contains('checked')) return;
  fetch('/tasks/' + taskId + '/status', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'status=Completed'
  })
  .then(function(r) {
    if (r.ok) {
      btn.classList.add('checked');
      const li = btn.closest('li');
      if (li) {
        li.classList.add('task-done');
        const title = li.querySelector('.task-title');
        if (title) title.classList.add('done');
      }
    }
  })
  .catch(function(err) { console.error('Task update failed:', err); });
}

// ── AI Policy Review ───────────────────────────────────────────────────────
function runAIReview(policyId) {
  const btn      = document.getElementById('aiBtn');
  const panelBtn = document.getElementById('aiPanelBtn');
  const results  = document.getElementById('aiResults');
  if (!results) return;

  // Loading state
  [btn, panelBtn].forEach(function(b) {
    if (b) { b.disabled = true; b.textContent = '⟳ Analyzing…'; }
  });
  results.innerHTML = '<div class="ai-loading"><div class="ai-spinner"></div><span>Claude is reviewing this policy…</span></div>';

  fetch('/policy/' + policyId + '/ai-review', { method: 'POST' })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      [btn, panelBtn].forEach(function(b) {
        if (b) { b.disabled = false; b.textContent = '✦ AI Review'; }
      });
      if (panelBtn) panelBtn.textContent = 'Run AI Review';

      if (data.error) {
        results.innerHTML = '<div class="ai-error">Review failed: ' + escHtml(data.error) + '</div>';
        return;
      }
      renderAIResults(results, data, policyId);
    })
    .catch(function(err) {
      [btn, panelBtn].forEach(function(b) {
        if (b) { b.disabled = false; b.textContent = '✦ AI Review'; }
      });
      if (panelBtn) panelBtn.textContent = 'Run AI Review';
      results.innerHTML = '<div class="ai-error">Network error. Please try again.</div>';
      console.error(err);
    });
}

function renderAIResults(container, data, policyId) {
  if (!data.issues || data.issues.length === 0) {
    container.innerHTML = '<div class="ai-clean"><span class="ai-clean-icon">✓</span><span>No issues found — policy looks good!</span></div>';
    return;
  }

  const sevOrder = { critical: 0, high: 1, medium: 2, low: 3 };
  const sorted   = data.issues.slice().sort(function(a, b) {
    return (sevOrder[a.severity] || 4) - (sevOrder[b.severity] || 4);
  });

  let html = '<div class="ai-summary">Found ' + sorted.length + ' issue' + (sorted.length !== 1 ? 's' : '') + ' · Severity: <span class="sev-badge sev-' + (data.overall_severity || 'medium') + '">' + (data.overall_severity || 'medium') + '</span></div>';
  html += '<div class="ai-issues">';

  sorted.forEach(function(issue) {
    const sev   = (issue.severity  || 'medium').toLowerCase();
    const field = issue.field      || '';
    const canFix = issue.suggested_value && field;

    html += '<div class="ai-issue ai-issue-' + sev + '">';
    html += '  <div class="ai-issue-top">';
    html += '    <span class="sev-badge sev-' + sev + '">' + sev + '</span>';
    if (field) html += '    <span class="ai-issue-field">' + escHtml(field.replace(/_/g, ' ')) + '</span>';
    html += '  </div>';
    html += '  <div class="ai-issue-desc">' + escHtml(issue.description || '') + '</div>';
    if (issue.suggestion) {
      html += '  <div class="ai-issue-sugg">' + escHtml(issue.suggestion) + '</div>';
    }
    if (canFix) {
      html += '  <button class="btn-ai-apply" onclick="applyCorrection(' + policyId + ', ' + JSON.stringify(field) + ', ' + JSON.stringify(issue.suggested_value) + ', this)">Apply Fix</button>';
    }
    html += '</div>';
  });

  html += '</div>';
  if (data.summary) {
    html += '<div class="ai-summary-text">' + escHtml(data.summary) + '</div>';
  }
  container.innerHTML = html;
}

function applyCorrection(policyId, field, value, btn) {
  btn.disabled    = true;
  btn.textContent = 'Applying…';
  fetch('/policy/' + policyId + '/apply-correction', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ field: field, value: value })
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.success) {
      btn.textContent = '✓ Applied';
      btn.classList.add('btn-ai-applied');
      const issueEl = btn.closest('.ai-issue');
      if (issueEl) issueEl.style.opacity = '0.55';
    } else {
      btn.disabled    = false;
      btn.textContent = 'Apply Fix';
      alert('Could not apply: ' + (data.error || 'Unknown error'));
    }
  })
  .catch(function(err) {
    btn.disabled    = false;
    btn.textContent = 'Apply Fix';
    console.error(err);
  });
}

// ── Mobile nav toggle ──────────────────────────────────────────────────────
(function() {
  const toggle  = document.getElementById('navToggle');
  const sidebar = document.querySelector('.sidebar');
  if (!toggle || !sidebar) return;
  toggle.addEventListener('click', function() {
    sidebar.classList.toggle('sidebar-open');
    toggle.setAttribute('aria-expanded', sidebar.classList.contains('sidebar-open'));
  });
  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', function(e) {
    if (sidebar.classList.contains('sidebar-open') &&
        !sidebar.contains(e.target) && e.target !== toggle) {
      sidebar.classList.remove('sidebar-open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
})();

// ── Flash message auto-dismiss ─────────────────────────────────────────────
(function() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function(f) {
    setTimeout(function() {
      f.style.transition = 'opacity 0.4s ease';
      f.style.opacity    = '0';
      setTimeout(function() { f.remove(); }, 450);
    }, 4000);
  });
})();

// ── Utility: HTML escape ───────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
