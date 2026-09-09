      (function () {
        let currentIndex = 0;
        const slides = document.querySelectorAll(".banner-slide");
        const dots = document.querySelectorAll(".dot");
        const prevBtn = document.getElementById("prevBtn");
        const nextBtn = document.getElementById("nextBtn");
        let autoPlayInterval;

        // Function to display the specified slide
        function showSlide(index) {
          // Normalize index
          if (index >= slides.length) index = 0;
          if (index < 0) index = slides.length - 1;

          currentIndex = index;

          // Update slides
          slides.forEach((slide, i) => {
            slide.classList.remove("active");
            if (i === currentIndex) {
              slide.classList.add("active");
            }
          });

          // Update indicator dots
          dots.forEach((dot, i) => {
            dot.classList.remove("active");
            if (i === currentIndex) {
              dot.classList.add("active");
            }
          });
        }

        // Function to go to next slide
        function nextSlide() {
          showSlide(currentIndex + 1);
        }

        // Function to go to previous slide
        function prevSlide() {
          showSlide(currentIndex - 1);
        }

        // Start autoplay (every 5 seconds)
        function startAutoPlay() {
          if (autoPlayInterval) clearInterval(autoPlayInterval);
          autoPlayInterval = setInterval(nextSlide, 5000);
        }

        // Stop autoplay (when user interacts with slider)
        function stopAutoPlay() {
          if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
            autoPlayInterval = null;
          }
        }

        // Button event handlers
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

        // Dot indicator event handlers
        dots.forEach((dot, index) => {
          dot.addEventListener("click", () => {
            stopAutoPlay();
            showSlide(index);
            startAutoPlay();
          });
        });

        // Initialize slider
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

      // ===========================================
      // 2. Floating particles starting from bottom of banner
      // ===========================================
      function createParticle() {
        var heroSection = document.querySelector(".hero");
        if (!heroSection) return;

        var particle = document.createElement("div");
        particle.classList.add("particle");

        // Random size between 2 and 7 pixels
        var size = Math.random() * 5 + 2;
        particle.style.width = size + "px";
        particle.style.height = size + "px";

        // Random horizontal position across banner width
        particle.style.left = Math.random() * 100 + "%";
        // Starts from bottom of banner
        particle.style.bottom = "0";

        // Random movement duration
        particle.style.animationDuration = Math.random() * 3 + 2 + "s";
        particle.style.animationDelay = Math.random() * 1 + "s";

        heroSection.appendChild(particle);

        // Remove particle after animation completes
        setTimeout(function () {
          if (particle && particle.remove) particle.remove();
        }, 5000);
      }

      // Create new particle every 250ms (for higher density)
      setInterval(createParticle, 250);

      // ===========================================
      // 3. Scroll Reveal Animation
      // ===========================================
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
    // ===========================================
// 4. 3D Magnetic Effect on Product Cards
// ===========================================
document.querySelectorAll('.product-card').forEach(card => {
  // Mouse move effect - creates 3D tilt and glow
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