/* ============================================================
   grosir.in — shared site behaviour
   Custom cursor, scroll reveal, mobile nav, FAQ accordion,
   product quantity/WhatsApp quote builder, catalog filtering,
   WhatsApp chat widget.
   ============================================================ */
(function () {
  "use strict";

  /* ---- CONFIG: update these for the real store ---- */
  window.GROSIRIN_CONFIG = {
    whatsappNumber: "6287714070404", // nomor WhatsApp bisnis grosir.in (format 62xxxxxxxxxx)
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
    setupWaWidget();
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
    setupDetailsFaq();
    openHashDetails();
    window.addEventListener("hashchange", openHashDetails);
  }

  /* Article FAQs and the price list's product rows are native <details> —
     they open and close without any JavaScript. This only adds the slide:
     the body's height (and opacity) animates open and shut instead of
     jumping. Reduced-motion users, and browsers without the Web Animations
     API, keep the instant native toggle. */
  function setupDetailsFaq() {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.querySelectorAll("details.faq-item, details.pl-acc").forEach(function (item) {
      var summary = item.querySelector("summary");
      var body = item.querySelector(".faq-answer, .pl-acc-body");
      if (!summary || !body || reduce || !body.animate) return;
      var anim = null;
      summary.addEventListener("click", function (e) {
        e.preventDefault();
        if (anim) anim.cancel();
        var closing = item.open;
        var start = closing ? body.offsetHeight : 0;
        if (!closing) item.open = true;             // render it so it can be measured
        var end = closing ? 0 : body.offsetHeight;
        item.classList.toggle("closing", closing);
        body.style.overflow = "hidden";
        anim = body.animate(
          [{ height: start + "px", opacity: closing ? 1 : 0 },
           { height: end + "px", opacity: closing ? 0 : 1 }],
          { duration: 380, easing: "cubic-bezier(.23,1,.32,1)" }
        );
        anim.onfinish = function () {
          if (closing) item.open = false;
          item.classList.remove("closing");
          body.style.overflow = "";
          anim = null;
        };
      });
    });
  }

  /* A link to a collapsed row (daftar-harga.html#blacu) opens it, so the
     visitor lands on the prices rather than on a closed heading. */
  function openHashDetails() {
    var id = location.hash ? decodeURIComponent(location.hash.slice(1)) : "";
    var el = id && document.getElementById(id);
    var d = el && (el.tagName === "DETAILS" ? el : el.closest("details"));
    if (!d || d.open) return;
    d.open = true;
    el.scrollIntoView();
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
    // data-moq is the SABLON minimum; data-min the polos minimum (1 for
    // products priced from the vendor list — plain bags have no minimum).
    var moq = parseInt(box.getAttribute("data-moq") || "10", 10);
    var minQty = parseInt(box.getAttribute("data-min") || String(moq), 10);
    var sablonSelect = document.getElementById("pd-sablon-select");

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
    // ranges, matching the vendor's real stock), keeping the chosen size if
    // the new colour has it.
    function refreshUkuranOptions() {
      if (!variants || !warnaSelect || !ukuranSelect) return;
      var opts = optionsForColor(warnaSelect.value);
      var keep = ukuranSelect.value;
      ukuranSelect.innerHTML = opts.map(function (o) {
        return '<option value="' + o.ukuran + '">' + o.ukuran + '</option>';
      }).join("");
      // Keep the chosen size when the new colour has it too.
      if (opts.some(function (o) { return o.ukuran === keep; })) ukuranSelect.value = keep;
    }

    // Mirrors build.py's tier_rows_html(): a tier below the sablon minimum is
    // polos-only and shown as a range ("1–9 pcs").
    function renderTierTable(t) {
      if (!tierBody) return;
      tierBody.innerHTML = t.map(function (row, i) {
        var next = t[i + 1];
        var label = (row.min < moq && next)
          ? row.min + "–" + (next.min - 1) + ' pcs <span class="tier-note">polos</span>'
          : row.min + "+ pcs";
        return "<tr><td>" + label + "</td><td class=\"price\">" + formatIDR(row.price) + "/pcs</td></tr>";
      }).join("");
    }

    function sablonOption() {
      if (!sablonSelect || !sablonSelect.value) return null;
      var opt = sablonSelect.options[sablonSelect.selectedIndex];
      return { price: parseInt(opt.getAttribute("data-price") || "0", 10),
               label: opt.textContent.split(" (+")[0] };
    }

    // Sublim only works on white bags: hide those choices for other colours,
    // and fall back to polos if the current choice stops being available.
    function filterSablonOptions() {
      if (!sablonSelect) return;
      var variant = currentVariant();
      var color = variant ? variant.warna : "";
      Array.prototype.forEach.call(sablonSelect.options, function (opt) {
        var colors = opt.getAttribute("data-colors");
        var ok = !colors || colors.split("|").indexOf(color) !== -1;
        opt.hidden = !ok;
        opt.disabled = !ok;
      });
      if (sablonSelect.selectedOptions.length && sablonSelect.selectedOptions[0].disabled) sablonSelect.value = "";
    }

    function currentMin() { return sablonOption() ? Math.max(moq, minQty) : minQty; }

    function priceFor(qty) {
      var applicable = tiers[0];
      tiers.forEach(function (t) { if (qty >= t.min) applicable = t; });
      return applicable ? applicable.price : tiers.length ? tiers[tiers.length - 1].price : 0;
    }

    // typing = true while the visitor is still typing: compute with the
    // clamped value but leave the field alone, so typing "25" isn't
    // snapped to the minimum after the "2".
    function update(typing) {
      var min = currentMin();
      var raw = parseInt(input.value, 10);
      var qty = Math.max(min, raw || min);
      if (!typing) input.value = qty;
      input.min = min;
      var sablon = sablonOption();
      var base = priceFor(qty);
      var unit = base + (sablon ? sablon.price : 0);
      var total = unit * qty;
      if (priceOut) {
        priceOut.textContent = sablon
          ? formatIDR(base) + " + sablon " + formatIDR(sablon.price) + " = " + formatIDR(unit) + " / pcs"
          : formatIDR(unit) + " / pcs (polos)";
        if (sablon && (raw || 0) < moq) priceOut.textContent += " · sablon minimal " + moq + " pcs";
      }
      if (estOut) estOut.textContent = formatIDR(total);
      if (waBtn) {
        var variant = currentVariant();
        var variantLines = variant ? ("Warna: " + variant.warna + "\nUkuran: " + variant.ukuran + "\n") : "";
        var msg = "Halo grosir.in, saya mau minta penawaran untuk:\n" +
          "Produk: " + productName + "\n" +
          variantLines +
          "Sablon: " + (sablon ? sablon.label : (sablonSelect ? "Polos (tanpa sablon)" : "...")) + "\n" +
          "Jumlah: " + qty + " pcs\n" +
          "Perkiraan harga: " + formatIDR(unit) + "/pcs (total " + formatIDR(total) + ")\n" +
          "Terima kasih.";
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
      filterSablonOptions();
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

    // Steps of 1 below 10 pcs (polos can be bought singly), 10 above —
    // and minus never jumps past 10 from above (15 → 10, not 5).
    if (minus) minus.addEventListener("click", function () {
      var q = parseInt(input.value, 10) || currentMin();
      input.value = Math.max(currentMin(), q <= 10 ? q - 1 : Math.max(10, q - 10));
      update();
    });
    if (plus) plus.addEventListener("click", function () {
      var q = parseInt(input.value, 10) || currentMin();
      input.value = q < 10 ? q + 1 : q + 10;
      update();
    });
    if (input) {
      input.addEventListener("input", function () { update(true); });
      input.addEventListener("change", function () { update(); });
    }
    if (sablonSelect) {
      sablonSelect.addEventListener("change", function () { update(); });
      filterSablonOptions();
    }
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
  /* ---------------- WhatsApp chat widget ----------------
     Progressive enhancement of the floating button. In the HTML it is a plain
     wa.me link, so it still works with JavaScript off; here it becomes a small
     card with topic shortcuts. Every shortcut is still just a wa.me link — the
     conversation lands in the ordinary WhatsApp Business app. No API, and no
     third-party script.

     The status line is computed from the real clock against the published
     operating hours. It is never a static "Online" badge: the site once had
     one, and it claimed to be online at 03:00 on a Sunday. */
  var WA_HOURS = { days: [1, 2, 3, 4, 5], open: 9 * 60, close: 17 * 60 };   // Senin–Jumat 09.00–17.00 WIB
  var HARI = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];

  function jakartaNow() {
    // WIB is UTC+7 all year — Indonesia has no daylight saving — so shifting
    // UTC is exact and does not depend on the visitor's own time zone.
    var d = new Date(Date.now() + 7 * 3600 * 1000);
    return { day: d.getUTCDay(), minutes: d.getUTCHours() * 60 + d.getUTCMinutes() };
  }
  function isWorkday(day) { return WA_HOURS.days.indexOf(day) !== -1; }
  function waStatus(now) {
    now = now || jakartaNow();
    if (isWorkday(now.day) && now.minutes >= WA_HOURS.open && now.minutes < WA_HOURS.close) {
      return { open: true, text: "Online · biasanya balas dalam 1 jam" };
    }
    var when;
    if (isWorkday(now.day) && now.minutes < WA_HOURS.open) {
      when = "hari ini mulai pukul 09.00 WIB";
    } else {
      for (var k = 1; k <= 7; k++) {
        var day = (now.day + k) % 7;
        if (isWorkday(day)) { when = (k === 1 ? "besok" : HARI[day]) + " pukul 09.00 WIB"; break; }
      }
    }
    return { open: false, text: "Di luar jam kerja · kami balas " + when };
  }
  window.GROSIRIN_waStatus = waStatus;   // exposed for testing the hours logic

  function setupWaWidget() {
    var btn = document.querySelector(".wa-float");
    if (!btn) return;

    // On a product page the quote shortcut names the product being viewed.
    var productBox = document.querySelector("[data-product]");
    var product = productBox ? productBox.getAttribute("data-product") : "";
    var topics = [
      { label: "Minta penawaran harga",
        msg: product ? "Halo grosir.in, saya mau minta penawaran harga untuk " + product + "."
                     : "Halo grosir.in, saya mau minta penawaran harga totebag custom." },
      { label: "Pesan totebag polos",
        msg: "Halo grosir.in, saya mau pesan totebag polos (tanpa sablon)" +
             (product ? " — " + product : "") + ". Jumlahnya sekitar ... pcs." },
      { label: "Tanya soal bahan",
        msg: "Halo grosir.in, saya mau tanya soal pilihan bahan totebag." },
      { label: "Cek stok & waktu produksi",
        msg: "Halo grosir.in, saya mau cek stok dan perkiraan waktu produksi." }
    ];

    var card = document.createElement("div");
    card.className = "wa-card";
    card.id = "wa-card";
    card.setAttribute("role", "dialog");
    card.setAttribute("aria-labelledby", "wa-card-title");
    card.hidden = true;

    var head = document.createElement("div");
    head.className = "wa-card-head";
    var title = document.createElement("div");
    title.className = "wa-card-title";
    title.id = "wa-card-title";
    title.textContent = "grosir.in";
    var status = document.createElement("div");
    status.className = "wa-card-status";
    var dot = document.createElement("span");
    dot.className = "wa-dot";
    var statusText = document.createElement("span");
    status.appendChild(dot); status.appendChild(statusText);
    var close = document.createElement("button");
    close.type = "button";
    close.className = "wa-card-close";
    close.setAttribute("aria-label", "Tutup");
    close.textContent = "×";
    head.appendChild(title); head.appendChild(status); head.appendChild(close);

    var body = document.createElement("div");
    body.className = "wa-card-body";
    var bubble = document.createElement("p");
    bubble.className = "wa-bubble";
    bubble.textContent = "Halo kak! Ada yang bisa kami bantu? Pilih topik di bawah, pesannya langsung terbuka di WhatsApp.";
    body.appendChild(bubble);
    var links = [];
    topics.forEach(function (t) {
      var a = document.createElement("a");
      a.className = "wa-topic";
      a.href = waLink(t.msg);
      a.target = "_blank";
      a.rel = "noopener";
      a.textContent = t.label;
      a.addEventListener("click", function () { hide(false); });
      body.appendChild(a);
      links.push(a);
    });

    var foot = document.createElement("div");
    foot.className = "wa-card-foot";
    foot.textContent = "Jam kerja: Senin–Jumat, 09.00–17.00 WIB";

    card.appendChild(head); card.appendChild(body); card.appendChild(foot);
    document.body.appendChild(card);

    btn.setAttribute("aria-haspopup", "dialog");
    btn.setAttribute("aria-controls", "wa-card");
    btn.setAttribute("aria-expanded", "false");
    btn.setAttribute("aria-label", "Buka chat WhatsApp");

    var timer = null;
    function refresh() {
      var st = waStatus();
      statusText.textContent = st.text;
      card.classList.toggle("is-open", st.open);
    }
    function show() {
      refresh();
      // A tab left open across 17.00 should not keep saying Online.
      timer = setInterval(refresh, 60 * 1000);
      card.hidden = false;
      btn.setAttribute("aria-expanded", "true");
      requestAnimationFrame(function () { card.classList.add("show"); });
      links[0].focus({ preventScroll: true });
    }
    function hide(returnFocus) {
      if (card.hidden) return;
      clearInterval(timer); timer = null;
      card.classList.remove("show");
      card.hidden = true;
      btn.setAttribute("aria-expanded", "false");
      if (returnFocus) btn.focus({ preventScroll: true });
    }

    btn.addEventListener("click", function (e) {
      // Let ctrl/cmd/shift/middle-click keep their normal open-in-new-tab meaning.
      if (e.ctrlKey || e.metaKey || e.shiftKey || e.button !== 0) return;
      e.preventDefault();
      if (card.hidden) show(); else hide(true);
    });
    close.addEventListener("click", function () { hide(true); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !card.hidden) hide(true);
    });
    document.addEventListener("click", function (e) {
      if (!card.hidden && !card.contains(e.target) && !btn.contains(e.target)) hide(false);
    });
  }

  function setupContactForm() {
    var form = document.getElementById("quote-form");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var data = new FormData(form);
      var msg = "Halo grosir.in, saya mau minta penawaran:\n" +
        "Nama: " + (data.get("nama") || "-") + "\n" +
        "Perusahaan/acara: " + (data.get("perusahaan") || "-") + "\n" +
        "Bahan: " + (data.get("kebutuhan") || "-") + "\n" +
        "Polos/sablon: " + (data.get("jenis") || "-") + "\n" +
        "Perkiraan jumlah: " + (data.get("jumlah") || "-") + " pcs\n" +
        "Pesan: " + (data.get("pesan") || "-");
      window.open(waLink(msg), "_blank");
    });
  }
})();
