const History = (() => {
  const list = document.getElementById('history-list');
  const items = [];

  function add(text) {
    items.unshift(text);
    if (items.length > 20) items.pop();
    render();
  }

  function render() {
    list.innerHTML = items.map(t => `<li>${escapeHtml(t)}</li>`).join('');
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[c]));
  }

  return { add };
})();