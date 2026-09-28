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

(function () {
  var icon = document.querySelector('link[rel="icon"]');
  if (!icon) {
    icon = document.createElement('link');
    icon.rel = 'icon';
    icon.type = 'image/svg+xml';
    icon.href = '/favicon.svg';
    document.head.appendChild(icon);
  }
})();

(function () {
  var catalog = document.querySelector('.books-catalog-page');
  if (!catalog) return;

  var cards = Array.prototype.slice.call(catalog.querySelectorAll('.catalog-card'));
  var search = document.getElementById('book-search');
  var filter = document.getElementById('book-genre-filter');
  var count = document.getElementById('book-result-count');

  var categories = [
    ['AI', /language models|artificial intelligence|prompt|chatgpt|data science|dark web/i],
    ['Fiction', /love|romance|novel|quest|voyager|werewolf|magic|struggling author|lunar|galactic|traveling to mars/i],
    ['Travel', /travell|mount|kailash|shasta|mars/i],
    ['Mystery', /aliens|god theory|triangle|atlantis|mystic|secrets|nexus|reality/i],
    ['Science', /physics|calculus|chemistry|electronics|carbon|science/i],
    ['History', /history|civilization|gandhi|queen elizabeth|ramayana|bible|hammurabi/i],
    ['Wellness', /mental health|meditation|yoga|ketogenic|vegetable gardening/i],
    ['Writing', /writer|writing|prompt engineering/i],
    ['Law & Business', /insurance|administrative law|copyright|patents|trademarks|healthcare management/i]
  ];

  function genreFor(title) {
    for (var i = 0; i < categories.length; i++) {
      if (categories[i][1].test(title)) return categories[i][0];
    }
    return 'Other';
  }

  cards.forEach(function (card) {
    var title = (card.querySelector('h2') || {}).textContent || '';
    card.dataset.title = title.trim().toLowerCase();
    card.dataset.genre = card.dataset.genre || genreFor(title);
  });

  function render() {
    var q = (search ? search.value : '').trim().toLowerCase();
    var wanted = filter ? filter.value : 'All';
    var visible = 0;

    cards.forEach(function (card) {
      var matchesText = !q || card.dataset.title.indexOf(q) !== -1;
      var matchesGenre = wanted === 'All' || card.dataset.genre === wanted;
      var show = matchesText && matchesGenre;
      card.hidden = !show;
      if (show) visible++;
    });

    if (count) count.textContent = visible + ' book' + (visible === 1 ? '' : 's') + ' shown';
  }

  if (search) search.addEventListener('input', render);
  if (filter) filter.addEventListener('change', render);
  render();
})();