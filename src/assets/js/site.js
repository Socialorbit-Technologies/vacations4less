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

  // Earliest travel date = today
  document.querySelectorAll('input[type="date"]').forEach(function (el) {
    el.min = new Date().toISOString().slice(0, 10);
  });
})();
