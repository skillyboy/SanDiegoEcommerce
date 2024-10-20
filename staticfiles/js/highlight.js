//
// highlight.js
//

import hljs from 'highlight.js/lib/core';
import javascript from 'highlight.js/lib/languages/javascript';
import xml from 'highlight.js/lib/languages/xml';

const highlights = document.querySelectorAll('.highlight');

hljs.registerLanguage('xml', xml);
hljs.registerLanguage('javascript', javascript);

highlights.forEach((highlight) => {
  hljs.highlightBlock(highlight);
});

window.hljs = hljs;
