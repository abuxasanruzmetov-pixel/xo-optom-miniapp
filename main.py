from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
from database import get_db, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="XO Optom Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Database initialized")

# ===== SCHEMAS =====
class CategoryCreate(BaseModel):
    name: str
    emoji: Optional[str] = ""

class ProductCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = ""
    price: float
    old_price: Optional[float] = 0
    stock: Optional[int] = 0
    image_url: Optional[str] = ""

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    old_price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[int] = None

class CartItem(BaseModel):
    user_id: int
    product_id: int
    quantity: Optional[int] = 1

class OrderCreate(BaseModel):
    user_id: int
    items: List[dict]
    address: Optional[str] = ""
    phone: Optional[str] = ""
    promo_code: Optional[str] = ""

class UserCreate(BaseModel):
    telegram_id: int
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    username: Optional[str] = ""
    phone: Optional[str] = ""

class PromoCreate(BaseModel):
    code: str
    discount_percent: float
    usage_limit: Optional[int] = 100

# ===== CATEGORIES =====
@app.get("/api/categories")
async def get_categories():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM categories ORDER BY id")
    cats = [dict(row) for row in c.fetchall()]
    conn.close()
    return cats

@app.post("/api/categories")
async def create_category(cat: CategoryCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (cat.name, cat.emoji))
    conn.commit()
    cat_id = c.lastrowid
    conn.close()
    return {"id": cat_id, "name": cat.name, "emoji": cat.emoji}

@app.delete("/api/categories/{cat_id}")
async def delete_category(cat_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ===== PRODUCTS =====
@app.get("/api/products")
async def get_products(category_id: Optional[int] = None):
    conn = get_db()
    c = conn.cursor()
    if category_id:
        c.execute("SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.category_id=? AND p.is_active=1 ORDER BY p.id DESC", (category_id,))
    else:
        c.execute("SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.is_active=1 ORDER BY p.id DESC")
    products = [dict(row) for row in c.fetchall()]
    conn.close()
    return products

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT p.*, c.name as category_name FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE p.id=?", (product_id,))
    product = c.fetchone()
    conn.close()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(product)

@app.post("/api/products")
async def create_product(product: ProductCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO products (category_id, name, description, price, old_price, stock, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (product.category_id, product.name, product.description, product.price, product.old_price, product.stock, product.image_url)
    )
    conn.commit()
    prod_id = c.lastrowid
    conn.close()
    return {"id": prod_id, **product.dict()}

@app.put("/api/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    conn = get_db()
    c = conn.cursor()
    updates = {k: v for k, v in product.dict().items() if v is not None}
    if updates:
        set_clause = ", ".join([f"{k}=?" for k in updates.keys()])
        c.execute(f"UPDATE products SET {set_clause} WHERE id=?", list(updates.values()) + [product_id])
        conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE products SET is_active=0 WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ===== USERS =====
@app.post("/api/users")
async def create_or_update_user(user: UserCreate):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE telegram_id=?", (user.telegram_id,))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE users SET first_name=?, last_name=?, username=? WHERE telegram_id=?",
                  (user.first_name, user.last_name, user.username, user.telegram_id))
        user_id = existing['id']
    else:
        c.execute("INSERT INTO users (telegram_id, first_name, last_name, username, phone) VALUES (?, ?, ?, ?, ?)",
                  (user.telegram_id, user.first_name, user.last_name, user.username, user.phone))
        user_id = c.lastrowid
    conn.commit()
    conn.close()
    return {"id": user_id, "telegram_id": user.telegram_id}

@app.get("/api/users/{telegram_id}")
async def get_user(telegram_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE telegram_id=?", (telegram_id,))
    user = c.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

# ===== CART =====
@app.get("/api/cart/{user_id}")
async def get_cart(user_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT cart.id, cart.quantity, products.id as product_id,
                 products.name, products.price, products.image_url, products.stock
                 FROM cart
                 JOIN products ON cart.product_id = products.id
                 WHERE cart.user_id=?""", (user_id,))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

@app.post("/api/cart")
async def add_to_cart(item: CartItem):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, quantity FROM cart WHERE user_id=? AND product_id=?", (item.user_id, item.product_id))
    existing = c.fetchone()
    if existing:
        c.execute("UPDATE cart SET quantity=quantity+? WHERE id=?", (item.quantity, existing['id']))
    else:
        c.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                  (item.user_id, item.product_id, item.quantity))
    conn.commit()
    conn.close()
    return {"success": True}

@app.put("/api/cart/{cart_id}")
async def update_cart(cart_id: int, quantity: int):
    conn = get_db()
    c = conn.cursor()
    if quantity <= 0:
        c.execute("DELETE FROM cart WHERE id=?", (cart_id,))
    else:
        c.execute("UPDATE cart SET quantity=? WHERE id=?", (quantity, cart_id))
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/cart/{user_id}")
async def clear_cart(user_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ===== FAVORITES =====
@app.get("/api/favorites/{user_id}")
async def get_favorites(user_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("""SELECT favorites.id, products.id as product_id,
                 products.name, products.price, products.old_price, products.image_url
                 FROM favorites
                 JOIN products ON favorites.product_id = products.id
                 WHERE favorites.user_id=?""", (user_id,))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

@app.post("/api/favorites")
async def toggle_favorite(user_id: int, product_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM favorites WHERE user_id=? AND product_id=?", (user_id, product_id))
    existing = c.fetchone()
    if existing:
        c.execute("DELETE FROM favorites WHERE id=?", (existing['id'],))
        conn.commit()
        conn.close()
        return {"added": False}
    else:
        c.execute("INSERT INTO favorites (user_id, product_id) VALUES (?, ?)", (user_id, product_id))
        conn.commit()
        conn.close()
        return {"added": True}

# ===== ORDERS =====
@app.post("/api/orders")
async def create_order(order: OrderCreate):
    conn = get_db()
    c = conn.cursor()
    
    discount = 0
    if order.promo_code:
        c.execute("SELECT * FROM promo_codes WHERE code=? AND is_active=1", (order.promo_code,))
        promo = c.fetchone()
        if promo and promo['used_count'] < promo['usage_limit']:
            discount = promo['discount_percent']
            c.execute("UPDATE promo_codes SET used_count=used_count+1 WHERE id=?", (promo['id'],))
    
    total = sum(item['price'] * item['quantity'] for item in order.items)
    total = total * (1 - discount / 100)
    
    c.execute("INSERT INTO orders (user_id, total_price, address, phone, promo_code, discount) VALUES (?, ?, ?, ?, ?, ?)",
              (order.user_id, total, order.address, order.phone, order.promo_code, discount))
    order_id = c.lastrowid
    
    for item in order.items:
        c.execute("INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                  (order_id, item['product_id'], item['quantity'], item['price']))
    
    c.execute("DELETE FROM cart WHERE user_id=?", (order.user_id,))
    conn.commit()
    conn.close()
    return {"order_id": order_id, "total": total, "discount": discount}

@app.get("/api/orders/{user_id}")
async def get_user_orders(user_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    orders = [dict(row) for row in c.fetchall()]
    for order in orders:
        c.execute("""SELECT oi.*, p.name, p.image_url FROM order_items oi
                     JOIN products p ON oi.product_id=p.id
                     WHERE oi.order_id=?""", (order['id'],))
        order['items'] = [dict(row) for row in c.fetchall()]
    conn.close()
    return orders

@app.get("/api/admin/orders")
async def get_all_orders(status: Optional[str] = None):
    conn = get_db()
    c = conn.cursor()
    if status:
        c.execute("""SELECT o.*, u.first_name, u.username FROM orders o
                     LEFT JOIN users u ON o.user_id=u.id
                     WHERE o.status=? ORDER BY o.created_at DESC""", (status,))
    else:
        c.execute("""SELECT o.*, u.first_name, u.username FROM orders o
                     LEFT JOIN users u ON o.user_id=u.id
                     ORDER BY o.created_at DESC""")
    orders = [dict(row) for row in c.fetchall()]
    for order in orders:
        c.execute("""SELECT oi.*, p.name FROM order_items oi
                     JOIN products p ON oi.product_id=p.id
                     WHERE oi.order_id=?""", (order['id'],))
        order['items'] = [dict(row) for row in c.fetchall()]
    conn.close()
    return orders

@app.put("/api/admin/orders/{order_id}")
async def update_order_status(order_id: int, status: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE orders SET status=? WHERE id=?", (status, order_id))
    conn.commit()
    conn.close()
    return {"success": True}

# ===== PROMO CODES =====
@app.post("/api/promo")
async def create_promo(promo: PromoCreate):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO promo_codes (code, discount_percent, usage_limit) VALUES (?, ?, ?)",
                  (promo.code, promo.discount_percent, promo.usage_limit))
        conn.commit()
        conn.close()
        return {"success": True}
    except:
        conn.close()
        raise HTTPException(status_code=400, detail="Promo code already exists")

@app.get("/api/promo/{code}")
async def check_promo(code: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM promo_codes WHERE code=? AND is_active=1", (code,))
    promo = c.fetchone()
    conn.close()
    if not promo:
        raise HTTPException(status_code=404, detail="Invalid promo code")
    if promo['used_count'] >= promo['usage_limit']:
        raise HTTPException(status_code=400, detail="Promo code expired")
    return {"discount_percent": promo['discount_percent']}

# ===== STATS =====
@app.get("/api/admin/stats")
async def get_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM orders")
    total_orders = c.fetchone()['total']
    c.execute("SELECT COUNT(*) as total FROM orders WHERE status='new'")
    new_orders = c.fetchone()['total']
    c.execute("SELECT COALESCE(SUM(total_price), 0) as total FROM orders WHERE status='done'")
    revenue = c.fetchone()['total']
    c.execute("SELECT COUNT(*) as total FROM users")
    total_users = c.fetchone()['total']
    c.execute("SELECT COUNT(*) as total FROM products WHERE is_active=1")
    total_products = c.fetchone()['total']
    conn.close()
    return {
        "total_orders": total_orders,
        "new_orders": new_orders,
        "revenue": revenue,
        "total_users": total_users,
        "total_products": total_products
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
