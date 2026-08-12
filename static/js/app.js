/* ==========================================================
   Furni Store — App JS: first-visit preloader + welcome
   overlay, scroll reveal, quantity steppers, OTP inputs,
   toasts.
   ========================================================== */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    initPreloaderAndWelcome();
    initScrollReveal();
    initQuantitySteppers();
    initAutoDismissAlerts();
    initOtpInputs();
  });

  // ---------- Preloader + Welcome overlay: only on the FIRST page of a browsing session ----------
  // Eligibility was already decided by a synchronous inline script in <head> (before paint),
  // which adds "preloader-active" / "welcome-eligible" classes only on the first page load
  // of the session. Here we just run the show/hide animation lifecycle.
  function initPreloaderAndWelcome() {
    var preloader = document.getElementById("preloader");
    var overlay = document.getElementById("welcomeOverlay");

    var preloaderEligible = preloader && preloader.classList.contains("preloader-active");
    var welcomeEligible = overlay && overlay.classList.contains("welcome-eligible");

    if (!preloaderEligible) {
      if (preloader) preloader.remove();
    } else {
      window.addEventListener("load", function () {
        setTimeout(function () {
          preloader.classList.add("preloader-hidden");
          setTimeout(function () { preloader.remove(); }, 600);
        }, 300);
      });
    }

    if (!welcomeEligible) {
      if (overlay) overlay.remove();
    } else {
      window.addEventListener("load", function () {
        setTimeout(function () {
          overlay.classList.add("welcome-show");
        }, 500);

        setTimeout(function () {
          overlay.classList.remove("welcome-show");
          overlay.classList.add("welcome-hide");
          setTimeout(function () { overlay.remove(); }, 800);
        }, 2600);
      });

      overlay.addEventListener("click", function () {
        overlay.classList.remove("welcome-show");
        overlay.classList.add("welcome-hide");
        setTimeout(function () { overlay.remove(); }, 800);
      });
    }
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

  // ---------- OTP input boxes: auto-advance, backspace, paste ----------
  function initOtpInputs() {
    var group = document.querySelector(".otp-input-group");
    if (!group) return;
    var inputs = Array.prototype.slice.call(group.querySelectorAll("input"));
    var hidden = document.getElementById("id_code");

    function syncHidden() {
      if (hidden) hidden.value = inputs.map(function (i) { return i.value; }).join("");
    }

    inputs.forEach(function (input, idx) {
      input.addEventListener("input", function () {
        input.value = input.value.replace(/[^0-9]/g, "").slice(0, 1);
        if (input.value && inputs[idx + 1]) inputs[idx + 1].focus();
        syncHidden();
      });
      input.addEventListener("keydown", function (e) {
        if (e.key === "Backspace" && !input.value && inputs[idx - 1]) {
          inputs[idx - 1].focus();
        }
      });
      input.addEventListener("paste", function (e) {
        var text = (e.clipboardData || window.clipboardData).getData("text").replace(/[^0-9]/g, "");
        if (!text) return;
        e.preventDefault();
        text.split("").forEach(function (ch, i) {
          if (inputs[i]) inputs[i].value = ch;
        });
        syncHidden();
        var next = inputs[Math.min(text.length, inputs.length - 1)];
        if (next) next.focus();
      });
    });

    if (inputs[0]) inputs[0].focus();
  }
})();
