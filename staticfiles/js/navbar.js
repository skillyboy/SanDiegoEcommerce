//
// navbar.js
//

import { Dropdown } from 'bootstrap';

const navbarDropdowns = document.querySelectorAll('.navbar-nav .dropdown, .navbar-nav .dropend');

navbarDropdowns.forEach((navbarDropdown) => {
  const navbarCollapse = navbarDropdown.closest('.navbar-collapse');
  const toggle = navbarDropdown.querySelector('[data-bs-toggle="dropdown"]');

  navbarDropdown.addEventListener('mouseenter', function () {
    if (navbarCollapse.classList.contains('show')) {
      return;
    }

    navbarDropdown.classList.add('hovered');
    Dropdown.getOrCreateInstance(toggle).show();
  });

  navbarDropdown.addEventListener('mouseleave', function () {
    if (navbarCollapse.classList.contains('show')) {
      return;
    }

    Dropdown.getOrCreateInstance(toggle).hide();
    toggle.blur();
  });
});
