//
// rating.js
//

const ratingInputs = document.querySelectorAll('.rating-input');

ratingInputs.forEach((ratingInput) => {
  ['change', 'input'].forEach((event) => {
    ratingInput.addEventListener(event, () => {
      const ratingCurrent = ratingInput.closest('.rating-form').querySelector('.rating');
      const value = ratingInput.value;

      ratingCurrent.dataset.value = value;
    });
  });
});
