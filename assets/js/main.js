/* ============================================================
   grosir.in — shared site behaviour
   Custom cursor, scroll reveal, mobile nav, FAQ accordion,
   product quantity/WhatsApp quote builder, catalog filtering.
   ============================================================ */
(function () {
  "use strict";

  /* ---- CONFIG: update these for the real store ---- */
  window.GROSIRIN_CONFIG = {
    whatsappNumber: "6281234567890", // TODO: ganti dengan nomor WhatsApp bisnis Anda (format 62xxxxxxxxxx)
    brandName: "grosir.in"
  };

  document.addEventListener("DOMContentLoaded", init);

  function init() {
    document.body.classList.add("loaded");
    setupCursor();
    setupScrollProgress();
    setupNav();
    setupReveal();
    setupFaq();
    setupQtyStepper();
    setupFilterChips();
    setupContactForm();
    setupDragScroll();
  }

  /* ---------------- custom cursor ---------------- */
  function setupCursor() {
    var isPointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (!isPointer) return;
    document.documentElement.classList.add("has-cursor");

    var cursor = document.createElement("div");
    cursor.className = "cursor";
    cursor.id = "cursor";
    var dot = document.createElement("div");
    dot.className = "cursor-dot";
    dot.id = "cursor-dot";
    document.body.appendChild(cursor);
    document.body.appendChild(dot);

    var mx = 0, my = 0, cx = 0, cy = 0;
    window.addEventListener("mousemove", function (e) {
      mx = e.clientX; my = e.clientY;
      dot.style.left = mx + "px";
      dot.style.top = my + "px";
    });
    (function raf() {
      cx += (mx - cx) * 0.18;
      cy += (my - cy) * 0.18;
      cursor.style.left = cx + "px";
      cursor.style.top = cy + "px";
      requestAnimationFrame(raf);
    })();

    var hoverables = "a, button, .filter-chip, .faq-q, input, textarea, select, .pd-thumb, .qty-stepper button";
    document.addEventListener("mouseover", function (e) {
      if (e.target.closest(".scroll-row")) return; // drag-scroll rows use their own grab/grabbing state
      if (e.target.closest(hoverables)) cursor.classList.add("hover");
    });
    document.addEventListener("mouseout", function (e) {
      if (e.target.closest(".scroll-row")) return;
      if (e.target.closest(hoverables)) cursor.classList.remove("hover");
    });
    document.addEventListener("mousedown", function () { cursor.classList.add("click"); });
    document.addEventListener("mouseup", function () { cursor.classList.remove("click"); });
  }

  /* ---------------- click-and-drag sidescroll ---------------- */
  function setupDragScroll() {
    var rows = document.querySelectorAll(".scroll-row");
    if (!rows.length) return;
    var cursorEl = document.getElementById("cursor");

    rows.forEach(function (row) {
      var isDown = false, startX = 0, startScroll = 0, moved = false;

      row.addEventListener("mousedown", function (e) {
        isDown = true;
        moved = false;
        startX = e.pageX;
        startScroll = row.scrollLeft;
        row.classList.add("dragging");
        if (cursorEl) { cursorEl.classList.remove("grab"); cursorEl.classList.add("grabbing"); }
        e.preventDefault(); // avoid text selection / native image drag while dragging
      });

      window.addEventListener("mousemove", function (e) {
        if (!isDown) return;
        var delta = e.pageX - startX;
        if (Math.abs(delta) > 4) moved = true;
        row.scrollLeft = startScroll - delta;
      });

      window.addEventListener("mouseup", function () {
        if (!isDown) return;
        isDown = false;
        row.classList.remove("dragging");
        if (cursorEl) {
          cursorEl.classList.remove("grabbing");
          if (row.matches(":hover")) cursorEl.classList.add("grab");
        }
      });

      // If the mouse actually moved (a drag, not a click), swallow the click
      // so releasing over a card doesn't accidentally navigate to it.
      row.addEventListener("click", function (e) {
        if (moved) { e.preventDefault(); e.stopPropagation(); }
      }, true);

      row.querySelectorAll("img").forEach(function (img) {
        img.addEventListener("dragstart", function (e) { e.preventDefault(); });
      });

      row.addEventListener("mouseenter", function () {
        if (!isDown && cursorEl) cursorEl.classList.add("grab");
      });
      row.addEventListener("mouseleave", function () {
        if (cursorEl) cursorEl.classList.remove("grab");
      });
    });
  }

  /* ---------------- scroll progress + nav shadow ---------------- */
  function setupScrollProgress() {
    var bar = document.getElementById("scroll-progress");
    var nav = document.getElementById("nav");
    if (nav) requestAnimationFrame(function () { nav.classList.add("ready"); });
    window.addEventListener("scroll", function () {
      var h = document.documentElement;
      var scrolled = h.scrollTop / (h.scrollHeight - h.clientHeight || 1);
      if (bar) bar.style.transform = "scaleX(" + scrolled + ")";
      if (nav) nav.classList.toggle("scrolled", h.scrollTop > 8);
    }, { passive: true });
  }

  /* ---------------- mobile nav ---------------- */
  function setupNav() {
    var toggle = document.getElementById("nav-toggle");
    var links = document.getElementById("nav-links");
    if (!toggle || !links) return;
    toggle.addEventListener("click", function () {
      toggle.classList.toggle("open");
      links.classList.toggle("open");
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        toggle.classList.remove("open");
        links.classList.remove("open");
      });
    });
  }

  /* ---------------- scroll reveal ---------------- */
  function setupReveal() {
    var els = document.querySelectorAll(".reveal");
    if (!els.length) return;
    if (!("IntersectionObserver" in window)) {
      els.forEach(function (el) { el.classList.add("in-view"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ---------------- FAQ accordion ---------------- */
  function setupFaq() {
    document.querySelectorAll(".faq-item").forEach(function (item) {
      var q = item.querySelector(".faq-q");
      var a = item.querySelector(".faq-a");
      if (!q || !a) return;
      q.addEventListener("click", function () {
        var isOpen = item.classList.contains("open");
        document.querySelectorAll(".faq-item.open").forEach(function (o) {
          if (o !== item) {
            o.classList.remove("open");
            o.querySelector(".faq-a").style.maxHeight = null;
          }
        });
        item.classList.toggle("open", !isOpen);
        a.style.maxHeight = !isOpen ? a.scrollHeight + "px" : null;
      });
    });
  }

  /* ---------------- product quantity + WhatsApp quote ---------------- */
  function formatIDR(n) {
    return "Rp " + Math.round(n).toLocaleString("id-ID");
  }

  function waLink(message) {
    var num = window.GROSIRIN_CONFIG.whatsappNumber;
    return "https://wa.me/" + num + "?text=" + encodeURIComponent(message);
  }
  window.GROSIRIN_waLink = waLink;

  function setupQtyStepper() {
    var box = document.querySelector("[data-product]");
    if (!box) return;
    var productName = box.getAttribute("data-product");
    var tiers = JSON.parse(box.getAttribute("data-tiers") || "[]"); // [{min, price}] — active tiers, swapped by variant selection
    var moq = parseInt(box.getAttribute("data-moq") || "10", 10);
    var qtyStep = 10;

    // Optional Warna/Ukuran variant pricing: {colors:[...], options:[{warna,ukuran,priceTiers}]}
    var variantsRaw = box.getAttribute("data-variants");
    var variants = variantsRaw ? JSON.parse(variantsRaw) : null;
    var warnaSelect = document.getElementById("pd-warna-select");
    var ukuranSelect = document.getElementById("pd-ukuran-select");
    var tierBody = document.querySelector(".tier-table tbody");

    var input = box.querySelector(".qty-input");
    var minus = box.querySelector(".qty-minus");
    var plus = box.querySelector(".qty-plus");
    var estOut = box.querySelector(".qty-est-value");
    var priceOut = box.querySelector(".qty-est-unit");
    var waBtn = box.querySelector(".qty-wa-btn");

    function optionsForColor(color) {
      return variants.options.filter(function (o) { return o.warna === color; });
    }

    function currentVariant() {
      if (!variants) return null;
      var color = warnaSelect ? warnaSelect.value : variants.colors[0];
      var opts = optionsForColor(color);
      var size = ukuranSelect ? ukuranSelect.value : null;
      var match = null;
      opts.forEach(function (o) { if (o.ukuran === size) match = o; });
      return match || opts[0] || null;
    }

    // Rebuild the Ukuran dropdown to only the sizes available for the
    // currently-selected Warna (different colors can have different size
    // ranges, matching the vendor's real stock).
    function refreshUkuranOptions() {
      if (!variants || !warnaSelect || !ukuranSelect) return;
      var opts = optionsForColor(warnaSelect.value);
      ukuranSelect.innerHTML = opts.map(function (o) {
        return '<option value="' + o.ukuran + '">' + o.ukuran + '</option>';
      }).join("");
    }

    function renderTierTable(t) {
      if (!tierBody) return;
      tierBody.innerHTML = t.map(function (row) {
        return "<tr><td>" + row.min + "+ pcs</td><td class=\"price\">" + formatIDR(row.price) + "/pcs</td></tr>";
      }).join("");
    }

    function priceFor(qty) {
      var applicable = tiers[0];
      tiers.forEach(function (t) { if (qty >= t.min) applicable = t; });
      return applicable ? applicable.price : tiers.length ? tiers[tiers.length - 1].price : 0;
    }

    function update() {
      var qty = Math.max(moq, parseInt(input.value, 10) || moq);
      input.value = qty;
      var unit = priceFor(qty);
      var total = unit * qty;
      if (priceOut) priceOut.textContent = formatIDR(unit) + " / pcs";
      if (estOut) estOut.textContent = formatIDR(total);
      if (waBtn) {
        var variant = currentVariant();
        var variantLines = variant ? ("Warna: " + variant.warna + "\nUkuran: " + variant.ukuran + "\n") : "";
        var msg = "Halo grosir.in, saya ingin request quote untuk:\n" +
          "Produk: " + productName + "\n" +
          variantLines +
          "Jumlah: " + qty + " pcs\n" +
          "Estimasi harga: " + formatIDR(unit) + "/pcs (total " + formatIDR(total) + ")\n" +
          "Mohon info lebih lanjut mengenai desain/custom print. Terima kasih.";
        waBtn.href = waLink(msg);
      }
    }

    // When Warna/Ukuran changes, swap the active price tiers to match that
    // combination's real vendor-priced tier table, then recompute everything.
    function applyVariant() {
      var variant = currentVariant();
      if (variant) {
        tiers = variant.priceTiers;
        renderTierTable(tiers);
      }
      update();
    }

    if (variants && warnaSelect) {
      warnaSelect.addEventListener("change", function () {
        refreshUkuranOptions();
        applyVariant();
      });
    }
    if (variants && ukuranSelect) {
      ukuranSelect.addEventListener("change", applyVariant);
    }

    // Let a click anywhere on the Warna/Ukuran card (its label text, its
    // padding — not just the visible value text) open the dropdown, on top
    // of the <label for> association which already focuses it. Feature
    // detected: where showPicker() isn't supported, the click still focuses
    // the select via the native label association, same as before.
    box.querySelectorAll(".pd-spec-select").forEach(function (wrap) {
      var select = wrap.querySelector("select");
      if (!select || typeof select.showPicker !== "function") return;
      wrap.addEventListener("click", function (e) {
        if (e.target === select) return; // clicking the select itself already opens it natively
        try { select.showPicker(); } catch (err) { /* requires direct user activation in some browsers — ignore */ }
      });
    });

    if (minus) minus.addEventListener("click", function () {
      input.value = Math.max(moq, (parseInt(input.value, 10) || moq) - qtyStep);
      update();
    });
    if (plus) plus.addEventListener("click", function () {
      input.value = (parseInt(input.value, 10) || moq) + qtyStep;
      update();
    });
    if (input) input.addEventListener("input", update);
    update();

    /* gallery thumbnails */
    var main = document.querySelector(".pd-gallery-main img");
    document.querySelectorAll(".pd-thumb").forEach(function (thumb) {
      thumb.addEventListener("click", function () {
        document.querySelectorAll(".pd-thumb").forEach(function (t) { t.classList.remove("active"); });
        thumb.classList.add("active");
        if (main) main.src = thumb.querySelector("img").src;
      });
    });
  }

  /* ---------------- catalog filter chips ---------------- */
  function setupFilterChips() {
    var bar = document.querySelector(".filter-bar");
    if (!bar) return;
    var chips = bar.querySelectorAll(".filter-chip");
    var cards = document.querySelectorAll(".product-card[data-category]");

    function applyFilter(cat) {
      chips.forEach(function (c) { c.classList.toggle("active", c.getAttribute("data-filter") === cat); });
      cards.forEach(function (card) {
        var show = cat === "all" || card.getAttribute("data-category") === cat;
        card.style.display = show ? "" : "none";
      });
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        applyFilter(chip.getAttribute("data-filter"));
      });
    });

    // Allow linking straight into a filtered view, e.g. katalog.html#spunbond
    var hash = (window.location.hash || "").replace("#", "");
    if (hash) {
      var match = bar.querySelector('.filter-chip[data-filter="' + hash + '"]');
      if (match) applyFilter(hash);
    }
  }

  /* ---------------- contact / quote form -> WhatsApp ---------------- */
  function setupContactForm() {
    var form = document.getElementById("quote-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var msg = "Halo grosir.in, saya ingin bertanya/request quote:\n" +
        "Nama: " + (data.get("nama") || "-") + "\n" +
        "Perusahaan: " + (data.get("perusahaan") || "-") + "\n" +
        "Kebutuhan: " + (data.get("kebutuhan") || "-") + "\n" +
        "Estimasi jumlah: " + (data.get("jumlah") || "-") + " pcs\n" +
        "Pesan: " + (data.get("pesan") || "-");
      window.open(waLink(msg), "_blank");
    });
  }
})();
