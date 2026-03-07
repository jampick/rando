// Tab switching
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');

tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    panels.forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
  });
});

// Haptic feedback helper
function vibrate(ms = 20) {
  if (navigator.vibrate) navigator.vibrate(ms);
}

// --- Coin Flip ---
const coinEl = document.querySelector('.coin');
const coinResult = document.getElementById('coin-result');
const headsCount = document.getElementById('heads-count');
const tailsCount = document.getElementById('tails-count');
let heads = 0, tails = 0, flipping = false;

document.getElementById('flip-btn').addEventListener('click', () => {
  if (flipping) return;
  flipping = true;
  vibrate();

  const isHeads = Math.random() < 0.5;

  // Reset animation
  coinEl.classList.remove('flip-heads', 'flip-tails');
  void coinEl.offsetWidth; // force reflow

  coinEl.classList.add(isHeads ? 'flip-heads' : 'flip-tails');

  setTimeout(() => {
    if (isHeads) {
      heads++;
      headsCount.textContent = heads;
      coinResult.textContent = 'Heads!';
    } else {
      tails++;
      tailsCount.textContent = tails;
      coinResult.textContent = 'Tails!';
    }
    vibrate(30);
    flipping = false;
  }, 800);
});

// --- Dice Roller ---
let diceSides = 6;
let diceCount = 1;

document.querySelectorAll('.dice-type').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.dice-type').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    diceSides = parseInt(btn.dataset.sides);
  });
});

document.getElementById('dice-minus').addEventListener('click', () => {
  if (diceCount > 1) {
    diceCount--;
    document.getElementById('dice-count').textContent = diceCount;
  }
});

document.getElementById('dice-plus').addEventListener('click', () => {
  if (diceCount < 20) {
    diceCount++;
    document.getElementById('dice-count').textContent = diceCount;
  }
});

document.getElementById('roll-btn').addEventListener('click', () => {
  vibrate();
  const display = document.getElementById('dice-display');
  const totalEl = document.getElementById('dice-total');
  display.innerHTML = '';

  let total = 0;
  for (let i = 0; i < diceCount; i++) {
    const val = Math.floor(Math.random() * diceSides) + 1;
    total += val;

    const die = document.createElement('div');
    die.className = 'die-result';
    die.textContent = val;
    die.style.animationDelay = `${i * 0.05}s`;
    display.appendChild(die);
  }

  totalEl.textContent = diceCount > 1 ? `Total: ${total}` : total;
  vibrate(30);
});

// --- Random Number ---
document.getElementById('generate-btn').addEventListener('click', () => {
  vibrate();
  const min = parseInt(document.getElementById('num-min').value) || 0;
  const max = parseInt(document.getElementById('num-max').value) || 100;
  const lo = Math.min(min, max);
  const hi = Math.max(min, max);
  const val = Math.floor(Math.random() * (hi - lo + 1)) + lo;

  const display = document.getElementById('number-display');
  display.textContent = val;
  display.classList.remove('shake');
  void display.offsetWidth;
  display.classList.add('shake');
  vibrate(30);
});

// --- List Picker ---
document.getElementById('pick-btn').addEventListener('click', () => {
  vibrate();
  const text = document.getElementById('picker-items').value.trim();
  if (!text) return;

  const items = text.split('\n').map(s => s.trim()).filter(Boolean);
  if (items.length === 0) return;

  const picked = items[Math.floor(Math.random() * items.length)];
  const display = document.getElementById('picker-display');

  // Quick shuffle animation
  let count = 0;
  const interval = setInterval(() => {
    display.textContent = items[Math.floor(Math.random() * items.length)];
    display.style.fontSize = '';
    count++;
    if (count > 10) {
      clearInterval(interval);
      display.textContent = picked;
      // Scale font for long text
      if (picked.length > 12) {
        display.style.fontSize = '2rem';
      }
      display.classList.remove('shake');
      void display.offsetWidth;
      display.classList.add('shake');
      vibrate(40);
    }
  }, 60);
});

// Register service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('sw.js').catch(() => {});
}
