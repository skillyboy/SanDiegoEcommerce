//
// counter.js
//

const countdowns = document.querySelectorAll('[data-countdown]');

function count(countdownDate, el) {
  const now = new Date().getTime();
  const distance = countdownDate - now;

  let days = Math.floor(distance / (1000 * 60 * 60 * 24));
  days = days < 10 ? '0' + days : days;
  let hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  hours = hours < 10 ? '0' + hours : hours;
  let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  minutes = minutes < 10 ? '0' + minutes : minutes;
  let seconds = Math.floor((distance % (1000 * 60)) / 1000);
  seconds = seconds < 10 ? '0' + seconds : seconds;

  el.querySelector('[data-days]').innerHTML = distance > 0 ? days : '00';
  el.querySelector('[data-hours]').innerHTML = distance > 0 ? hours : '00';
  el.querySelector('[data-minutes]').innerHTML = distance > 0 ? minutes : '00';
  el.querySelector('[data-seconds]').innerHTML = distance > 0 ? seconds : '00';
}

countdowns.forEach((countdown) => {
  const date = countdown.dataset.date;
  const countdownDate = new Date(date).getTime();

  count(countdownDate, countdown);
  setInterval(function () {
    count(countdownDate, countdown);
  }, 1000);
});
