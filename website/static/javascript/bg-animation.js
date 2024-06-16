const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");
const branding = `rgba(204, 153, 51, ${Math.random() * 0.4 + 0.1})`;
const shadow = `rgba(204, 153, 10, 1)`
const particles = [];
const particleCount = 100;

let w = (canvas.width = innerWidth);
let h = (canvas.height = innerHeight);

function resize() {
  w = canvas.width = innerWidth;
  h = canvas.height = innerHeight;
}

window.addEventListener("resize", resize);

class Particle {
  constructor() {
    this.x = Math.random() * w;
    this.y = Math.random() * h;
    this.size = Math.random() * 5 + 1;
    this.speedX = Math.random() - 0.3;
    this.speedY = Math.random() - 0.3;
    this.color = branding;
    this.shadowColor = shadow;
    this.shadowBlur = 10;
  }

  update() {
    this.x += this.speedX;
    this.y += this.speedY;
    if (this.x > w || this.x < 0) this.speedX *= -1;
    if (this.y > h || this.y < 0) this.speedY *= -1;
  }

  draw() {
    ctx.fillStyle = this.color;
    ctx.shadowBlur = this.shadowBlur;
    ctx.shadowColor = this.shadowColor;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.fill();
  }
}

function init() {
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }
}

function animate() {
  ctx.clearRect(0, 0, w, h);
  particles.forEach((particle) => {
    particle.update();
    particle.draw();
  });
  requestAnimationFrame(animate);
}

init();
animate();
