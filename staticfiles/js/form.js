//
// form.js
//

const toggles = document.querySelectorAll('[data-toggle="form-caption"]');

toggles.forEach((toggle) => {
  toggle.addEventListener('change', function () {
    const target = document.querySelector(toggle.dataset.target);
    const value = toggle.value;

    target.innerHTML = value;
  });
});
