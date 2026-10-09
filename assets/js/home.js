// トップページと実績ページ（/media/）の共通スクリプト
// Scroll reveal
const reveals = document.querySelectorAll('.reveal, .reveal-scale, .reveal-left, .reveal-right');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

reveals.forEach(el => observer.observe(el));

// ヒーロー「AIを使ってみたら」タイピング演出
(function initTypewriter() {
  const live = document.getElementById('typeLive');
  const after = document.getElementById('typeAfter');
  const line3 = document.getElementById('typeLine3');
  if (!live || !after || !line3) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  const caret = live.querySelector('.type-caret');
  const textNode = live.firstChild;
  const full = 'AIを使ってみたら';

  textNode.textContent = '';
  after.style.opacity = '0';
  line3.style.opacity = '0';
  line3.style.transform = 'translateY(8px)';
  after.style.transition = 'opacity 0.8s ease';
  line3.style.transition = 'opacity 0.9s cubic-bezier(0.16, 1, 0.3, 1), transform 0.9s cubic-bezier(0.16, 1, 0.3, 1)';
  caret.classList.add('blink');

  let i = 0;
  setTimeout(() => {
    const iv = setInterval(() => {
      i++;
      textNode.textContent = full.slice(0, i);
      if (i >= full.length) {
        clearInterval(iv);
        setTimeout(() => {
          after.style.opacity = '1';
          line3.style.opacity = '1';
          line3.style.transform = 'translateY(0)';
        }, 350);
        setTimeout(() => {
          caret.classList.remove('blink');
          caret.style.transition = 'opacity 0.8s ease';
          caret.style.opacity = '0';
        }, 2800);
      }
    }, 130);
  }, 1500);
})();

// スクロール演出：見出し行リビール・ヒーローパララックス・慣性スクロール
(function initScrollFeel() {
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 見出しを行ごとに分割し、マスクの下から立ち上げる
  if (!reduce) {
    document.querySelectorAll('.section-title').forEach(title => {
      const lines = title.innerHTML.split(/<br\s*\/?>/i);
      title.innerHTML = lines.map(l =>
        '<span class="line"><span class="line-inner">' + l + '</span></span>'
      ).join('');
      title.querySelectorAll('.line-inner').forEach((el, i) => {
        el.style.transitionDelay = (i * 0.12) + 's';
      });
    });
    const titleObserver = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          en.target.classList.add('lines-in');
          titleObserver.unobserve(en.target);
        }
      });
    }, { threshold: 0.3 });
    document.querySelectorAll('.section-title').forEach(t => titleObserver.observe(t));
  }

  const finePointer = window.matchMedia('(pointer: fine)').matches;
  if (reduce || !finePointer) return;

  // ヒーローパララックス（本と文字がわずかに違う速度で沈む）
  const heroLeft = document.querySelector('.hero-left');
  let ticking = false;
  function parallax() {
    const y = window.scrollY;
    if (y < window.innerHeight * 1.2) {
      document.documentElement.style.setProperty('--para', (y * 0.12) + 'px');
      if (heroLeft) heroLeft.style.transform = 'translateY(' + (y * 0.05) + 'px)';
    }
    ticking = false;
  }
  window.addEventListener('scroll', () => {
    if (!ticking) { ticking = true; requestAnimationFrame(parallax); }
  }, { passive: true });
})();

// TV・雑誌カードのstagger
['.tv-grid .tv-card', '.magazine-grid .magazine-card'].forEach(selector => {
  document.querySelectorAll(selector).forEach((card, i) => {
    card.style.transitionDelay = `${i * 0.1}s`;
    card.classList.add('reveal');
    observer.observe(card);
  });
});

// 見出しの手書きマーカー（スクロールで線が引かれる）
(function initMarkers() {
  const titles = document.querySelectorAll('.section-title');
  if (!titles.length) return;
  const svgNS = 'http://www.w3.org/2000/svg';
  titles.forEach(t => {
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'marker-underline');
    svg.setAttribute('viewBox', '0 0 240 14');
    svg.setAttribute('preserveAspectRatio', 'none');
    svg.setAttribute('aria-hidden', 'true');
    const path = document.createElementNS(svgNS, 'path');
    path.setAttribute('d', 'M4 10 C 44 4, 78 12, 116 7 C 152 3, 196 6, 236 8');
    path.setAttribute('pathLength', '1');
    svg.appendChild(path);
    t.insertAdjacentElement('afterend', svg);
  });
  // 見出しの文字幅に合わせて線の長さを調整（最終行の実測幅×0.9）
  function sizeMarkers() {
    titles.forEach(t => {
      const svg = t.nextElementSibling;
      if (!svg || !svg.classList.contains('marker-underline')) return;
      let textW = 0;
      const lines = t.querySelectorAll('.line-inner');
      if (lines.length) {
        textW = lines[lines.length - 1].getBoundingClientRect().width;
      } else {
        const range = document.createRange();
        range.selectNodeContents(t);
        textW = range.getBoundingClientRect().width;
      }
      if (textW > 0) {
        svg.style.width = Math.max(72, Math.round(textW * 0.9)) + 'px';
        svg.style.maxWidth = '100%';
      }
    });
  }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(sizeMarkers);
  } else {
    window.addEventListener('load', sizeMarkers);
  }
  const markerObserver = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) {
        en.target.classList.add('drawn');
        markerObserver.unobserve(en.target);
      }
    });
  }, { threshold: 0.6 });
  document.querySelectorAll('.marker-underline').forEach(s => markerObserver.observe(s));
})();

// Nav scroll effect
const nav = document.querySelector('body > nav');
window.addEventListener('scroll', () => {
  if (window.scrollY > 60) {
    nav.style.boxShadow = '0 4px 24px rgba(0,0,0,0.08)';
  } else {
    nav.style.boxShadow = 'none';
  }
});

// Mobile CTA Visibility
const mobileCta = document.getElementById('mobile-cta');
window.addEventListener('scroll', () => {
  const contactEl = document.getElementById('contact');
  const contactInView = contactEl &&
    window.scrollY + window.innerHeight > contactEl.offsetTop + 120;
  if (window.scrollY > 500 && window.innerWidth <= 768 && !contactInView) {
    mobileCta.classList.add('visible');
  } else {
    mobileCta.classList.remove('visible');
  }
});

const lightbox = document.getElementById('lightbox');
const lightboxImg = document.getElementById('lightbox-img');
const lightboxClose = document.getElementById('lightbox-close');
const lightboxTitle = document.getElementById('lightbox-title');
let lightboxTrigger = null;

function openLightbox(img) {
  lightboxTrigger = img;
  lightboxImg.src = img.currentSrc || img.src;
  lightboxImg.alt = img.alt;
  lightboxTitle.textContent = '拡大表示：' + (img.alt || '画像');
  document.body.classList.add('lightbox-open');
  lightbox.showModal();
  lightboxClose.focus();
}

function closeLightbox() {
  if (lightbox.open) lightbox.close();
}

const lightboxImages = document.querySelectorAll(
  '.mokuji-img, .book-cover-large, .bookstore-card:not([aria-hidden="true"]) img, .ranking-item-img-wrap img'
);

lightboxImages.forEach(img => {
  img.tabIndex = 0;
  img.setAttribute('role', 'button');
  img.setAttribute('aria-haspopup', 'dialog');
  img.setAttribute('aria-controls', 'lightbox');
  img.setAttribute('aria-label', '画像を拡大：' + (img.alt || '画像'));
  img.dataset.lightboxTrigger = '';

  img.addEventListener('click', () => openLightbox(img));
  img.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      openLightbox(img);
    }
  });
});

// Mobile editorial index — open/close + smooth scroll
(function initMobileNav() {
  const toggle = document.querySelector('.nav-toggle');
  const overlay = document.getElementById('nav-overlay');
  if (!toggle || !overlay) return;

  const body = document.body;

  function open() {
    body.classList.add('nav-open');
    overlay.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
    toggle.setAttribute('aria-label', 'メニューを閉じる');
    overlay.setAttribute('aria-hidden', 'false');
  }

  function close() {
    body.classList.remove('nav-open');
    overlay.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.setAttribute('aria-label', 'メニューを開く');
    overlay.setAttribute('aria-hidden', 'true');
  }

  toggle.addEventListener('click', () => {
    if (overlay.classList.contains('is-open')) close();
    else open();
  });

  overlay.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const href = link.getAttribute('href');
      close();
      setTimeout(() => {
        const target = document.querySelector(href);
        if (!target) return;
        const navEl = document.querySelector('nav');
        const navH = navEl ? navEl.getBoundingClientRect().height : 56;
        const top = target.getBoundingClientRect().top + window.scrollY - navH - 8;
        window.scrollTo({ top, behavior: 'smooth' });
      }, 320);
    });
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) close();
  });
})();

// Bookstore gallery — auto-scroll with touch/hover passthrough
(function initBookstoreMarquee() {
  const scroller = document.querySelector('.bookstore-scroll');
  const track = scroller && scroller.querySelector('.bookstore-track');
  if (!scroller || !track) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // reduced-motion: no auto-scroll, but keep the seamless wrap for manual swipes
  const speed = reduceMotion ? 0 : (window.innerWidth <= 600 ? 0.35 : 0.5); // px per frame, slow and editorial
  let hoverPaused = false;
  let pauseUntil = 0;

  const pauseFor = ms => { pauseUntil = Math.max(pauseUntil, performance.now() + ms); };

  scroller.addEventListener('mouseenter', () => { hoverPaused = true; });
  scroller.addEventListener('mouseleave', () => { hoverPaused = false; });
  scroller.addEventListener('pointerdown', () => pauseFor(2500), { passive: true });
  scroller.addEventListener('touchstart', () => pauseFor(3000), { passive: true });
  scroller.addEventListener('wheel',      () => pauseFor(2000), { passive: true });

  function step(now) {
    const half = track.scrollWidth / 2;
    if (!hoverPaused && now >= pauseUntil) {
      scroller.scrollLeft += speed;
    }
    if (scroller.scrollLeft >= half) {
      scroller.scrollLeft -= half;
    } else if (scroller.scrollLeft < 0) {
      scroller.scrollLeft += half;
    }
    requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
})();

lightboxClose.addEventListener('click', closeLightbox);

lightbox.addEventListener('click', e => {
  if (e.target === lightbox) closeLightbox();
});

lightbox.addEventListener('cancel', e => {
  e.preventDefault();
  closeLightbox();
});

lightbox.addEventListener('close', () => {
  document.body.classList.remove('lightbox-open');
  lightboxImg.removeAttribute('src');
  lightboxImg.alt = '';
  lightboxTitle.textContent = '画像の拡大表示';
  if (lightboxTrigger) lightboxTrigger.focus();
  lightboxTrigger = null;
});

// Back to top
(function initBackToTop() {
  const btn = document.getElementById('back-to-top');
  if (!btn) return;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let ticking = false;
  function update() {
    if (window.scrollY > 600) btn.classList.add('visible');
    else btn.classList.remove('visible');
    ticking = false;
  }
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });
  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
  });
})();

// Web記事：媒体別に折りたたみ、閉じた状態でも本数と最新掲載を見せる
{
  document.querySelectorAll('.web-media-block').forEach(block => {
    const name = block.querySelector('.web-media-name');
    const list = block.querySelector('.article-list');
    const items = Array.from(block.querySelectorAll('.article-item'));
    if (!name || !list || !items.length) return;

    const latest = items.reduce((selected, item) => {
      const currentDate = item.querySelector('.article-date')?.textContent?.trim() || '';
      const selectedDate = selected.querySelector('.article-date')?.textContent?.trim() || '';
      return currentDate > selectedDate ? item : selected;
    }, items[0]);

    const titleEl = latest.querySelector('.article-title');
    let previewTitle = '';
    if (titleEl) {
      const titleClone = titleEl.cloneNode(true);
      titleClone.querySelectorAll('.sr-only').forEach(el => el.remove());
      previewTitle = titleClone.textContent.trim();
    }
    const header = document.createElement('button');
    header.type = 'button';
    header.className = 'web-media-header-toggle';
    header.setAttribute('aria-expanded', 'false');

    const heading = document.createElement('div');
    heading.className = 'web-media-heading';
    heading.appendChild(name);

    const meta = document.createElement('div');
    meta.className = 'web-media-meta';
    meta.innerHTML = `<span class="web-media-count">${items.length}本掲載</span><span class="web-media-open-label">記事一覧を見る</span>`;
    heading.appendChild(meta);

    if (previewTitle) {
      const preview = document.createElement('p');
      preview.className = 'web-media-preview';
      preview.textContent = `最新掲載：${previewTitle}`;
      heading.appendChild(preview);
    }

    const chevron = document.createElement('span');
    chevron.className = 'web-media-chevron';
    chevron.setAttribute('aria-hidden', 'true');
    chevron.textContent = '⌄';

    header.append(heading, chevron);
    block.insertBefore(header, list);
    block.classList.add('is-collapsed');

    header.addEventListener('click', () => {
      const expanded = block.classList.toggle('is-open');
      block.classList.toggle('is-collapsed', !expanded);
      header.setAttribute('aria-expanded', String(expanded));
      const label = header.querySelector('.web-media-open-label');
      if (label) label.textContent = expanded ? '閉じる' : '記事一覧を見る';
    });
  });
}

// お問い合わせフォーム：ページ内で完結するAJAX送信＋計測
(function initContactForm() {
  const form = document.getElementById('contact-form');
  const success = document.getElementById('contact-success');
  const submitBtn = document.getElementById('contact-submit');
  if (!form || !success || !submitBtn) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = '送信中…';
    try {
      const res = await fetch(form.action, {
        method: 'POST',
        body: new FormData(form),
        headers: { Accept: 'application/json' }
      });
      if (!res.ok) throw new Error('formspree error');
      form.hidden = true;
      success.hidden = false;
      success.scrollIntoView({ behavior: 'smooth', block: 'center' });
      if (typeof gtag === 'function') {
        gtag('event', 'generate_lead', { form_id: 'contact-form' });
      }
    } catch (err) {
      // AJAXが失敗したら通常送信にフォールバック（submit()はこのハンドラを再発火しない）
      submitBtn.disabled = false;
      submitBtn.textContent = '送信する →';
      form.submit();
    }
  });
})();

// メディア実績：アーカイブ（雑誌・イベント・Web記事・コラム連載）の開閉
{
  const toggle = document.getElementById('media-archive-toggle');
  const body = document.getElementById('media-archive-body');
  if (toggle && body) {
    toggle.addEventListener('click', () => {
      const expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      body.hidden = expanded;
    });
  }
}

// CTAクリック計測
document.querySelectorAll('[data-cta]').forEach(el => {
  el.addEventListener('click', () => {
    if (typeof gtag === 'function') {
      gtag('event', 'cta_click', { cta_location: el.dataset.cta });
    }
  });
});

// コラム連載「もっと見る」
{
  const columnItems = Array.from(document.querySelectorAll('.column-list .column-item'));
  const SHOW = 3;
  if (columnItems.length > SHOW) {
    columnItems.slice(SHOW).forEach(item => item.style.display = 'none');

    const btn = document.createElement('button');
    btn.className = 'column-show-more-btn';
    btn.textContent = `さらに${columnItems.length - SHOW}本を見る ＋`;

    let expanded = false;
    btn.addEventListener('click', () => {
      expanded = !expanded;
      columnItems.slice(SHOW).forEach(item => item.style.display = expanded ? '' : 'none');
      btn.textContent = expanded ? '折りたたむ ー' : `さらに${columnItems.length - SHOW}本を見る ＋`;
    });

    const columnList = document.querySelector('.column-list');
    columnList.after(btn);
  }
}
