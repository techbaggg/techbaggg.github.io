document.getElementById('year').textContent=new Date().getFullYear();

(function () {
  var footer = document.querySelector('.footer');
  if (!footer || document.querySelector('.amazon-affiliate-banner')) return;

  var banner = document.createElement('section');
  banner.className = 'amazon-affiliate-banner';
  banner.setAttribute('aria-label', 'Amazon Associates link');

  banner.innerHTML =
    '<div class="amazon-affiliate-copy">' +
      '<span class="amazon-affiliate-label">AMAZON.IN</span>' +
      '<strong>Explore and shop on Amazon.in</strong>' +
      '<small>Paid link · As an Amazon Associate I earn from qualifying purchases.</small>' +
    '</div>' +
    '<a class="amazon-affiliate-button" href="https://amzn.to/4yWFRi5" target="_blank" rel="sponsored noopener noreferrer">Visit Amazon.in ↗</a>';

  footer.parentNode.insertBefore(banner, footer);
})();