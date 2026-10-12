(function(){"use strict";
function run(){var n=document.querySelectorAll('[data-sc="hours"]'),d=String(new Date().getDay());
 for(var i=0;i<n.length;i++){var r=n[i].querySelector('tr[data-day="'+d+'"]');if(r)r.setAttribute("aria-current","date")}}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
