const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");
const scoreEl = document.getElementById("score");
const livesEl = document.getElementById("lives");
const statusEl = document.getElementById("status");
const restartEl = document.getElementById("restart");

const tileSize = 32;
const grid = 10;

const dirs = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 }
};

let pellets = [];
let score = 0;
let lives = 3;
let gameOver = false;

const pacman = {
  x: 1,
  y: 1,
  dir: "right",
  mouth: 0
};

const ghost = {
  x: 8,
  y: 8,
  dir: "left"
};

function resetPellets() {
  pellets = [];
  for (let y = 0; y < grid; y += 1) {
    for (let x = 0; x < grid; x += 1) {
      const startOrGhost = (x === 1 && y === 1) || (x === 8 && y === 8);
      if (!startOrGhost) pellets.push({ x, y });
    }
  }
}

function setStatus(text, kind = "") {
  statusEl.textContent = text;
  statusEl.className = `status ${kind}`.trim();
}

function move(entity) {
  const d = dirs[entity.dir];
  entity.x = (entity.x + d.x + grid) % grid;
  entity.y = (entity.y + d.y + grid) % grid;
}

function pickGhostDirection() {
  const options = Object.keys(dirs);
  const best = options.reduce((acc, dir) => {
    const nx = (ghost.x + dirs[dir].x + grid) % grid;
    const ny = (ghost.y + dirs[dir].y + grid) % grid;
    const dist = Math.abs(nx - pacman.x) + Math.abs(ny - pacman.y);
    if (!acc || dist < acc.dist) return { dir, dist };
    return acc;
  }, null);

  ghost.dir = Math.random() < 0.7 ? best.dir : options[Math.floor(Math.random() * options.length)];
}

function eatPellet() {
  const idx = pellets.findIndex((p) => p.x === pacman.x && p.y === pacman.y);
  if (idx !== -1) {
    pellets.splice(idx, 1);
    score += 10;
    scoreEl.textContent = String(score);

    if (pellets.length === 0) {
      setStatus("Você venceu! 🎉", "ok");
      gameOver = true;
    }
  }
}

function checkCollision() {
  if (pacman.x === ghost.x && pacman.y === ghost.y) {
    lives -= 1;
    livesEl.textContent = String(lives);

    if (lives <= 0) {
      setStatus("Game Over 💥", "danger");
      gameOver = true;
      return;
    }

    setStatus("Ops! O fantasma te pegou.", "danger");
    pacman.x = 1;
    pacman.y = 1;
    ghost.x = 8;
    ghost.y = 8;
  }
}

function drawCell(x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let y = 0; y < grid; y += 1) {
    for (let x = 0; x < grid; x += 1) {
      drawCell(x, y, (x + y) % 2 === 0 ? "#101735" : "#0a1129");
    }
  }

  pellets.forEach((p) => {
    ctx.beginPath();
    ctx.fillStyle = "#f5f5f5";
    ctx.arc(p.x * tileSize + 16, p.y * tileSize + 16, 4, 0, Math.PI * 2);
    ctx.fill();
  });

  const centerX = pacman.x * tileSize + 16;
  const centerY = pacman.y * tileSize + 16;
  const open = (Math.sin(pacman.mouth) + 1) * 0.2;
  const angles = {
    right: [open, Math.PI * 2 - open],
    left: [Math.PI + open, Math.PI - open],
    up: [Math.PI * 1.5 + open, Math.PI * 1.5 - open],
    down: [Math.PI * 0.5 + open, Math.PI * 0.5 - open]
  };

  ctx.beginPath();
  ctx.moveTo(centerX, centerY);
  ctx.fillStyle = "#ffd53d";
  ctx.arc(centerX, centerY, 13, angles[pacman.dir][0], angles[pacman.dir][1], false);
  ctx.fill();

  ctx.beginPath();
  ctx.fillStyle = "#ff6a88";
  ctx.arc(ghost.x * tileSize + 16, ghost.y * tileSize + 16, 12, Math.PI, 0);
  ctx.rect(ghost.x * tileSize + 4, ghost.y * tileSize + 16, 24, 12);
  ctx.fill();
}

function tick() {
  if (!gameOver) {
    move(pacman);
    pickGhostDirection();
    move(ghost);
    eatPellet();
    checkCollision();
    pacman.mouth += 0.45;
  }

  draw();
}

function restart() {
  score = 0;
  lives = 3;
  gameOver = false;
  pacman.x = 1;
  pacman.y = 1;
  pacman.dir = "right";
  ghost.x = 8;
  ghost.y = 8;
  ghost.dir = "left";
  scoreEl.textContent = "0";
  livesEl.textContent = "3";
  setStatus("Use os botões para mover o Pacman!");
  resetPellets();
}

document.querySelectorAll(".ctrl").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (gameOver) return;
    pacman.dir = btn.dataset.dir;
  });
});

window.addEventListener("keydown", (ev) => {
  const map = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right"
  };

  if (map[ev.key] && !gameOver) {
    pacman.dir = map[ev.key];
    ev.preventDefault();
  }
});

restartEl.addEventListener("click", restart);
restart();
setInterval(tick, 220);
