//
// vote.js
//

const toggles = document.querySelectorAll('[data-toggle="vote"]');

toggles.forEach((toggle) => {
  toggle.addEventListener('click', (e) => {
    e.preventDefault();

    const count = toggle.dataset.count;
    toggle.setAttribute('data-count', parseInt(count) + 1);
  });
});
