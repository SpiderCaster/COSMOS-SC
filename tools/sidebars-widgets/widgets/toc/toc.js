(function(){"use strict";
function slug(s,used){var b=s.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"")||"section",id=b,n=2;while(used[id]){id=b+"-"+n++}used[id]=1;return id}
function init(box){
 var src=document.querySelector(box.getAttribute("data-source")||"article");if(!src)return;
 var min=parseInt(box.getAttribute("data-min"),10)||3,hs=src.querySelectorAll("h2,h3"),used={},i,h;
 for(i=0;i<document.querySelectorAll("[id]").length;i++){used[document.querySelectorAll("[id]")[i].id]=1}
 if(hs.length<min)return;
 var ol=box.querySelector("ol");ol.textContent="";
 for(i=0;i<hs.length;i++){h=hs[i];if(box.contains(h))continue;
  if(!h.id)h.id=slug(h.textContent,used);
  var li=document.createElement("li"),a=document.createElement("a");
  li.className="sc-toc-"+h.tagName.charAt(1);a.href="#"+h.id;a.textContent=h.textContent;li.appendChild(a);ol.appendChild(li)}
 box.hidden=false}
function run(){var n=document.querySelectorAll('[data-sc="toc"]');for(var i=0;i<n.length;i++)init(n[i])}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run()})();
