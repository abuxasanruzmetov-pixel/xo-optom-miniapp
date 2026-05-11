import os
import telebot
from telebot import types
from flask import Flask, request

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "998972030307"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", 8000))

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

carts = {}

products = [
    {"id": 1, "name": "Un vishi",      "price": 10000,  "stock": 50, "cat": "Un"},
    {"id": 2, "name": "Soya sousi",    "price": 10000,  "stock": 30, "cat": "Sous"},
    {"id": 3, "name": "Jets shokolad", "price": 25000,  "stock": 20, "cat": "Shokolad"},
    {"id": 4, "name": "Jazzi shokolad","price": 28000,  "stock": 15, "cat": "Shokolad"},
    {"id": 5, "name": "Slivka qrem",   "price": 35000,  "stock": 10, "cat": "Qrem"},
    {"id": 6, "name": "Asal 7l",       "price": 110000, "stock": 8,  "cat": "Asal"},
]


def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Katalog", "Savat")
    kb.row("Aloqa")
    return kb


@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "XASANBOY OPTOM\nXush kelibsiz!", reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text == "Katalog")
def katalog(m):
    cats = list(dict.fromkeys(p["cat"] for p in products))
    kb = types.InlineKeyboardMarkup()
    for cat in cats:
        kb.add(types.InlineKeyboardButton(cat, callback_data="c_" + cat))
    bot.send_message(m.chat.id, "Kategoriya tanlang:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("c_"))
def show_cat(call):
    cat = call.data[2:]
    items = [p for p in products if p["cat"] == cat]
    kb = types.InlineKeyboardMarkup()
    for p in items:
        kb.add(types.InlineKeyboardButton(p["name"], callback_data="p_" + str(p["id"])))
    kb.add(types.InlineKeyboardButton("Orqaga", callback_data="back"))
    bot.edit_message_text(cat, call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):
    cats = list(dict.fromkeys(p["cat"] for p in products))
    kb = types.InlineKeyboardMarkup()
    for cat in cats:
        kb.add(types.InlineKeyboardButton(cat, callback_data="c_" + cat))
    bot.edit_message_text("Kategoriya tanlang:", call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("p_"))
def show_product(call):
    pid = int(call.data[2:])
    p = next((x for x in products if x["id"] == pid), None)
    if not p:
        bot.answer_callback_query(call.id, "Topilmadi")
        return
    text = f"{p['name']}\nNarx: {p['price']:,} so'm\nZaxira: {p['stock']} dona"
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("-", callback_data=f"minus_{pid}"),
        types.InlineKeyboardButton("Savatga", callback_data=f"add_{pid}"),
        types.InlineKeyboardButton("+", callback_data=f"plus_{pid}")
    )
    kb.add(types.InlineKeyboardButton("Orqaga", callback_data="c_" + p["cat"]))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("add_"))
def add_to_cart(call):
    pid = int(call.data[4:])
    uid = call.from_user.id
    if uid not in carts:
        carts[uid] = {}
    carts[uid][pid] = carts[uid].get(pid, 0) + 1
    bot.answer_callback_query(call.id, "Savatga qo'shildi!")


@bot.message_handler(func=lambda m: m.text == "Savat")
def show_cart(m):
    uid = m.chat.id
    cart = carts.get(uid, {})
    if not cart:
        bot.send_message(uid, "Savat bo'sh.")
        return
    total = 0
    lines = []
    for pid, qty in cart.items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            subtotal = p["price"] * qty
            total += subtotal
            lines.append(f"{p['name']} x{qty} = {subtotal:,} so'm")
    text = "\n".join(lines) + f"\n\nJami: {total:,} so'm"
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("Buyurtma berish", callback_data="order"),
        types.InlineKeyboardButton("Tozalash", callback_data="clear")
    )
    bot.send_message(uid, text, reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data == "clear")
def clear_cart(call):
    carts.pop(call.from_user.id, None)
    bot.edit_message_text("Savat tozalandi.", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "order")
def place_order(call):
    uid = call.from_user.id
    cart = carts.get(uid, {})
    if not cart:
        bot.answer_callback_query(call.id, "Savat bo'sh")
        return
    total = 0
    lines = []
    for pid, qty in cart.items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            subtotal = p["price"] * qty
            total += subtotal
            lines.append(f"{p['name']} x{qty} = {subtotal:,}")
    user = call.from_user
    name = (user.first_name or "") + " " + (user.last_name or "")
    username = "@" + user.username if user.username else "yo'q"
    admin_msg = f"YANGI BUYURTMA\nMijoz: {name.strip()}\nUsername: {username}\nID: {uid}\n\n" + "\n".join(lines) + f"\n\nJami: {total:,} so'm"
    try:
        bot.send_message(ADMIN_ID, admin_msg)
    except Exception as e:
        print(f"Admin xabar xatosi: {e}")
    carts.pop(uid, None)
    bot.edit_message_text("Buyurtmangiz qabul qilindi!", call.message.chat.id, call.message.message_id)
    bot.answer_callback_query(call.id, "Buyurtma qabul!")


@bot.message_handler(func=lambda m: m.text == "Aloqa")
def contact(m):
    bot.send_message(m.chat.id, "Bog'lanish uchun: @xasanboy_optom\nTel: +998901234567")


@app.route("/webhook", methods=["POST"])
def webhook():
    json_data = request.get_json(force=True)
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def index():
    return "Bot ishlayapti!", 200


if __name__ == "__main__":
    if WEBHOOK_URL:
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_URL + "/webhook")
        print(f"Webhook o'rnatildi: {WEBHOOK_URL}/webhook")
    else:
        print("WEBHOOK_URL yo'q, polling rejimda ishga tushirilmoqda...")
        import threading
        t = threading.Thread(target=lambda: bot.polling(none_stop=True))
        t.daemon = True
        t.start()
    app.run(host="0.0.0.0", port=PORT)
