(function(){var q=document.getElementById('q'),box=document.getElementById('hits'),data=null,sel=-1;
function load(){if(data)return Promise.resolve(data);return fetch(ROOT+'assets/index.json').then(function(r){return r.json()}).then(function(d){data=d;return d})}
function esc(s){return String(s||'').replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function run(){var s=q.value.trim().toLowerCase();if(s.length<2){box.style.display='none';return}
load().then(function(d){var words=s.split(/\s+/),hits=[];for(var i=0;i<d.length&&hits.length<40;i++){var t=(d[i][0]+' '+d[i][1]+' '+d[i][3]).toLowerCase();if(words.every(function(w){return t.indexOf(w)>=0}))hits.push(d[i])}
hits.sort(function(a,b){return (a[0].toLowerCase().indexOf(s)===0?0:1)-(b[0].toLowerCase().indexOf(s)===0?0:1)});sel=-1;
box.innerHTML=hits.length?hits.map(function(h){return '<a href="'+ROOT+esc(h[2])+'"><span>'+esc(h[0])+'</span><small>'+esc(h[1])+(h[3]?' · '+esc(h[3]):'')+'</small></a>'}).join(''):'<a><span>No matches</span></a>';box.style.display='block'})}
q.addEventListener('input',run);q.addEventListener('focus',run);
q.addEventListener('keydown',function(e){var a=box.querySelectorAll('a[href]');if(!a.length)return;if(e.key==='ArrowDown'){sel=Math.min(sel+1,a.length-1);e.preventDefault()}else if(e.key==='ArrowUp'){sel=Math.max(sel-1,0);e.preventDefault()}else if(e.key==='Enter'){location.href=a[Math.max(sel,0)].href;return}else return;a.forEach(function(x,i){x.classList.toggle('sel',i===sel)})});
document.addEventListener('click',function(e){if(!e.target.closest('.search'))box.style.display='none'})})();
/* collapsible sections, expand/collapse all, page filter, open the section a link points into */
(function(){
function openTo(el){while(el){if(el.tagName==='DETAILS')el.open=true;el=el.parentElement}}
function hash(){var id=decodeURIComponent(location.hash.slice(1));if(!id)return;var t=document.getElementById(id);if(t){openTo(t);setTimeout(function(){t.scrollIntoView({block:'start'})},0)}}
window.addEventListener('hashchange',hash);hash();
var bar=document.querySelector('.toolbar');if(!bar)return;
var all=function(){return document.querySelectorAll('main details')};
bar.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;var o=b.dataset.act==='open';all().forEach(function(d){d.open=o})});
var f=bar.querySelector('input'),cnt=bar.querySelector('.count');if(!f)return;
var units=Array.prototype.slice.call(document.querySelectorAll('main .unit'));
var secs=Array.prototype.slice.call(document.querySelectorAll('main details.sec'));
var saved=null,t=null;
function run(){var s=f.value.trim().toLowerCase(),words=s.split(/\s+/).filter(Boolean);
if(!words.length){units.forEach(function(u){u.classList.remove('hide')});secs.forEach(function(d){d.classList.remove('hide')});if(saved){secs.forEach(function(d,i){d.open=saved[i]});saved=null}if(cnt)cnt.textContent='';return}
if(!saved)saved=secs.map(function(d){return d.open});
var n=0;units.forEach(function(u){var tx=(u.dataset.q||(u.dataset.q=u.textContent.toLowerCase()));var ok=words.every(function(w){return tx.indexOf(w)>=0});u.classList.toggle('hide',!ok);if(ok)n++});
secs.forEach(function(d){var any=d.querySelector('.unit:not(.hide)')||(!d.querySelector('.unit')&&words.every(function(w){return d.textContent.toLowerCase().indexOf(w)>=0}));d.classList.toggle('hide',!any);if(any)d.open=true});
if(cnt)cnt.textContent=n+' match'+(n===1?'':'es')}
f.addEventListener('input',function(){clearTimeout(t);t=setTimeout(run,120)});
f.addEventListener('keydown',function(e){if(e.key==='Escape'){f.value='';run()}});
})();
