/* ==========================================================
   Furni Store — App JS: first-visit preloader + welcome
   overlay, scroll reveal, quantity steppers, toasts.
   (OTP input-box logic lives inline in verify_otp.html so it
   never depends on this file's load timing/caching.)
   ========================================================== */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    initPreloaderAndWelcome();
    initScrollReveal();
    initQuantitySteppers();
    initAutoDismissAlerts();
    initSearchSuggestions();
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

  // ---------- Live search suggestions (navbar search box) ----------
  function initSearchSuggestions() {
    var input = document.getElementById("navSearchInput");
    var box = document.getElementById("navSearchSuggestions");
    if (!input || !box) return;

    var debounceTimer = null;
    var activeIndex = -1;
    var currentItems = [];
    var currentRequest = null;

    function closeBox() {
      box.classList.remove("show");
      box.innerHTML = "";
      activeIndex = -1;
      currentItems = [];
    }

    function escapeHtml(str) {
      var div = document.createElement("div");
      div.textContent = str == null ? "" : String(str);
      return div.innerHTML;
    }

    function renderResults(results) {
      if (!results.length) {
        box.innerHTML = '<div class="search-suggestions-empty">No products found.</div>';
        box.classList.add("show");
        currentItems = [];
        return;
      }
      box.innerHTML = results.map(function (item) {
        var img = item.image ? '<img src="' + escapeHtml(item.image) + '" alt="">' : "";
        return (
          '<a href="' + escapeHtml(item.url) + '" class="search-suggestion-item">' +
            img +
            '<span class="name">' + escapeHtml(item.name) + '</span>' +
            '<span class="price">$' + escapeHtml(item.price) + '</span>' +
          '</a>'
        );
      }).join("");
      box.classList.add("show");
      currentItems = Array.prototype.slice.call(box.querySelectorAll(".search-suggestion-item"));
      activeIndex = -1;
    }

    input.addEventListener("input", function () {
      var query = input.value.trim();
      clearTimeout(debounceTimer);

      if (query.length < 2) {
        closeBox();
        return;
      }

      debounceTimer = setTimeout(function () {
        if (currentRequest) currentRequest.abort();
        var controller = new AbortController();
        currentRequest = controller;

        fetch("/shop/search-suggestions/?q=" + encodeURIComponent(query), { signal: controller.signal })
          .then(function (res) { return res.json(); })
          .then(function (data) { renderResults(data.results || []); })
          .catch(function (err) {
            if (err.name !== "AbortError") closeBox();
          });
      }, 250);
    });

    input.addEventListener("keydown", function (e) {
      if (!currentItems.length) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, currentItems.length - 1);
        highlightActive();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        highlightActive();
      } else if (e.key === "Enter" && activeIndex >= 0) {
        e.preventDefault();
        currentItems[activeIndex].click();
      } else if (e.key === "Escape") {
        closeBox();
      }
    });

    function highlightActive() {
      currentItems.forEach(function (item, idx) {
        item.classList.toggle("active", idx === activeIndex);
      });
      var active = currentItems[activeIndex];
      if (active && typeof active.scrollIntoView === "function") {
        active.scrollIntoView({ block: "nearest" });
      }
    }

    document.addEventListener("click", function (e) {
      if (!box.contains(e.target) && e.target !== input) closeBox();
    });
  }
})();
