// SLV Tailor Shop — Main JS

// ── Mobile nav toggle ──
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');
if (navToggle && navLinks) {
  navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
  document.addEventListener('click', e => {
    if (!navToggle.contains(e.target) && !navLinks.contains(e.target))
      navLinks.classList.remove('open');
  });
}

// ── Scroll-to-top button ──
const scrollBtn = document.querySelector('.scroll-top');
if (scrollBtn) {
  window.addEventListener('scroll', () => {
    scrollBtn.classList.toggle('show', window.scrollY > 300);
  }, { passive: true });
  scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

// ── Admin sidebar mobile ──
const mobilMenuBtn = document.querySelector('.mobile-menu-btn');
const adminLayout = document.querySelector('.admin-layout');
if (mobilMenuBtn && adminLayout) {
  mobilMenuBtn.addEventListener('click', () => adminLayout.classList.toggle('sidebar-open'));
  document.addEventListener('click', e => {
    if (adminLayout && adminLayout.classList.contains('sidebar-open')) {
      const sidebar = adminLayout.querySelector('.sidebar');
      if (sidebar && !sidebar.contains(e.target) && !mobilMenuBtn.contains(e.target))
        adminLayout.classList.remove('sidebar-open');
    }
  });
}

// ── Lazy loading images ──
if ('IntersectionObserver' in window) {
  const lazyImgs = document.querySelectorAll('img.lazy');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        if (img.dataset.src) { img.src = img.dataset.src; }
        img.classList.add('loaded');
        observer.unobserve(img);
      }
    });
  }, { rootMargin: '100px' });
  lazyImgs.forEach(img => observer.observe(img));
}

// ── Image lightbox ──
function openImageModal(src, title) {
  const overlay = document.getElementById('imgModalOverlay');
  const img = document.getElementById('imgModalImg');
  const cap = document.getElementById('imgModalCaption');
  if (overlay && img) {
    img.src = src;
    if (cap) cap.textContent = title || '';
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}
function closeImageModal() {
  const overlay = document.getElementById('imgModalOverlay');
  if (overlay) { overlay.classList.remove('open'); document.body.style.overflow = ''; }
}

// ── Modal helpers ──
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('open'); document.body.style.overflow = 'hidden'; }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('open'); document.body.style.overflow = ''; }
}
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) {
      overlay.classList.remove('open');
      document.body.style.overflow = '';
    }
  });
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => {
      m.classList.remove('open'); document.body.style.overflow = '';
    });
  }
});

// ── Billing: auto calculate balance ──
function updateBalance() {
  const final = parseFloat(document.getElementById('final_amount')?.value || 0);
  const advance = parseFloat(document.getElementById('advance_amount')?.value || 0);
  const balField = document.getElementById('balance_display');
  if (balField) balField.textContent = 'Rs. ' + Math.max(0, final - advance).toFixed(2);
}
['final_amount', 'advance_amount'].forEach(id => {
  const el = document.getElementById(id);
  if (el) el.addEventListener('input', updateBalance);
});
updateBalance();

// ── Auto fill from order ──
function fillFromOrder(selectEl) {
  const opt = selectEl.options[selectEl.selectedIndex];
  if (!opt || !opt.value) return;
  const setVal = (id, val) => { const el = document.getElementById(id); if (el && val) el.value = val; };
  setVal('customer_name', opt.dataset.name);
  setVal('phone', opt.dataset.phone);
  setVal('age', opt.dataset.age);
  setVal('address', opt.dataset.address);
  setVal('dress_type', opt.dataset.dress);
  setVal('measurements', opt.dataset.measurements);
  setVal('delivery_date', opt.dataset.delivery);
  updateBalance();
}

// ── Confirm delete ──
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', e => {
    if (!confirm(el.dataset.confirm || 'Are you sure?')) e.preventDefault();
  });
});

// ── Print invoice ──
function printInvoice() { window.print(); }

// ── Filter chips (designs page) ──
document.querySelectorAll('.filter-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    const form = chip.closest('form') || document.getElementById('filterForm');
    const input = document.getElementById(chip.dataset.target);
    if (input) {
      input.value = chip.dataset.value;
      if (form) form.submit();
    }
  });
});

// ── Toast notification ──
function showToast(msg, type = 'success') {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.style.cssText = 'position:fixed;bottom:1.5rem;left:50%;transform:translateX(-50%);z-index:9999;display:flex;flex-direction:column;gap:0.5rem;';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.style.cssText = `background:${type==='success'?'#2E7D32':type==='error'?'#C62828':'#5D4037'};color:#fff;padding:0.8rem 1.5rem;border-radius:8px;font-size:0.95rem;font-weight:600;box-shadow:0 4px 12px rgba(0,0,0,0.2);min-width:200px;text-align:center;`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 2500);
}
