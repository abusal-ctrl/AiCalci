document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('ai-input');
  const btn   = document.getElementById('ai-submit');
  const out   = document.getElementById('ai-output');

  function renderMarkdown(text) {
    // Escape HTML first
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Newlines
    html = html.replace(/\n/g, '<br>');
    return html;
  }

  async function run() {
    const q = input.value.trim();
    if (!q) return;
    out.className = 'output';
    out.innerHTML = 'Thinking...';
    btn.disabled = true;

    try {
      const data = await API.aiSolve(q);

      if (data.success && !data.error) {
        out.classList.add('success');
        let html = '';

        if (data.steps && data.steps.length) {
          html += data.steps.map(s => `<div class="step">${renderMarkdown(s)}</div>`).join('');
        }
        html += `<hr><div class="final">✅ <strong>Final answer:</strong> ${renderMarkdown(data.final_answer)}</div>`;

        if (data.verified) {
          html += `<div class="verified">✔ Verified: ${renderMarkdown(data.verification_note || '')}</div>`;
        }
        out.innerHTML = html;
        History.add(`🤖 ${q}\n   → ${data.final_answer}`);
      } else {
        out.classList.add('error');
        out.textContent = `Error: ${data.error || 'Unknown error'}`;
      }
    } catch (e) {
      out.classList.add('error');
      out.textContent = `Error: ${e.message}`;
    } finally {
      btn.disabled = false;
    }
  }

  btn.addEventListener('click', run);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) run();
  });
});