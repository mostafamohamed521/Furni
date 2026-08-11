/* ==========================================================
   Furni Store — App JS: preloader, welcome overlay,
   scroll reveal, quantity steppers, wishlist ajax, toasts.
   ========================================================== */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    initPreloader();
    initWelcomeOverlay();
    initScrollReveal();
    initQuantitySteppers();
    initAutoDismissAlerts();
  });

  // ---------- Preloader ----------
  function initPreloader() {
    var preloader = document.getElementById("preloader");
    if (!preloader) return;
    window.addEventListener("load", function () {
      setTimeout(function () {
        preloader.classList.add("preloader-hidden");
        document.body.classList.remove("furni-loading");
      }, 350);
    });
  }

  // ---------- Welcome overlay (first visit of the browser session) ----------
  function initWelcomeOverlay() {
    var overlay = document.getElementById("welcomeOverlay");
    if (!overlay) return;

    var seen = sessionStorage.getItem("furni_welcome_seen");
    if (seen) {
      overlay.remove();
      return;
    }

    window.addEventListener("load", function () {
      setTimeout(function () {
        overlay.classList.add("welcome-show");
      }, 550);

      setTimeout(function () {
        overlay.classList.remove("welcome-show");
        overlay.classList.add("welcome-hide");
        sessionStorage.setItem("furni_welcome_seen", "1");
        setTimeout(function () { overlay.remove(); }, 800);
      }, 2600);
    });

    overlay.addEventListener("click", function () {
      overlay.classList.remove("welcome-show");
      overlay.classList.add("welcome-hide");
      sessionStorage.setItem("furni_welcome_seen", "1");
      setTimeout(function () { overlay.remove(); }, 800);
    });
  }

  // ---------- Scroll reveal ----------
  function initScrollReveal() {
    var items = document.querySelectorAll(".reveal-up");
    if (!items.length) return;

    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("revealed"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("revealed");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    items.forEach(function (el) { observer.observe(el); });
  }

  // ---------- Quantity steppers (cart / product detail) ----------
  function initQuantitySteppers() {
    document.querySelectorAll(".quantity-container").forEach(function (wrap) {
      var input = wrap.querySelector(".quantity-amount");
      var decrease = wrap.querySelector(".decrease");
      var increase = wrap.querySelector(".increase");
      if (!input) return;

      var max = parseInt(input.getAttribute("max") || "99", 10);

      if (decrease) {
        decrease.addEventListener("click", function () {
          var val = parseInt(input.value || "1", 10);
          if (val > 1) input.value = val - 1;
          input.dispatchEvent(new Event("change"));
        });
      }
      if (increase) {
        increase.addEventListener("click", function () {
          var val = parseInt(input.value || "1", 10);
          if (val < max) input.value = val + 1;
          input.dispatchEvent(new Event("change"));
        });
      }
    });
  }

  // ---------- Auto-dismiss alerts ----------
  function initAutoDismissAlerts() {
    document.querySelectorAll(".alert-dismissible").forEach(function (alertEl) {
      setTimeout(function () {
        if (window.bootstrap && bootstrap.Alert) {
          var instance = bootstrap.Alert.getOrCreateInstance(alertEl);
          instance.close();
        } else {
          alertEl.remove();
        }
      }, 4500);
    });
  }
})();
