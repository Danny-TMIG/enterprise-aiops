import '../styles/global.css';
import './components/button.ts';
import './components/card.ts';
import './components/badge.ts';
import './components/modal.ts';
import './components/sidebar.ts';
import './components/navbar.ts';
import './components/footer.ts';
import './components/grid.ts';
import './components/form-input.ts';
import './components/select.ts';
import './components/table.ts';
import './components/pagination.ts';
import './components/tooltip.ts';
import './components/dropdown.ts';
import './components/carousel.ts';
import './components/tabs.ts';

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch((e) => {
      console.warn('sw registration failed', e);
    });
  });
}
