//
// collapse.js
//

import { Collapse } from 'bootstrap';

const toggles = document.querySelectorAll('[data-collapse]');

toggles.forEach((toggle) => {
  toggle.addEventListener('click', (e) => {
    const action = toggle.dataset.collapse;
    const target = toggle.dataset.target;
    const targetEl = document.querySelector(target);

    const instance = Collapse.getOrCreateInstance(targetEl, { toggle: action === 'show' ? true : false });
    action === 'show' ? instance.show() : instance.hide();
  });
});
