// Dark-themed site script: particle background, installs counter, interactions

/* ---------------------------
   Canvas particle background
   --------------------------- */
const canvas = document.getElementById('bgCanvas');
const ctx = canvas.getContext('2d', { alpha: true });
let W = canvas.width = innerWidth;
let H = canvas.height = innerHeight;
let particles = [];
const PARTICLE_COUNT = Math.max(40, Math.floor(Math.min(W, H) / 18));

function rand(min, max){ return Math.random() * (max - min) + min; }

function makeParticles() {
  particles = [];
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    particles.push({
      x: rand(0, W),
      y: rand(0, H),
      vx: rand(-0.12, 0.12),
      vy: rand(-0.06, 0.06),
      r: rand(0.6, 3.2),
      hue: rand(200, 290),
      life: rand(80, 220)
    });
  }
}
makeParticles();

function resize() {
  W = canvas.width = innerWidth;
  H = canvas.height = innerHeight;
  makeParticles();
}
addEventListener('resize', resize);

let t0 = performance.now();
function drawFrame(now) {
  const dt = Math.min(40, now - t0);
  t0 = now;
  ctx.clearRect(0,0,W,H);

  // darker gradient overlay
  const g = ctx.createLinearGradient(0,0,W,H);
  g.addColorStop(0, 'rgba(3,3,7,0.24)');
  g.addColorStop(1, 'rgba(1,1,3,0.34)');
  ctx.fillStyle = g;
  ctx.fillRect(0,0,W,H);

  // particles (neon points)
  for (let p of particles) {
    p.x += p.vx * dt;
    p.y += p.vy * dt;
    p.life -= dt * 0.02;
    if (p.x < -10) p.x = W + 10;
    if (p.x > W + 10) p.x = -10;
    if (p.y < -10) p.y = H + 10;
    if (p.y > H + 10) p.y = -10;
    if (p.life <= 0) {
      p.x = rand(0, W); p.y = rand(0, H); p.life = rand(80,220);
    }

    const alpha = Math.max(0, Math.min(1, p.life / 220));
    ctx.beginPath();
    const grad = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 6);
    grad.addColorStop(0, `hsla(${p.hue},90%,65%,${0.95 * alpha})`);
    grad.addColorStop(0.6, `hsla(${p.hue},80%,55%,${0.15 * alpha})`);
    grad.addColorStop(1, `rgba(2,6,23,0)`);
    ctx.fillStyle = grad;
    ctx.arc(p.x, p.y, p.r * 6, 0, Math.PI*2);
    ctx.fill();
  }

  // connection lines (very subtle)
  ctx.beginPath();
  for (let i=0;i<particles.length;i++){
    for (let j=i+1;j<particles.length;j++){
      const a=particles[i], b=particles[j];
      const dx=a.x-b.x, dy=a.y-b.y;
      const d2 = dx*dx+dy*dy;
      if (d2 < 8000){ // smaller threshold for denser look
        const alpha = 0.06 * (1 - d2/8000);
        ctx.strokeStyle = `rgba(124,92,255,${alpha})`;
        ctx.lineWidth = 0.5;
        ctx.moveTo(a.x,a.y);
        ctx.lineTo(b.x,b.y);
      }
    }
  }
  ctx.stroke();
  requestAnimationFrame(drawFrame);
}
requestAnimationFrame(drawFrame);

/* ---------------------------
   Installs counter (no arc)
   --------------------------- */
const API = 'https://pepy.tech/projects/artemis-ui';
const counterEl = document.getElementById('counter');
const counterSub = document.getElementById('counter-sub');

function animateNumber(target){
  const start = Number((counterEl.dataset.current) || 0);
  const duration = 1100 + Math.min(2000, Math.log(target+1)*120);
  const t0 = performance.now();
  function step(t){
    const p = Math.min(1, (t - t0) / duration);
    const eased = 1 - Math.pow(1 - p, 3);
    const v = Math.floor(start + (target - start) * eased);
    counterEl.textContent = v.toLocaleString();
    counterEl.dataset.current = v;
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

async function fetchInstalls(){
  counterSub.textContent = 'fetching…';
  counterEl.textContent = '…';
  try {
    const res = await fetch(API, {cache: 'no-store'});
    if (!res.ok) throw new Error('fetch error');
    const data = await res.json();
    const last = data?.downloads?.last_month ?? data?.downloads?.last_30 ?? null;
    if (last == null) throw new Error('no-data');
    animateNumber(Number(last));
    counterSub.textContent = 'source: pepy.tech';
  } catch (err) {
    console.warn('live fetch failed', err);
    counterSub.textContent = 'using cached value';
    try {
      const r = await fetch('./stats/installs.json');
      if (r.ok){
        const j = await r.json();
        if (j?.last_month) { animateNumber(Number(j.last_month)); counterSub.textContent = 'source: stats/installs.json'; return; }
      }
      counterEl.textContent = '—';
      counterSub.textContent = 'unavailable';
    } catch(e){
      counterEl.textContent = '—';
      counterSub.textContent = 'unavailable';
    }
  }
}
fetchInstalls();
setInterval(fetchInstalls, 10*60*1000);

/* ---------------------------
   Copy pip button micro-interaction
   --------------------------- */
const copyBtn = document.getElementById('copyBtn');
copyBtn.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText('pip install artemis-ui');
    copyBtn.textContent = 'Copied ✓';
    copyBtn.classList.add('copied');
    setTimeout(()=>{ copyBtn.textContent = 'pip install artemis-ui'; copyBtn.classList.remove('copied'); },1500);
  } catch {
    const ok = prompt('Copy this:', 'pip install artemis-ui');
    if (!ok) {/* ignore */}
  }
});

/* ---------------------------
   Small interaction: title nudge on hover
   --------------------------- */
const title = document.querySelector('.glow-title');
title.addEventListener('mouseenter', ()=> {
  title.style.transform = 'translateX(2px)';
  title.style.transition = 'transform 260ms ease';
  setTimeout(()=> title.style.transform = '', 300);
});
