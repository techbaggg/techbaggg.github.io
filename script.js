document.getElementById('year').textContent=new Date().getFullYear();
(function () {
  var nav = document.querySelector('.nav nav');
  if (!nav || nav.querySelector('a[href*="resume"]')) return;
  var link = document.createElement('a');
  link.href = '/resume/';
  link.textContent = 'Resume';
  var contact = nav.querySelector('a[href*="contact"]');
  if (contact) nav.insertBefore(link, contact);
  else nav.appendChild(link);
})();


(function () {
  var footer = document.querySelector('.footer');
  var body = document.body;
  if (!body || document.querySelector('.amazon-affiliate-banner')) return;

  if (footer) {
    Array.prototype.slice.call(footer.querySelectorAll('a[href*="affiliate-disclosure"]')).forEach(function (link) {
      link.remove();
    });
  }

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

  body.insertBefore(banner, body.firstElementChild);
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
(function(){var grid=document.getElementById('home-books-grid');if(!grid)return;var search=document.getElementById('home-book-search'),filters=document.getElementById('home-book-filters'),more=document.getElementById('home-books-more'),result=document.getElementById('home-book-result'),count=document.getElementById('home-book-count'),books=[],shown=24,category='All';fetch('/data/books.json',{cache:'no-store'}).then(function(r){if(!r.ok)throw new Error();return r.json()}).then(function(data){books=data.books||[];if(count)count.textContent=books.length;var cats=['All'].concat(Array.from(new Set(books.map(function(b){return b.genre||b.category||'Other'}))).sort());cats.forEach(function(c){var b=document.createElement('button');b.type='button';b.className='library-filter'+(c==='All'?' active':'');b.textContent=c;b.onclick=function(){category=c;shown=24;Array.prototype.forEach.call(filters.children,function(x){x.classList.remove('active')});b.classList.add('active');render()};filters.appendChild(b)});if(search)search.addEventListener('input',function(){shown=24;render()});if(more)more.onclick=function(){shown+=24;render()};render()}).catch(function(){grid.innerHTML='<p class="not-found" style="display:block">Book data is temporarily unavailable.</p>';if(more)more.hidden=true});function render(){var q=(search?search.value:'').trim().toLowerCase(),filtered=books.filter(function(b){var t=(b.title||'').toLowerCase(),g=b.genre||b.category||'Other';return(!q||t.indexOf(q)!==-1)&&(category==='All'||g===category)}),slice=filtered.slice(0,shown);grid.innerHTML='';slice.forEach(function(book){var item=document.createElement('article');item.className='home-book-item';var a=document.createElement('a');a.href=book.amazon_url||('https://www.amazon.com/dp/'+book.asin);a.target='_blank';a.rel='noopener noreferrer';var img=document.createElement('img');img.src=book.cover||book.image||('https://m.media-amazon.com/images/P/'+book.asin+'.01.L.jpg');img.alt='Book cover: '+(book.title||'Book')+' by Jagdish Arora';img.loading='lazy';a.appendChild(img);var h=document.createElement('h3');h.textContent=book.title||'Untitled book';a.appendChild(h);var s=document.createElement('span');s.textContent=book.genre||book.category||'Book';a.appendChild(s);item.appendChild(a);grid.appendChild(item)});if(result)result.textContent='Showing '+slice.length+' of '+filtered.length+' books';if(more)more.hidden=shown>=filtered.length}}})();