import '@/css/tw-output.css'
import htmx from 'htmx.org';
import { toggleHidden } from '@/js/modules/domUtils.js';
// import { toggleTheme } from '@/js/toggle-theme.js';

window.htmx = htmx;
window.toggleHidden = toggleHidden;
