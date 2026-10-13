(function () {
  // Mobile menu
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    });
  }

  // Footer year
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  // Show a form error passed back by contact.php (?error=...)
  var params = new URLSearchParams(window.location.search);
  var err = params.get('error');
  var box = document.getElementById('form-error');
  if (err && box) {
    var messages = {
      missing: 'Add your name and a phone number or email so we can reach you.',
      email: 'That email address doesn’t look right. Check it and send again.',
      send: 'Your request didn’t go through. Call us at 808.232.9000 or email contact@vacations4less.us.'
    };
    box.textContent = messages[err] || messages.send;
    box.hidden = false;
  }

  // Newsletter confirmation on the thank-you page
  if (window.location.hash === '#subscribed') {
    var h = document.querySelector('.page-head h1');
    var p = document.querySelector('.page-head p');
    if (h) h.textContent = 'You\u2019re on the list';
    if (p) p.textContent = 'Thanks for signing up. We\u2019ll email you travel deals and tips now and then.';
  }

  // Prefill destination from a destination card (?dest=Maui%2C%20Hawaii)
  var dest = params.get('dest');
  var destInput = document.getElementById('c-dest');
  if (dest && destInput && !destInput.value) {
    destInput.value = dest.slice(0, 120);
  }

  // Blog gallery lightbox
  var box2 = document.querySelector('.lightbox');
  if (box2 && typeof box2.showModal === 'function') {
    var lbImg = box2.querySelector('img');
    var lbCap = box2.querySelector('.lightbox-caption');
    document.querySelectorAll('.gallery a').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var thumb = a.querySelector('img');
        lbImg.src = a.href;
        lbImg.alt = thumb ? thumb.alt : '';
        lbCap.textContent = thumb ? thumb.alt : '';
        box2.showModal();
      });
    });
    box2.addEventListener('click', function (e) { if (e.target === box2) box2.close(); });
  }

  // Hero slider
  var slider = document.querySelector('.hero-slider');
  if (slider) {
    var SLIDE_MS = 6500;
    var media = slider.querySelectorAll('.slide-media');
    var copies = slider.querySelectorAll('.slide-copy');
    var dots = slider.querySelectorAll('.slider-dot');
    var pauseBtn = slider.querySelector('.slider-pause');
    var live = slider.querySelector('.slide-copies');
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var current = 0, timer = null, userPaused = reduce, hoverPaused = false;
    slider.style.setProperty('--slide-ms', SLIDE_MS + 'ms');

    var load = function (i) {
      var img = media[i] && media[i].querySelector('img[data-src]');
      if (!img) return;
      if (img.dataset.srcset) img.srcset = img.dataset.srcset;
      img.src = img.dataset.src;
      img.removeAttribute('data-src');
      img.removeAttribute('data-srcset');
    };

    var show = function (i) {
      var n = media.length;
      i = (i + n) % n;
      load(i);
      load((i + 1) % n);
      [media, copies, dots].forEach(function (list) {
        list.forEach(function (el, k) { el.classList.toggle('is-active', k === i); });
      });
      copies.forEach(function (el, k) {
        if (k === i) el.removeAttribute('aria-hidden'); else el.setAttribute('aria-hidden', 'true');
      });
      dots.forEach(function (el, k) {
        if (k === i) el.setAttribute('aria-current', 'true'); else el.removeAttribute('aria-current');
      });
      current = i;
    };

    // The progress bar under the active dot runs in step with the timer
    var restartBar = function () {
      var bar = dots[current] && dots[current].querySelector('span');
      if (!bar) return;
      bar.classList.remove('run');
      void bar.offsetWidth;
      bar.classList.add('run');
    };

    var playing = function () { return !userPaused && !hoverPaused && !document.hidden; };
    var schedule = function () {
      clearTimeout(timer);
      slider.classList.toggle('is-playing', !userPaused);
      slider.classList.toggle('is-paused', userPaused || hoverPaused);
      live.setAttribute('aria-live', userPaused ? 'polite' : 'off');
      if (playing()) {
        restartBar();
        timer = setTimeout(function () { show(current + 1); schedule(); }, SLIDE_MS);
      }
    };
    var go = function (i) { show(i); schedule(); };

    slider.querySelector('.slider-prev').addEventListener('click', function () { go(current - 1); });
    slider.querySelector('.slider-next').addEventListener('click', function () { go(current + 1); });
    dots.forEach(function (d, k) { d.addEventListener('click', function () { go(k); }); });
    pauseBtn.addEventListener('click', function () {
      userPaused = !userPaused;
      pauseBtn.setAttribute('aria-pressed', userPaused ? 'true' : 'false');
      pauseBtn.setAttribute('aria-label', userPaused ? 'Play slideshow' : 'Pause slideshow');
      schedule();
    });
    pauseBtn.setAttribute('aria-pressed', userPaused ? 'true' : 'false');
    if (userPaused) pauseBtn.setAttribute('aria-label', 'Play slideshow');

    // Hold still while someone is reading the copy or filling in the quote form
    var hold = function (on) { return function () { hoverPaused = on; schedule(); }; };
    var copyArea = slider.querySelector('.hero-copy');
    copyArea.addEventListener('mouseenter', hold(true));
    copyArea.addEventListener('mouseleave', hold(false));
    slider.addEventListener('focusin', hold(true));
    slider.addEventListener('focusout', function (e) { if (!slider.contains(e.relatedTarget)) hold(false)(); });
    document.addEventListener('visibilitychange', schedule);

    // Swipe on touch screens (not on the form)
    var startX = null;
    slider.addEventListener('touchstart', function (e) {
      startX = e.target.closest('.ticket') ? null : e.touches[0].clientX;
    }, { passive: true });
    slider.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) go(current + (dx < 0 ? 1 : -1));
      startX = null;
    });

    show(0);
    schedule();
  }

  // Earliest travel date = today
  document.querySelectorAll('input[type="date"]').forEach(function (el) {
    el.min = new Date().toISOString().slice(0, 10);
  });
})();
