// main.js – simple interactions for the landing page

document.addEventListener('DOMContentLoaded', function () {
  // CTA button scrolls to the about section
  const ctaBtn = document.getElementById('ctaBtn');
  if (ctaBtn) {
    ctaBtn.addEventListener('click', function () {
      const about = document.getElementById('about');
      if (about) {
        about.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }

  // Contact form validation & fake submit (alert)
  const form = document.getElementById('contactForm');
  const statusEl = document.getElementById('formStatus');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      const name = form.elements['name'].value.trim();
      const email = form.elements['email'].value.trim();
      const message = form.elements['message'].value.trim();

      if (!name || !email || !message) {
        statusEl.textContent = 'Bitte füllen Sie alle Felder aus.';
        statusEl.className = 'error';
        return;
      }
      // Simple email pattern
      const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
      if (!emailPattern.test(email)) {
        statusEl.textContent = 'Bitte geben Sie eine gültige E‑Mail-Adresse ein.';
        statusEl.className = 'error';
        return;
      }

      // In a real site you would POST the data. Here we just show a success message.
      statusEl.textContent = 'Vielen Dank! Ihre Nachricht wurde gesendet.';
      statusEl.className = 'success';
      form.reset();
    });
  }
});
