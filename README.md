<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>XASANBOY OPTOM</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;font-family:'Segoe UI',sans-serif;-webkit-tap-highlight-color:transparent}
body{background:#f5f5f5;max-width:430px;margin:0 auto;min-height:100vh}
.header{background:linear-gradient(135deg,#e8000a,#a80008);padding:14px 16px;color:#fff;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:100;box-shadow:0 4px 20px rgba(232,0,10,0.3)}
.logo{width:42px;height:42px;background:#fff;border-radius:12px;display:flex;align-items:center;justify-content:center;font-weight:900;color:#e8000a;font-size:14px;flex-shrink:0;line-height:1}
.h-title{font-size:17px;font-weight:800;letter-spacing:-0.3px}
.h-sub{font-size:11px;opacity:0.75}
.back-btn{background:rgba(255,255,255,0.2);border:none;color:#fff;border-radius:10px;width:36px;height:36px;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.cats{display:flex;gap:8px;overflow-x:auto;padding:12px 12px;background:#fff;scrollbar-width:none;border-bottom:1px solid #f1f5f9}
.cats::-webkit-scrollbar{display:none}
.cat{flex-shrink:0;padding:7px 14px;border-radius:20px;border:2px solid #e2e8f0;background:#fff;font-size:12px;font-weight:700;cursor:pointer;color:#64748b;transition:all 0.2s}
.cat.active{background:#e8000a;border-color:#e8000a;color:#fff}
.products{padding:10px 10px 90px}
.product{background:#fff;border-radius:14px;padding:12px;margin-bottom:8px;display:flex;gap:12px;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,0.06)}
.prod-img{width:68px;height:68px;background:linear-gradient(135deg,#fff5f5,#fff);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:34px;flex-shrink:0;border:1px solid #fecdd3}
.prod-info{flex:1;min-width:0}
.prod-name{font-weight:700;font-size:14px;color:#1e293b;margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.prod-price{font-weight:800;font-size:15px;color:#e8000a}
.prod-stock{font-size:11px;color:#94a3b8;margin-top:2px}
.add-btn{background:#fff1f2;color:#e8000a;border:1.5px solid #fecdd3;border-radius:10px;padding:8px 12px;font-weight:700;cursor:pointer;font-size:12px;white-space:nowrap;transition:all 0.2s;flex-shrink:0}
.add-btn.added{background:#e8000a;color:#fff;border-color:#e8000a}
.cart-bar{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:calc(100% - 24px);max-width:406px;background:linear-gradient(135deg,#e8000a,#a80008);padding:14px 18px;display:flex;align-items:center;gap:10px;color:#fff;cursor:pointer;box-shadow:0 -4px 20px rgba(232,0,10,0.3);border-radius:16px 16px 0 0;z-index:50;transition:transform 0.3s}
.cart-bar.hidden{transform:translateX(-50%) translateY(100%)}
.cart-count-badge{background:#fff;color:#e8000a;border-radius:50%;width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:13px;flex-shrink:0}
.cart-total-text{flex:1;font-weight:700;font-size:15px}
.page{display:none}
.page.active{display:block}
.cart-list{padding:12px 12px 0}
.cart-item{background:#fff;border-radius:14px;padding:11px 12px;margin-bottom:8px;display:flex;gap:10px;align-items:center;box-shadow:0 1px 6px rgba(0,0,0,0.05)}
.cart-emoji{width:44px;height:44px;background:#fff5f5;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0}
.qty-row{display:flex;align-items:center;gap:6px;flex-shrink:0}
.qty-btn{width:28px;height:28px;border-radius:8px;border:1.5px solid #e2e8f0;background:#f8fafc;cursor:pointer;font-size:16px;font-weight:700;display:flex;align-items:center;justify-content:center}
.qty-num{font-weight:800;font-size:15px;min-width:20px;text-align:center}
.summary-card{background:#fff;border-radius:14px;padding:14px;margin:8px 12px;box-shadow:0 1px 6px rgba(0,0,0,0.05)}
.sum-row{display:flex;justify-content:space-between;padding:5px 0;font-size:14px;color:#64748b}
.sum-total{display:flex;justify-content:space-between;padding:8px 0 0;font-size:18px;font-weight:800;color:#1e293b;border-top:1px solid #f1f5f9;margin-top:4px}
.order-btn{display:block;width:calc(100% - 24px);margin:10px 12px 90px;background:linear-gradient(135deg,#e8000a,#a80008);color:#fff;border:none;border-radius:16px;padding:16px;font-size:16px;font-weight:800;cursor:pointer;box-shadow:0 6px 20px rgba(232,0,10,0.35);letter-spacing:0.3px}
.empty-state{text-align:center;padding:60px 20px;color:#94a3b8}
.empty-state div:first-child{font-size:64px;margin-bottom:12px}
.empty-state div:nth-child(2){font-weight:800;font-size:18px;color:#1e293b;margin-bottom:6px}
.go-btn{background:#e8000a;color:#fff;border:none;border-radius:14px;padding:12px 28px;font-size:15px;font-weight:700;cursor:pointer;margin-top:10px}
</style>
</head>
<body>

<!-- CATALOG PAGE -->
<div id="catalog-page" class="page active">
  <div class="header">
    <div class="logo">XO<br>🛒</div>
    <div style="flex:1">
      <div class="h-title">XASANBOY OPTOM</div>
      <div class="h-sub">Tezkor sifatli yetkazib berish</div>
    </div>
  </div>
  <div class="cats" id="cats-container"></div>
  <div class="products" id="products-container"></div>
</div>

<!-- CART PAGE -->
<div id="cart-page" class="page">
  <div class="header">
    <button class="back-btn" onclick="showPage('catalog')">←</button>
    <div style="flex:1">
      <div class="h-title">Savat</div>
      <div class="h-sub" id="cart-subtitle">0 ta mahsulot</div>
    </div>
    <button onclick="clearCart()" style="background:rgba(255,255,255,0.2);border:none;color:#fff;border-radius:8px;padding:5px 10px;font-size:12px;font-weight:700;cursor:pointer">Tozalash</button>
  </div>
  <div class="cart-list" id="cart-list"></div>
  <div class="summary-card" id="summary-card" style="display:none">
    <div class="sum-row"><span>Mahsulotlar</span><span id="sum-subtotal"></span></div>
    <div class="sum-total"><span>Jami to'lov</span><span id="sum-total" style="color:#e8000a"></span></div>
  </div>
  <button class="order-btn" onclick="placeOrder()">✅ BUYURTMA BERISH</button>
</div>

<!-- CART BAR -->
<div class="cart-bar hidden" id="cart-bar" onclick="showPage('cart')">
  <span>🛒</span>
  <span class="cart-count-badge" id="cart-badge">0</span>
  <span class="cart-total-text" id="cart-bar-total">Savatni ko'rish</span>
  <span style="font-size:18px">→</span>
</div>

<script>
const tg = window.Telegram && window.Telegram.WebApp;
if(tg){ tg.ready(); tg.expand(); }

const PRODUCTS = [
  {id:1, name:"Un vishi", price:10000, stock:50, cat:"Highlights", emoji:"🌾"},
  {id:2, name:"Soya sous 500ml", price:10000, stock:30, cat:"Soya sous", emoji:"🫙"},
  {id:3, name:"Jets shaqalod", price:25000, stock:40, cat:"Shoqolad", emoji:"🍫"},
  {id:4, name:"Jazzi shaqalod", price:28000, stock:25, cat:"Shoqolad", emoji:"🍬"},
  {id:5, name:"Slivka qrem", price:35000, stock:15, cat:"Sut mahsulotlari", emoji:"🥛"},
  {id:6, name:"Asal 7l", price:110000, stock:8, cat:"Asal", emoji:"🍯"},
  {id:7, name:"Milter bedan", price:20000, stock:18, cat:"Sut mahsulotlari", emoji:"🍮"},
  {id:8, name:"Maloko elit", price:18000, stock:44, cat:"Sut mahsulotlari", emoji:"🥛"},
];

const CATS = ["Hammasi", ...new Set(PRODUCTS.map(p => p.cat))];
let activeCat = "Hammasi";
let cart = {};

function fmt(n){ return n.toLocaleString() + " so'm"; }

function renderCats(){
  document.getElementById("cats-container").innerHTML = CATS.map(c =>
    `<button class="cat ${c===activeCat?'active':''}" onclick="setCat('${c}')">${c}</button>`
  ).join("");
}

function setCat(cat){
  activeCat = cat;
  renderCats();
  renderProducts();
}

function renderProducts(){
  const list = activeCat==="Hammasi" ? PRODUCTS : PRODUCTS.filter(p => p.cat===activeCat);
  if(list.length===0){
    document.getElementById("products-container").innerHTML = '<div style="text-align:center;padding:40px;color:#94a3b8">Mahsulot topilmadi</div>';
    return;
  }
  document.getElementById("products-container").innerHTML = list.map(p => {
    const inCart = cart[p.id];
    return `<div class="product">
      <div class="prod-img">${p.emoji}</div>
      <div class="prod-info">
        <div class="prod-name">${p.name}</div>
        <div class="prod-price">${fmt(p.price)}</div>
        <div class="prod-stock">Mavjud: ${p.stock} dona</div>
      </div>
      <button class="add-btn ${inCart?'added':''}" onclick="addToCart(${p.id})">
        ${inCart ? '✓ '+inCart.qty+' ta' : '+ Qo\'shish'}
      </button>
    </div>`;
  }).join("");
}

function addToCart(id){
  const p = PRODUCTS.find(x => x.id===id);
  if(!p) return;
  if(cart[id]) cart[id].qty++;
  else cart[id] = {...p, qty:1};
  updateCartBar();
  renderProducts();
}

function updateCartBar(){
  const items = Object.values(cart);
  const count = items.reduce((s,i) => s+i.qty, 0);
  const total = items.reduce((s,i) => s+i.price*i.qty, 0);
  const bar = document.getElementById("cart-bar");
  if(count===0){ bar.classList.add("hidden"); return; }
  bar.classList.remove("hidden");
  document.getElementById("cart-badge").textContent = count;
  document.getElementById("cart-bar-total").textContent = fmt(total);
}

function renderCart(){
  const items = Object.values(cart);
  const total = items.reduce((s,i) => s+i.price*i.qty, 0);
  document.getElementById("cart-subtitle").textContent = items.reduce((s,i)=>s+i.qty,0) + " ta mahsulot";
  if(items.length===0){
    document.getElementById("cart-list").innerHTML = `
      <div class="empty-state">
        <div>🛒</div>
        <div>Savat bo'sh</div>
        <div style="font-size:14px;color:#94a3b8">Katalogdan mahsulot qo'shing</div>
        <button class="go-btn" onclick="showPage('catalog')">Xarid qilish</button>
      </div>`;
    document.getElementById("summary-card").style.display="none";
    return;
  }
  document.getElementById("cart-list").innerHTML = items.map(i => `
    <div class="cart-item">
      <div class="cart-emoji">${i.emoji}</div>
      <div style="flex:1;min-width:0">
        <div style="font-weight:700;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${i.name}</div>
        <div style="font-size:13px;color:#e8000a;font-weight:700;margin-top:2px">${fmt(i.price*i.qty)}</div>
      </div>
      <div class="qty-row">
        <button class="qty-btn" onclick="changeQty(${i.id},-1)">−</button>
        <span class="qty-num">${i.qty}</span>
        <button class="qty-btn" onclick="changeQty(${i.id},1)">+</button>
      </div>
    </div>
  `).join("");
  document.getElementById("sum-subtotal").textContent = fmt(total);
  document.getElementById("sum-total").textContent = fmt(total);
  document.getElementById("summary-card").style.display="block";
}

function changeQty(id, d){
  if(!cart[id]) return;
  cart[id].qty += d;
  if(cart[id].qty <= 0) delete cart[id];
  updateCartBar();
  renderCart();
  renderProducts();
}

function clearCart(){
  cart = {};
  updateCartBar();
  renderCart();
  renderProducts();
}

function showPage(name){
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.getElementById(name+"-page").classList.add("active");
  if(name==="cart") renderCart();
}

function placeOrder(){
  const items = Object.values(cart);
  if(items.length===0){ alert("Savat bo'sh!"); return; }
  const total = items.reduce((s,i) => s+i.price*i.qty, 0);
  let text = "🛍 Yangi buyurtma!\n\n📦 Mahsulotlar:\n";
  items.forEach(i => { text += `• ${i.name} x${i.qty} = ${fmt(i.price*i.qty)}\n`; });
  text += `\n💰 Jami: ${fmt(total)}`;
  if(tg && tg.sendData){ tg.sendData(text); tg.close(); }
  else { alert("Buyurtma yuborildi!\n\n"+text); }
}

renderCats();
renderProducts();
</script>
</body>
</html>
