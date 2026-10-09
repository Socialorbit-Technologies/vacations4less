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

  // Earliest travel date = today
  document.querySelectorAll('input[type="date"]').forEach(function (el) {
    el.min = new Date().toISOString().slice(0, 10);
  });
})();
