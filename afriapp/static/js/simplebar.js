//
// simplebar.js
//

import Simplebar from 'simplebar';

const toggles = document.querySelectorAll('[data-simplebar-collapse]');

toggles.forEach((toggle) => {
  const target = toggle.dataset.simplebarCollapse;
  const targetEl = document.querySelector(target);

  toggle.addEventListener('shown.bs.collapse', () => {
    new Simplebar(targetEl);
  });

  toggle.addEventListener('hidden.bs.collapse', () => {
    Simplebar.instances.get(targetEl).unMount();
  });
});
