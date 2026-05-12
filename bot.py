import os
import logging
import telebot
from telebot import types
from flask import Flask, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "998972030307"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
PORT = int(os.environ.get("PORT", 8080))

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

carts = {}

products = [
    {"id": 1, "name": "Un vishi",       "price": 10000,  "stock": 50, "cat": "Un"},
    {"id": 2, "name": "Soya sousi",     "price": 10000,  "stock": 30, "cat": "Sous"},
    {"id": 3, "name": "Jets shokolad",  "price": 25000,  "stock": 20, "cat": "Shokolad"},
    {"id": 4, "name": "Jazzi shokolad", "price": 28000,  "stock": 15, "cat": "Shokolad"},
    {"id": 5, "name": "Slivka qrem",    "price": 35000,  "stock": 10, "cat": "Qrem"},
    {"id": 6, "name": "Asal 7l",        "price": 110000, "stock": 8,  "cat": "Asal"},
]


def main_kb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("\U0001f4cb Katalog", "\U0001f6d2 Savat")
    kb.row("\U0001f4de Aloqa")
    return kb


@bot.message_handler(commands=["start"])
def start(m):
    text = "\U0001f44b XASANBOY OPTOM ga xush kelibsiz!\n\nBiz ulgurji savdo bilan shug'ullanamiz."
    bot.send_message(m.chat.id, text, reply_markup=main_kb())


@bot.message_handler(func=lambda m: m.text and "Katalog" in m.text)
def katalog(m):
    cats = list(dict.fromkeys(p["cat"] for p in products))
    kb = types.InlineKeyboardMarkup()
    for cat in cats:
        kb.add(types.InlineKeyboardButton(cat, callback_data="c_" + cat))
    bot.send_message(m.chat.id, "\U0001f4c2 Kategoriya tanlang:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data.startswith("c_"))
def show_cat(call):
    cat = call.data[2:]
    items = [p for p in products if p["cat"] == cat]
    kb = types.InlineKeyboardMarkup()
    for p in items:
        kb.add(types.InlineKeyboardButton(
            f"{p['name']} - {p['price']:,} so'm",
            callback_data="p_" + str(p["id"])
        ))
    kb.add(types.InlineKeyboardButton("\U00002b05 Orqaga", callback_data="back"))
    try:
        bot.edit_message_text(
            f"\U0001f4c2 {cat} mahsulotlari:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=kb
        )
    except Exception:
        bot.send_message(call.message.chat.id, f"\U0001f4c2 {cat} mahsulotlari:", reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):
    cats = list(dict.fromkeys(p["cat"] for p in products))
    kb = types.InlineKeyboardMarkup()
    for cat in cats:
        kb.add(types.InlineKeyboardButton(cat, callback_data="c_" + cat))
    try:
        bot.edit_message_text("\U0001f4c2 Kategoriya tanlang:", call.message.chat.id, call.message.message_id, reply_markup=kb)
    except Exception:
        bot.send_message(call.message.chat.id, "\U0001f4c2 Kategoriya tanlang:", reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("p_"))
def show_product(call):
    pid = int(call.data[2:])
    p = next((x for x in products if x["id"] == pid), None)
    if not p:
        bot.answer_callback_query(call.id, "Mahsulot topilmadi")
        return
    text = (
        f"\U0001f6cd {p['name']}\n"
        f"\U0001f4b0 Narx: {p['price']:,} so'm\n"
        f"\U0001f4e6 Zaxira: {p['stock']} dona"
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        "\U0001f6d2 Savatga qo'shish",
        callback_data=f"add_{pid}"
    ))
    kb.add(types.InlineKeyboardButton("\U00002b05 Orqaga", callback_data="c_" + p["cat"]))
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=kb)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith("add_"))
def add_to_cart(call):
    pid = int(call.data[4:])
    uid = call.from_user.id
    if uid not in carts:
        carts[uid] = {}
    carts[uid][pid] = carts[uid].get(pid, 0) + 1
    p = next((x for x in products if x["id"] == pid), None)
    name = p["name"] if p else "Mahsulot"
    bot.answer_callback_query(call.id, f"\U00002705 {name} savatga qo'shildi!")


@bot.message_handler(func=lambda m: m.text and "Savat" in m.text)
def show_cart(m):
    uid = m.chat.id
    cart = carts.get(uid, {})
    if not cart:
        bot.send_message(uid, "\U0001f6d2 Savat bo'sh.\n\nKatalogdan mahsulot tanlang!")
        return
    total = 0
    lines = []
    for pid, qty in cart.items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            subtotal = p["price"] * qty
            total += subtotal
            lines.append(f"• {p['name']} x{qty} = {subtotal:,} so'm")
    text = "\U0001f6d2 Savatingiz:\n\n" + "\n".join(lines) + f"\n\n\U0001f4b0 Jami: {total:,} so'm"
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("\U00002705 Buyurtma berish", callback_data="order"),
        types.InlineKeyboardButton("\U0000274c Tozalash", callback_data="clear")
    )
    bot.send_message(uid, text, reply_markup=kb)


@bot.callback_query_handler(func=lambda c: c.data == "clear")
def clear_cart(call):
    carts.pop(call.from_user.id, None)
    try:
        bot.edit_message_text("\U0001f6d2 Savat tozalandi.", call.message.chat.id, call.message.message_id)
    except Exception:
        bot.send_message(call.message.chat.id, "\U0001f6d2 Savat tozalandi.")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data == "order")
def place_order(call):
    uid = call.from_user.id
    cart = carts.get(uid, {})
    if not cart:
        bot.answer_callback_query(call.id, "Savat bo'sh!")
        return
    total = 0
    lines = []
    for pid, qty in cart.items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            subtotal = p["price"] * qty
            total += subtotal
            lines.append(f"{p['name']} x{qty} = {subtotal:,} so'm")
    user = call.from_user
    fname = user.first_name or ""
    lname = user.last_name or ""
    uname = "@" + user.username if user.username else "yo'q"
    admin_text = (
        f"\U0001f6d2 YANGI BUYURTMA\n"
        f"Mijoz: {fname} {lname}\n"
        f"Username: {uname}\n"
        f"ID: {uid}\n\n"
        + "\n".join(lines)
        + f"\n\nJami: {total:,} so'm"
    )
    try:
        bot.send_message(ADMIN_ID, admin_text)
        logger.info(f"Admin ga buyurtma yuborildi: {uid}")
    except Exception as e:
        logger.error(f"Admin xabar xatosi: {e}")
    carts.pop(uid, None)
    try:
        bot.edit_message_text(
            "\U00002705 Buyurtmangiz qabul qilindi!\n\nTez orada siz bilan bog'lanamiz.",
            call.message.chat.id,
            call.message.message_id
        )
    except Exception:
        bot.send_message(call.message.chat.id, "\U00002705 Buyurtmangiz qabul qilindi!")
    bot.answer_callback_query(call.id, "Buyurtma qabul!")


@bot.message_handler(func=lambda m: m.text and "Aloqa" in m.text)
def contact(m):
    text = "\U0001f4de Bog'lanish uchun:\n\n@xasanboy_optom\nTel: +998972030307"
    bot.send_message(m.chat.id, text)


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        json_data = request.get_json(force=True)
        if json_data:
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
    except Exception as e:
        logger.error(f"Webhook xatosi: {e}")
    return "OK", 200


@app.route("/")
def index():
    return f"Bot ishlayapti! Webhook: {WEBHOOK_URL}/webhook", 200


if __name__ == "__main__":
    logger.info(f"Bot ishga tushmoqda... PORT={PORT}, WEBHOOK_URL={WEBHOOK_URL}")
    if WEBHOOK_URL:
        try:
            bot.remove_webhook()
            import time
            time.sleep(1)
            bot.set_webhook(url=WEBHOOK_URL + "/webhook")
            logger.info(f"Webhook o'rnatildi: {WEBHOOK_URL}/webhook")
        except Exception as e:
            logger.error(f"Webhook o'rnatish xatosi: {e}")
    else:
        logger.warning("WEBHOOK_URL yo'q! Polling rejimida ishga tushirilmoqda...")
        import threading
        t = threading.Thread(target=lambda: bot.polling(none_stop=True, interval=0))
        t.daemon = True
        t.start()
    app.run(host="0.0.0.0", port=PORT, debug=False)
