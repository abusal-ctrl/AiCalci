const CONV_UNITS = {
  length:      ["m","km","cm","mm","mi","yd","ft","in"],
  mass:        ["kg","g","mg","lb","oz","t"],
  time:        ["s","min","h","day","week"],
  temperature: ["C","F","K"],
  area:        ["m2","km2","cm2","ft2","in2","acre","ha"],
  volume:      ["L","mL","m3","cm3","gal","qt","pt","cup","floz"],
  speed:       ["m/s","km/h","mph","knot","ft/s"],
  currency:    ["USD","EUR","GBP","INR","JPY","AUD","CAD","CHF","CNY"]
};

document.addEventListener('DOMContentLoaded', () => {
  const cat   = document.getElementById('conv-category');
  const from  = document.getElementById('conv-from');
  const to    = document.getElementById('conv-to');
  const val   = document.getElementById('conv-value');
  const btn   = document.getElementById('conv-submit');
  const out   = document.getElementById('conv-output');

  function fillUnits() {
    const units = CONV_UNITS[cat.value] || [];
    from.innerHTML = units.map(u => `<option value="${u}">${u}</option>`).join('');
    to.innerHTML   = units.map(u => `<option value="${u}">${u}</option>`).join('');
    if (units.length > 1) to.selectedIndex = 1;
  }
  cat.addEventListener('change', fillUnits);
  fillUnits();

  async function run() {
    const value = parseFloat(val.value);
    if (isNaN(value)) return;
    out.className = 'output';
    out.textContent = 'Converting...';
    try {
      const data = await API.convert(cat.value, value, from.value, to.value);
      if (data.success) {
        out.classList.add('success');
        out.textContent = `${value} ${from.value} = ${data.result} ${to.value}`;
        History.add(`🔄 ${value} ${from.value} → ${data.result} ${to.value}`);
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
  val.addEventListener('keypress', e => { if (e.key === 'Enter') run(); });
});