// script.js — fetch installs and animate the counter
const INST_DOM = document.getElementById('installs');
const INSTALL_BTN = document.getElementById('install-btn');

INSTALL_BTN.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText('pip install artemis-ui');
    INSTALL_BTN.textContent = 'Copied!';
    setTimeout(()=> INSTALL_BTN.textContent = 'pip install artemis-ui',1400);
  } catch(e){
    // fallback: select text
    alert('Copy this: pip install artemis-ui');
  }
});

function animateCount(node, target) {
  const start = 0;
  const duration = Math.min(2000, 20 * Math.log(target + 1) * 100);
  const startTime = performance.now();
  function tick(now){
    const t = Math.min(1, (now - startTime) / duration);
    const eased = (1 - Math.cos(Math.PI * t)) / 2;
    const val = Math.floor(start + (target - start) * eased);
    node.textContent = val.toLocaleString();
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

async function fetchInstalls() {
  const API = 'https://pepy.tech/api/v2/projects/artemis-ui';
  // show a pleasant loading animation
  INST_DOM.textContent = '…';
  try {
    const res = await fetch(API, {cache: 'no-store'});
    if (!res.ok) throw new Error('failed to fetch');
    const data = await res.json();
    // pepy.tech returns downloads.last_month
    const lastMonth = data?.downloads?.last_month ?? data?.downloads?.last_30 ?? null;
    if (lastMonth == null) throw new Error('no monthly data');
    animateCount(INST_DOM, Number(lastMonth));
  } catch (err) {
    console.warn('pepy fetch failed', err);
    // fallback: show a badge or a cached value
    INST_DOM.textContent = '—';
    // Optional: attempt a cached JSON at ./stats/installs.json if you set up a workflow
    try {
      const cached = await fetch('./stats/installs.json');
      if (cached.ok) {
        const j = await cached.json();
        if (j.last_month) animateCount(INST_DOM, Number(j.last_month));
      }
    } catch(e){
      // nothing
    }
  }
}

// run on load
fetchInstalls();

// Optional: poll every 10 minutes to keep it fresh on long-lived pages
setInterval(fetchInstalls, 10 * 60 * 1000);
