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
