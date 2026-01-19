import { useEffect, useRef } from "react";

export default function ParticleBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    let animationFrameId;
    let particles = [];
    const particleCount = 100;
    const colors = [
      "#95E913",
      "#549E06",
      "#C6F486",
      "#542C3C",
      "#9D6777",
      "#ADB5D6",
    ];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    class Particle {
      constructor() {
        this.reset(true);
      }

      reset(isInitial = false) {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;

        // Depth/Parallax logic
        this.size = Math.random() * 3 + 0.5;
        const speedMultiplier = this.size * 0.15;
        this.speedX = (Math.random() - 0.5) * speedMultiplier;
        this.speedY = (Math.random() - 0.5) * speedMultiplier;

        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.opacity = isInitial ? Math.random() * 0.5 : 0;
        this.fadeSpeed = 0.001 + Math.random() * 0.002;
        this.isFadingOut = false;

        // Organic wobble
        this.angle = Math.random() * Math.PI * 2;
        this.velocityVariation = Math.random() * 0.01;
      }

      update() {
        // Constant velocity (no friction)
        this.x += this.speedX;
        this.y += this.speedY;

        // Smooth wave motion
        this.angle += this.velocityVariation;
        this.x += Math.sin(this.angle) * 0.2;

        // Smooth fade lifecycle
        if (!this.isFadingOut) {
          this.opacity += this.fadeSpeed;
          if (this.opacity >= 0.6) this.isFadingOut = true;
        } else {
          this.opacity -= this.fadeSpeed;
          if (this.opacity <= 0) this.reset(false);
        }

        // Screen Wrap (keeps particles moving eternally)
        if (this.x < -10) this.x = canvas.width + 10;
        if (this.x > canvas.width + 10) this.x = -10;
        if (this.y < -10) this.y = canvas.height + 10;
        if (this.y > canvas.height + 10) this.y = -10;
      }

      draw() {
        ctx.save();
        ctx.globalAlpha = this.opacity;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = this.color;

        if (this.size > 2.5) {
          ctx.shadowBlur = 5;
          ctx.shadowColor = this.color;
        }

        ctx.fill();
        ctx.restore();
      }
    }

    const init = () => {
      resize();
      particles = Array.from({ length: particleCount }, () => new Particle());
    };

    const animate = () => {
      // Clear with transparent black to prevent ghosting while allowing background to show
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p) => {
        p.update();
        p.draw();
      });
      animationFrameId = requestAnimationFrame(animate);
    };

    window.addEventListener("resize", resize);
    init();
    animate();

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full"
      style={{
        zIndex: 0,
        pointerEvents: "none",
        background: "transparent",
      }}
    />
  );
}
