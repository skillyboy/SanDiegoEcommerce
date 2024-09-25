//
// variations.scss
//

import { Collapse } from 'bootstrap';

const toggles = document.querySelectorAll('[data-toggle="card-collapse"]');
const collapses = document.querySelectorAll('.card-collapse');

toggles.forEach((toggle) => {
  toggle.addEventListener('mouseenter', function () {
    const collapse = toggle.querySelector('.card-collapse');
    const bsCollapse = new Collapse(collapse, {
      toggle: true,
    });
  });

  toggle.addEventListener('mouseleave', function () {
    const collapse = toggle.querySelector('.card-collapse');
    const bsCollapse = Collapse.getInstance(collapse);
    const isCollapsing = collapse.classList.contains('collapsing');

    setTimeout(() => bsCollapse.hide(), isCollapsing ? 350 : 0);
  });
});

collapses.forEach((collapse) => {
  collapse.addEventListener('show.bs.collapse', function () {
    const parent = collapse.closest('.card-collapse-parent');
    const collapseHeight = collapse.scrollHeight;

    parent.style.webkitTransform = `translateY(-${collapseHeight}px)`;
    parent.style.transform = `translateY(-${collapseHeight}px)`;
  });

  collapse.addEventListener('hide.bs.collapse', function () {
    const parent = collapse.closest('.card-collapse-parent');

    parent.style.webkitTransform = '';
    parent.style.transform = '';
  });
});
