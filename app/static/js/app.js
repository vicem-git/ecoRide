import '@/css/tw-output.css'
import htmx from 'htmx.org';
import { toggleHidden } from '@/js/modules/domUtils.js';
import 'tom-select/dist/css/tom-select.css';
import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'


window.Alpine = Alpine;
Alpine.plugin(persist);

Alpine.store('darkMode', {
  on: Alpine.$persist(false).as('darkMode_on'),

  toggle() {
    this.on = !this.on
  }
});

Alpine.store('modal', {
  show: Alpine.$persist(false).as('modal_show'),
  errorMessage: Alpine.$persist('').as('modal_error'),
  open() {
    this.show = true
  },
  close() {
    this.show = false;
    this.errorMessage = '';
  },
  setError(message) {
    this.errorMessage = message;
    this.open();
  }
});

Alpine.store('tripSearch', {
  start_city: Alpine.$persist('').as('trip_start'),
  end_city: Alpine.$persist('').as('trip_end'),
  passenger_nr: Alpine.$persist(1).as('trip_passengers'),
  start_date: Alpine.$persist('').as('trip_date'),
  eco: Alpine.$persist(false).as('trip_eco'),
  price: Alpine.$persist(25).as('trip_price'),
  rating: Alpine.$persist(3).as('trip_rating'),
});

Alpine.start();


window.htmx = htmx;
window.toggleHidden = toggleHidden;

document.body.addEventListener("htmx:beforeSwap", () => {
  document.querySelectorAll(".dropdown").forEach((dropdown) => {
    dropdown.classList.add("hidden");
  });
});

document.body.addEventListener("htmx:afterOnLoad", (evt) => {
  const trigger = evt.detail.xhr.getResponseHeader("HX-Trigger");
  if (trigger) {
    const data = JSON.parse(trigger);
    if (data.redirectTo) {
      setTimeout(() => {
        window.location.href = data.redirectTo;
      }, 3000);
    }
  }
});
