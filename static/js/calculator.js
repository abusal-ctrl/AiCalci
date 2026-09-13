document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('calc-input');
  const btn = document.getElementById('calc-submit');
  const clearBtn = document.getElementById('calc-clear');
  const out = document.getElementById('calc-output');

  // Keypad
  document.querySelectorAll('.keypad button').forEach(k => {
    k.addEventListener('click', () => {
      const ins = k.dataset.ins;
      const start = input.selectionStart;
      const end = input.selectionEnd;
      const before = input.value.slice(0, start);
      const after = input.value.slice(end);
      input.value = before + ins + after;
      input.focus();
      input.selectionStart = input.selectionEnd = start + ins.length;
    });
  });

  clearBtn.addEventListener('click', () => {
    input.value = '';
    out.textContent = '';
    out.className = 'output';
    input.focus();
  });

  async function run() {
    const expr = input.value.trim();
    if (!expr) return;
    out.className = 'output';
    out.textContent = 'Calculating...';
    try {
      const data = await API.calculate(expr);
      if (data.success) {
        out.classList.add('success');
        out.textContent = `= ${data.result}`;
        History.add(`🧮 ${expr} = ${data.result}`);
      } else {
        out.classList.add('error');
        out.textContent = `Error: ${data.error}`;
      }
    } catch (e) {
      out.classList.add('error');
      out.textContent = `Error: ${e.message}`;
    }
  }

  btn.addEventListener('click', run);
  input.addEventListener('keypress', e => { if (e.key === 'Enter') run(); });
});