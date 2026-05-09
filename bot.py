import os
import telebot
from telebot import types

import os
TOKEN = os.environ.get("TOKEN")
ADMIN_ID = 998972030307

bot = telebot.TeleBot(TOKEN)
telebot.apihelper.READ_TIMEOUT = 60
telebot.apihelper.CONNECT_TIMEOUT = 30

carts = {}
products = [
    {"id":1,"name":"Un vishi","price":10000,"stock":50,"cat":"Un"},
    {"id":2,"name":"Soya sous","price":10000,"stock":30,"cat":"Sous"},
    {"id":3,"name":"Jets shaqalod","price":25000,"stock":20,"cat":"Shaqalod"},
    {"id":4,"name":"Jazzi shaqalod","price":28000,"stock":15,"cat":"Shaqalod"},
    {"id":5,"name":"Slivka qrem","price":35000,"stock":10,"cat":"Qrem"},
    {"id":6,"name":"Asal 7l","price":110000,"stock":8,"cat":"Asal"},
]

def mkb():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("Katalog", "Savat")
    kb.row("Aloqa")
    return kb@bot.message_handler(commands=["start"])
def start(m):
    bot.send_message(m.chat.id, "XASANBOY OPTOM\nXush kelibsiz!", reply_markup=mkb())

@bot.message_handler(func=lambda m: m.text == "Katalog")
def catalog(m):
    kb = types.InlineKeyboardMarkup()
    cats = list(set(p["cat"] for p in products))
    for cat in cats:
        kb.add(types.InlineKeyboardButton(cat, callback_data="c_" + cat))
    bot.send_message(m.chat.id, "Kategoriya tanlang:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("c_"))
def show_cat(call):
    cat = call.data[2:]
    kb = types.InlineKeyboardMarkup()
    for p in [x for x in products if x["cat"] == cat]:
        kb.add(types.InlineKeyboardButton(p["name"], callback_data="p_" + str(p["id"])))
    kb.add(types.InlineKeyboardButton("Orqaga", callback_data="back"))
    bot.edit_message_text(cat, call.message.chat.id, call.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):
    kb = types.InlineKeyboardMarkup()
    cats = list(set(p["cat"] for p in products))
    for cat in cats:
        kb.add(types.InlineKeyboardButton(cat, callback_data="c_" + cat))
    bot.edit_message_text("Kategoriya tanlang:", call.message.chat.id, call.message.message_id, reply_markup=kb)
@bot.callback_query_handler(func=lambda c: c.data.startswith("p_"))
def show_p(call):
    pid = int(call.data[2:])
    p = next((x for x in products if x["id"] == pid), None)
    if not p:
        return
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("-", callback_data="minus_"+str(pid)),
        types.InlineKeyboardButton("1", callback_data="qty_"+str(pid)),
        types.InlineKeyboardButton("+", callback_data="plus_"+str(pid))
    )
    kb.add(types.InlineKeyboardButton("Savatga qosh", callback_data="add_"+str(pid)))
    kb.add(types.InlineKeyboardButton("Orqaga", callback_data="c_"+p["cat"]))
    text = p["name"]+"\nNarx: "+str(p["price"])+" som\nMavjud: "+str(p["stock"])+" ta"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("add_"))
def add_cart(call):
    uid = call.from_user.id
    pid = int(call.data[4:])
    if uid not in carts:
        carts[uid] = {}
    carts[uid][pid] = carts[uid].get(pid, 0) + 1
    p = next((x for x in products if x["id"] == pid), None)
    bot.answer_callback_query(call.id, p["name"]+" savatga qoshildi!")
@bot.message_handler(func=lambda m: m.text == "Savat")
def show_cart(m):
    uid = m.from_user.id
    if uid not in carts or not carts[uid]:
        bot.send_message(m.chat.id, "Savat bosh!")
        return
    text = "Savatingiz:\n"
    total = 0
    kb = types.InlineKeyboardMarkup()
    for pid, qty in carts[uid].items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            summa = p["price"] * qty
            total += summa
            text += "- "+p["name"]+" x"+str(qty)+" = "+str(summa)+" som\n"
    text += "\nJami: "+str(total)+" som"
    kb.add(types.InlineKeyboardButton("Buyurtma berish", callback_data="order"))
    kb.add(types.InlineKeyboardButton("Savatni tozalash", callback_data="clear"))
    bot.send_message(m.chat.id, text, reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data == "clear")
def clear_cart(call):
    carts[call.from_user.id] = {}
    bot.edit_message_text("Savat tozalandi!", call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda c: c.data == "order")
def order(call):
    uid = call.from_user.id
    if uid not in carts or not carts[uid]:
        return
    text = "Yangi buyurtma!\nFoydalanuvchi: "+str(uid)+"\n\n"
    total = 0
    for pid, qty in carts[uid].items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            summa = p["price"] * qty
            total += summa
            text += "- "+p["name"]+" x"+str(qty)+" = "+str(summa)+" som\n"
    text += "\nJami: "+str(total)+" som"
    bot.send_message(ADMIN_ID, text)
    carts[uid] = {}
    bot.edit_message_text("Buyurtma qabul qilindi!", call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "Aloqa")
def contact(m):
    bot.send_message(m.chat.id, "Aloqa: @Xasanboy_produkt\nTel: +998972030307")

bot.polling(none_stop=True)
