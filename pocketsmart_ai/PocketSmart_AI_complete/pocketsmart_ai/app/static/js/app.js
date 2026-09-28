window.formatMoney = function(amount, currency) {
  try { return new Intl.NumberFormat(undefined, {style:'currency', currency: currency || 'INR', maximumFractionDigits:0}).format(amount); }
  catch { return `${currency || 'INR'} ${Math.round(amount).toLocaleString()}`; }
};
window.escapeHtml = function(value) { const d=document.createElement('div'); d.textContent=value ?? ''; return d.innerHTML; };
