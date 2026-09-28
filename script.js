document.getElementById('year').textContent=new Date().getFullYear();

(function () {
  var footer = document.querySelector('.footer');
  if (!footer || document.querySelector('.amazon-affiliate-banner')) return;

  var banner = document.createElement('section');
  banner.className = 'amazon-affiliate-banner';
  banner.setAttribute('aria-label', 'Amazon Associates link');

  banner.innerHTML =
    '<a class="amazon-affiliate-link" href="https://amzn.to/4yWFRi5" target="_blank" rel="sponsored noopener noreferrer" aria-label="Amazon.in Deals">' +
      '<span class="amazon-affiliate-logo" aria-hidden="true"><span>amazon</span><i></i></span>' +
      '<span class="amazon-affiliate-copy">' +
        '<span class="amazon-affiliate-domain">amazon.in</span>' +
        '<strong>Amazon.in - Deals</strong>' +
        '<span>Explore deals on Amazon.in</span>' +
      '</span>' +
    '</a>';

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

(function () {
  var grid = document.getElementById('pipeline-books-grid');
  if (!grid) return;

  fetch('/data/books.json', {cache: 'no-store'})
    .then(function (response) { if (!response.ok) throw new Error('Book data unavailable'); return response.json(); })
    .then(function (data) {
      grid.innerHTML = '';
      (data.books || []).forEach(function (book) {
        var card = document.createElement('article');
        card.className = 'catalog-card verified-book';
        var title = document.createElement('h3');
        title.textContent = book.title || 'Untitled book';
        var meta = document.createElement('p');
        meta.textContent = (book.isbn ? 'ISBN ' + book.isbn + ' · ' : '') + 'ASIN ' + book.asin;
        var link = document.createElement('a');
        link.className = 'amazon-button';
        link.href = book.amazon_url;
        link.target = '_blank';
        link.rel = 'noopener';
        link.textContent = 'Amazon.com ↗';
        card.appendChild(title);
        card.appendChild(meta);
        if (book.cover) {
          var img = document.createElement('img');
          img.className = 'book-cover-image';
          img.src = book.cover;
          img.alt = (book.title || 'Book') + ' cover';
          img.loading = 'lazy';
          card.insertBefore(img, title);
        }
        card.appendChild(link);
        if (book.slug) {
          var detail = document.createElement('a');
          detail.className = 'text-link';
          detail.href = '/books/' + book.slug + '/';
          detail.textContent = 'Book page →';
          card.appendChild(detail);
        }
        grid.appendChild(card);
      });
    })
    .catch(function () {
      grid.innerHTML = '<p class="not-found" style="display:block">The verified book data is temporarily unavailable.</p>';
    });
})();

(function () {
  var path = window.location.pathname;
  if (path.indexOf('/articles/') !== 0 || path === '/articles/' || document.querySelector('.article-book-links')) return;
  var target = '/books/';
  if (/large-language|prompt-engineering|ai-and-the-future/i.test(path)) target = '/books/large-language-models/';
  else if (/kailash|bermuda|atlantis/i.test(path)) target = '/books/mount-kailash-bermuda-triangle-atlantis/';
  else if (/shasta/i.test(path)) target = '/books/travellers-guide-mount-shasta/';
  else if (/time-travel/i.test(path)) target = '/books/time-travel/';
  var section = document.createElement('section');
  section.className = 'related-content article-book-links';
  section.innerHTML = '<p class="eyebrow">RELATED BOOK</p><h2>Continue with the book</h2><p>Explore the related title on the official author site, then use the Amazon link to check the current edition.</p><div class="related-links"><a href="' + target + '">Open book page →</a><a href="/books/">Browse all books →</a></div>';
  var main = document.querySelector('main');
  if (main) main.appendChild(section);
})();