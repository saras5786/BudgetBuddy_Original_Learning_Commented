/* SHARED JAVASCRIPT: base.html loads this on every page. Other JS files use BB.get(), BB.send(), BB.fmt() and BB.toast(). */

window.BB={
  fmt:(n,c='₹')=>`${c}${Number(n||0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2})}`,
  get:async u=>{const r=await fetch(u);if(!r.ok)throw new Error('Request failed');return r.json()},
  send:async(u,opt={})=>{const r=await fetch(u,{headers:{'Content-Type':'application/json'},...opt});const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.error||'Request failed');return d},
  toast:(m)=>{const e=document.createElement('div');e.className='flash success';e.textContent=m;document.querySelector('.main').prepend(e);setTimeout(()=>e.remove(),2600)},
  currency:'₹'
};
document.querySelectorAll('.auth-tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('.auth-tab').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.auth-panel').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.tab).classList.add('active')});
document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));document.querySelectorAll('.tab-panel').forEach(x=>x.classList.remove('active'));b.classList.add('active');document.getElementById(b.dataset.target).classList.add('active')});
BB.get('/api/me').then(d=>BB.currency=d.currency).catch(()=>{});
