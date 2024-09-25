//
// smooth-scroll.js
//

import SmoothScroll from 'smooth-scroll';

const toggle = '[data-smoothscroll]';
const offset = 0;

var options = {
  header: '.navbar.fixed-top',
  offset: function (anchor, toggle) {
    return toggle.dataset.offset ? toggle.dataset.offset : offset;
  },
};

new SmoothScroll(toggle, options);

window.SmoothScroll = SmoothScroll;
