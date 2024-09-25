//
// flickity.js
//

import Flickity from 'flickity';

// Flickity defaults
Flickity.defaults.pageDots = false;
Flickity.defaults.prevNextButtons = false;
Flickity.defaults.imagesLoaded = true;
Flickity.defaults.initialIndex = 0;
Flickity.defaults.wrapAround = true;
Flickity.defaults.cellAlign = 'left';

// Toggles
const toggles = document.querySelectorAll('[data-toggle="flickity"]');

toggles.forEach((toggle) => {
  toggle.addEventListener('click', () => {
    const slide = toggle.getAttribute('data-slide');
    const target = toggle.getAttribute('data-target');
    const targetEl = document.querySelector(target);
    const slider = Flickity.data(targetEl);
    slider.select(slide, null, true);
  });
});

window.Flickity = Flickity;
