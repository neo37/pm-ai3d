// Institute of Design Thinking — UI behaviours
(function () {
  "use strict";

  // Mobile nav
  var toggle = document.getElementById("navToggle");
  var nav = document.getElementById("siteNav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.classList.toggle("open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("open");
        toggle.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Header shadow on scroll
  var header = document.getElementById("siteHeader");
  if (header) {
    var onScroll = function () {
      header.style.boxShadow =
        window.scrollY > 8 ? "0 6px 24px -14px rgba(13,24,38,.4)" : "none";
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Reveal on scroll — GSAP ScrollTrigger if available, else IntersectionObserver
  var reveals = document.querySelectorAll(".reveal");
  var hasGsap = typeof window.gsap !== "undefined" && typeof window.ScrollTrigger !== "undefined";

  if (hasGsap) {
    gsap.registerPlugin(ScrollTrigger);
    reveals.forEach(function (el) {
      el.classList.add("in"); // let GSAP own opacity/transform
      gsap.fromTo(
        el,
        { y: 34, autoAlpha: 0 },
        {
          y: 0, autoAlpha: 1, duration: 0.9, ease: "power3.out",
          scrollTrigger: { trigger: el, start: "top 86%" },
        }
      );
    });
    // Image scale-in for portfolio & gallery thumbs
    document.querySelectorAll(".proj-thumb img, .bento-img img, .gallery img").forEach(function (img) {
      gsap.fromTo(
        img,
        { scale: 1.14 },
        { scale: 1, duration: 1.2, ease: "power3.out",
          scrollTrigger: { trigger: img, start: "top 92%" } }
      );
    });
    // Word-by-word scrub reveal for elements marked data-scrub
    document.querySelectorAll("[data-scrub]").forEach(function (el) {
      var words = el.textContent.trim().split(/\s+/);
      el.innerHTML = words
        .map(function (w) { return '<span class="w" style="display:inline-block">' + w + "</span>"; })
        .join(" ");
      gsap.fromTo(
        el.querySelectorAll(".w"),
        { opacity: 0.16 },
        { opacity: 1, stagger: 0.06, ease: "none",
          scrollTrigger: { trigger: el, start: "top 80%", end: "bottom 55%", scrub: true } }
      );
    });
  } else if (reveals.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
        });
      },
      { threshold: 0.14 }
    );
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  // Count-up numbers ([data-count])
  document.querySelectorAll("[data-count]").forEach(function (el) {
    var target = parseFloat(el.getAttribute("data-count"));
    var suffix = el.getAttribute("data-suffix") || "";
    var run = function () {
      var start = null, dur = 1400;
      var tick = function (t) {
        if (!start) start = t;
        var p = Math.min((t - start) / dur, 1);
        var val = Math.floor((1 - Math.pow(1 - p, 3)) * target);
        el.textContent = val + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    if (hasGsap) {
      ScrollTrigger.create({ trigger: el, start: "top 90%", once: true, onEnter: run });
    } else if ("IntersectionObserver" in window) {
      var o = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { run(); o.unobserve(e.target); } });
      });
      o.observe(el);
    } else { run(); }
  });

  // Portfolio filters
  var filterBar = document.querySelector("[data-filters]");
  if (filterBar) {
    var cards = document.querySelectorAll("[data-cat]");
    filterBar.querySelectorAll("button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var cat = btn.getAttribute("data-filter");
        filterBar
          .querySelectorAll("button")
          .forEach(function (b) { b.classList.remove("active"); });
        btn.classList.add("active");
        cards.forEach(function (c) {
          var show = cat === "all" || c.getAttribute("data-cat") === cat;
          c.style.display = show ? "" : "none";
        });
      });
    });
  }
})();
