//
// img-comp.js
//

const inputs = document.querySelectorAll('.img-comp-input');

function comp(el) {
  const front = el.parentElement.querySelector('.img-comp-front');
  const handle = el.parentElement.querySelector('.img-comp-handle');

  front.style.maxWidth = el.value + '%';
  handle.style.left = el.value + '%';
}

inputs.forEach((input) => {
  'input change'.split(' ').forEach(function (event) {
    input.addEventListener(event, function () {
      comp(input);
    });
  });
});
