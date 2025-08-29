import '@/css/tw-output.css'
import htmx from 'htmx.org';
import { toggleHidden } from '@/js/modules/domUtils.js';
import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'
import collapse from '@alpinejs/collapse'
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
} from 'chart.js';

Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend
);

window.Alpine = Alpine;
Alpine.plugin(persist);
Alpine.plugin(collapse);

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
  },
  replaceContent(html) {
    this.errorMessage = '';
    this.open();
    document.querySelector('#global-modal').innerHTML = html;
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

window.addEventListener('pageshow', () => {
  Alpine.store('modal').close();
});

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


// instead of serverMsg, object with all custom events.
// or format events to include type
// evt = {"user-trips-updated":{"type":"serverMsg", "message": "Trips updated"}}


document.body.addEventListener("serverMsg", function (evt) {
  Alpine.store('modal').replaceContent(evt.detail.value);
});

window.renderChart = function (canvasId, labels, values, datasetLabel = 'Income') {
  const ctx = document.getElementById(canvasId)?.getContext('2d');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: datasetLabel,
        data: values,
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.2)',
        fill: true,
      }]
    },
    options: {}
  });
};


document.body.addEventListener('htmx:afterSwap', function (evt) {
  if (evt.target.id === 'income-timeline') {
    const el = evt.target.querySelector('[data-chart-labels]');
    if (!el) return;

    const labels = JSON.parse(el.dataset.chartLabels);
    const values = JSON.parse(el.dataset.chartValues);

    window.renderChart('income-timeline-chart', labels, values, 'Income');
  }
});


document.body.addEventListener('htmx:afterSwap', function (evt) {
  if (evt.target.id === 'trips-timeline') {
    const el = evt.target.querySelector('[data-chart-labels]');
    if (!el) return;

    const labels = JSON.parse(el.dataset.chartLabels);
    const values = JSON.parse(el.dataset.chartValues);

    window.renderChart('trips-timeline-chart', labels, values, 'Trips');
  }
});

