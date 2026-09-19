      (function () {
        let currentIndex = 0;
        const slides = document.querySelectorAll(".banner-slide");
        const dots = document.querySelectorAll(".dot");
        const prevBtn = document.getElementById("prevBtn");
        const nextBtn = document.getElementById("nextBtn");
        let autoPlayInterval;

        function showSlide(index) {
          if (index >= slides.length) index = 0;
          if (index < 0) index = slides.length - 1;

          currentIndex = index;

          slides.forEach((slide, i) => {
            slide.classList.remove("active");
            if (i === currentIndex) {
              slide.classList.add("active");
            }
          });

          dots.forEach((dot, i) => {
            dot.classList.remove("active");
            if (i === currentIndex) {
              dot.classList.add("active");
            }
          });
        }

        function nextSlide() {
          showSlide(currentIndex + 1);
        }

        function prevSlide() {
          showSlide(currentIndex - 1);
        }

        function startAutoPlay() {
          if (autoPlayInterval) clearInterval(autoPlayInterval);
          autoPlayInterval = setInterval(nextSlide, 5000);
        }

        function stopAutoPlay() {
          if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            autoPlayInterval = null;
          }
        }

        if (prevBtn) {
          prevBtn.addEventListener("click", () => {
            stopAutoPlay();
            prevSlide();
            startAutoPlay();
          });
        }

        if (nextBtn) {
          nextBtn.addEventListener("click", () => {
            stopAutoPlay();
            nextSlide();
            startAutoPlay();
          });
        }

        dots.forEach((dot, index) => {
          dot.addEventListener("click", () => {
            stopAutoPlay();
            showSlide(index);
            startAutoPlay();
          });
        });

        if (slides.length > 0) {
          showSlide(0);
          startAutoPlay();
        }
      })();

       var hero = document.getElementById("heroSection");
      if (hero) {
        hero.addEventListener("mousemove", function (e) {
          var rect = hero.getBoundingClientRect();
          var x = ((e.clientX - rect.left) / rect.width) * 100;
          var y = ((e.clientY - rect.top) / rect.height) * 100;
          hero.style.setProperty("--mouse-x", x + "%");
          hero.style.setProperty("--mouse-y", y + "%");
        });
      }

      function createParticle() {
        var heroSection = document.querySelector(".hero");
        if (!heroSection) return;

        var particle = document.createElement("div");
        particle.classList.add("particle");

        var size = Math.random() * 5 + 2;
        particle.style.width = size + "px";
        particle.style.height = size + "px";

        particle.style.left = Math.random() * 100 + "%";
        particle.style.bottom = "0";

        particle.style.animationDuration = Math.random() * 3 + 2 + "s";
        particle.style.animationDelay = Math.random() * 1 + "s";

        heroSection.appendChild(particle);

        setTimeout(function () {
          if (particle && particle.remove) particle.remove();
        }, 5000);
      }

      setInterval(createParticle, 250);

      var revealElements = document.querySelectorAll(".scroll-reveal");

      function checkReveal() {
        for (var i = 0; i < revealElements.length; i++) {
          var el = revealElements[i];
          var rect = el.getBoundingClientRect();
          if (rect.top < window.innerHeight - 100) {
            el.classList.add("revealed");
          }
        }
      }

      window.addEventListener("scroll", checkReveal);
      checkReveal();
document.querySelectorAll('.product-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;

    const rotateY = (x - 0.5) * 15;
    const rotateX = (y - 0.5) * -15;

    const glowX = (x - 0.5) * 100;
    const glowY = (y - 0.5) * 100;

    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px)`;
    card.style.transition = 'transform 0.05s linear';

    card.style.setProperty('--glow-x', `${x * 100}%`);
    card.style.setProperty('--glow-y', `${y * 100}%`);

    card.style.boxShadow = `${glowX * 0.5}px ${glowY * 0.5}px 40px rgba(193, 18, 31, 0.3)`;
    card.style.borderColor = '#c1121f';
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
    card.style.transition = 'transform 0.4s cubic-bezier(0.2, 0.9, 0.4, 1.1)';
    card.style.boxShadow = 'none';
    card.style.borderColor = 'rgba(255, 255, 255, 0.05)';
  });
});