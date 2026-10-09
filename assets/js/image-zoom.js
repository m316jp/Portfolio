// 既存の拡大操作を保ち、拡大可能な画像にだけ視覚的な手がかりを付ける。
document.querySelectorAll('[data-lightbox-trigger]').forEach(img => {
  const wrapper = document.createElement('span');
  wrapper.className = 'image-zoom';
  if (img.classList.contains('book-cover-large')) {
    wrapper.classList.add('image-zoom--cover');
  }
  img.before(wrapper);
  wrapper.append(img);

  const label = document.createElement('span');
  label.className = 'image-zoom-label';
  label.setAttribute('aria-hidden', 'true');
  label.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6M7 10h6M10 7v6"/></svg>拡大';
  label.addEventListener('click', () => img.click());
  wrapper.append(label);
});
