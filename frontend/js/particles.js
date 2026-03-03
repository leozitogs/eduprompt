/**
 * EduPrompt — Sistema de Partículas Animadas para Hero Section
 * Cria um background interativo com partículas conectadas por linhas.
 * 
 * Autor: Leonardo Gonçalves Sobral
 */

(function () {
  'use strict';

  const canvas = document.getElementById('heroCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height;
  let particles = [];
  let mouse = { x: null, y: null, radius: 150 };
  let animationId;

  // ─── Configuração ───
  const CONFIG = {
    particleCount: 80,
    particleMinSize: 1,
    particleMaxSize: 3,
    particleSpeed: 0.3,
    lineDistance: 140,
    lineWidth: 0.6,
    particleColor: '255, 244, 79',     // Lemon Yellow
    lineColor: '255, 244, 79',          // Lemon Yellow
    particleOpacity: 0.6,
    lineOpacity: 0.12,
    mouseInfluence: 0.02,
    responsive: true
  };

  // ─── Classe Partícula ───
  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.size = Math.random() * (CONFIG.particleMaxSize - CONFIG.particleMinSize) + CONFIG.particleMinSize;
      this.speedX = (Math.random() - 0.5) * CONFIG.particleSpeed * 2;
      this.speedY = (Math.random() - 0.5) * CONFIG.particleSpeed * 2;
      this.opacity = Math.random() * 0.5 + 0.3;
    }

    update() {
      // Movimento base
      this.x += this.speedX;
      this.y += this.speedY;

      // Interação com o mouse
      if (mouse.x !== null && mouse.y !== null) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < mouse.radius) {
          const force = (mouse.radius - dist) / mouse.radius;
          this.x -= dx * force * CONFIG.mouseInfluence;
          this.y -= dy * force * CONFIG.mouseInfluence;
        }
      }

      // Wrap around nas bordas
      if (this.x < -10) this.x = width + 10;
      if (this.x > width + 10) this.x = -10;
      if (this.y < -10) this.y = height + 10;
      if (this.y > height + 10) this.y = -10;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${CONFIG.particleColor}, ${this.opacity * CONFIG.particleOpacity})`;
      ctx.fill();
    }
  }

  // ─── Inicialização ───
  function init() {
    resize();
    particles = [];

    // Ajustar quantidade de partículas para telas menores
    let count = CONFIG.particleCount;
    if (width < 768) count = Math.floor(count * 0.5);
    else if (width < 1200) count = Math.floor(count * 0.75);

    for (let i = 0; i < count; i++) {
      particles.push(new Particle());
    }
  }

  function resize() {
    width = canvas.width = canvas.offsetWidth;
    height = canvas.height = canvas.offsetHeight;
  }

  // ─── Desenhar conexões entre partículas ───
  function drawConnections() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONFIG.lineDistance) {
          const opacity = (1 - dist / CONFIG.lineDistance) * CONFIG.lineOpacity;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(${CONFIG.lineColor}, ${opacity})`;
          ctx.lineWidth = CONFIG.lineWidth;
          ctx.stroke();
        }
      }
    }
  }

  // ─── Loop de animação ───
  function animate() {
    ctx.clearRect(0, 0, width, height);

    particles.forEach(p => {
      p.update();
      p.draw();
    });

    drawConnections();
    animationId = requestAnimationFrame(animate);
  }

  // ─── Event Listeners ───
  window.addEventListener('resize', () => {
    resize();
    // Recriar partículas se a mudança de tamanho for significativa
    if (Math.abs(canvas.width - width) > 100) {
      init();
    }
  });

  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });

  canvas.addEventListener('mouseleave', () => {
    mouse.x = null;
    mouse.y = null;
  });

  // Respeitar preferência de movimento reduzido
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (!prefersReducedMotion.matches) {
    init();
    animate();
  }

  prefersReducedMotion.addEventListener('change', (e) => {
    if (e.matches) {
      cancelAnimationFrame(animationId);
    } else {
      init();
      animate();
    }
  });
})();
