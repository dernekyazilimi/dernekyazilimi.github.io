(() => {
  if (!window.gtag) return;
  const banner = document.querySelector('#cookie-banner');
  const preferences = document.querySelectorAll('[data-cookie-preferences]');
  const choice = document.cookie.split(';').map(item => item.trim())
    .find(item => /^cerez_onayi=(kabul|red)$/.test(item));
  let opener;

  function clearAnalyticsCookies() {
    for (const entry of document.cookie.split(';')) {
      const name = entry.trim().split('=')[0];
      if (name !== '_ga' && !name.startsWith('_ga_')) continue;
      for (const domain of ['', '; Domain=' + location.hostname, '; Domain=dernekyazilimi.org']) {
        document.cookie = name + '=; Max-Age=0; Path=/; Secure; SameSite=Lax' + domain;
      }
    }
  }

  if (choice !== 'cerez_onayi=kabul') clearAnalyticsCookies();
  banner.hidden = Boolean(choice);
  for (const button of preferences) {
    button.hidden = false;
    button.addEventListener('click', () => {
      opener = button;
      banner.hidden = false;
      banner.querySelector('button').focus();
    });
  }
  const reserveSpace = () => document.body.style.paddingBottom =
    banner.hidden ? '' : banner.offsetHeight + 'px';
  new ResizeObserver(reserveSpace).observe(banner);
  for (const button of banner.querySelectorAll('[data-choice]')) {
    button.addEventListener('click', () => {
      const value = button.dataset.choice;
      document.cookie = 'cerez_onayi=' + value +
        '; Max-Age=15552000; Path=/; Domain=dernekyazilimi.org; SameSite=Lax; Secure';
      gtag('consent', 'update', {analytics_storage: value === 'kabul' ? 'granted' : 'denied'});
      if (value === 'kabul') window.__loadGTM?.();
      if (value === 'red') clearAnalyticsCookies();
      banner.hidden = true;
      reserveSpace();
      opener?.focus();
    });
  }
})();
