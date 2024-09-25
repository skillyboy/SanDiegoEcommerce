//
// list.js
//

import List from 'list.js';

const toggles = document.querySelectorAll('[data-list]');

toggles.forEach((toggle) => {
  const options = JSON.parse(toggle.dataset.list);
  new List(toggle, options);
});

window.List = List;
