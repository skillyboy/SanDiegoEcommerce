//
// dropdown.scss
//

import { Collapse } from 'bootstrap';

//
// Collapse nested elements when dropdown hides
//

const navbarDropdowns = document.querySelectorAll(
  '.navbar .dropdown, .navbar .dropup, .navbar .dropend, .navbar .dropstart'
);

navbarDropdowns.forEach((navbarDropdown) => {
  navbarDropdown.addEventListener('hide.bs.dropdown', () => {
    const collapseToggles = navbarDropdown.querySelectorAll('.dropdown-item[data-bs-toggle="collapse"]');

    collapseToggles.forEach((collapseToggle) => {
      const targetId = collapseToggle.getAttribute('data-bs-target') || collapseToggle.getAttribute('href');
      const targetEl = document.querySelector(targetId);
      const instance = Collapse.getInstance(targetEl);

      instance && instance.hide();
    });
  });
});

//
// Collapse navbar on anchor click
//

const navbarSmoothToggles = document.querySelectorAll('.navbar [data-smoothscroll]');

navbarSmoothToggles.forEach((navbarSmoothToggle) => {
  navbarSmoothToggle.addEventListener('click', () => {
    const navbarCollapse = navbarSmoothToggle.closest('.navbar-collapse');
    const instance = Collapse.getInstance(navbarCollapse);

    instance && instance.hide();
  });
});
