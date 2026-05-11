import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.filters import CommandStart
from aiogram.types import Update

TOKEN = os.environ.get("TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "998972030307"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8000))

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

carts = {}

products = [
    {"id": 1, "name": "Un vishi",       "price": 10000,  "stock": 50, "cat": "Un"},
    {"id": 2, "name": "Soya sous",      "price": 10000,  "stock": 30, "cat": "Sous"},
    {"id": 3, "name": "Jets shaqalod",  "price": 25000,  "stock": 20, "cat": "Shaqalod"},
    {"id": 4, "name": "Jazzi shaqalod", "price": 28000,  "stock": 15, "cat": "Shaqalod"},
    {"id": 5, "name": "Slivka qrem",    "price": 35000,  "stock": 10, "cat": "Qrem"},
    {"id": 6, "name": "Asal 7l",        "price": 110000, "stock": 8,  "cat": "Asal"},
]

def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Katalog"), KeyboardButton(text="Savat")],
            [KeyboardButton(text="Aloqa")]
        ],
        resize_keyboard=True
    )

@router.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer("XASANBOY OPTOM\nXush kelibsiz!", reply_markup=main_kb())

@router.message(F.text == "Katalog")
async def catalog(m: Message):
    cats = list(dict.fromkeys(p["cat"] for p in products))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data="c_" + cat)]
        for cat in cats
    ])
    await m.answer("Kategoriya tanlang:", reply_markup=kb)

@router.callback_query(F.data.startswith("c_"))
async def show_cat(call: CallbackQuery):
    cat = call.data[2:]
    items = [p for p in products if p["cat"] == cat]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=p["name"], callback_data="p_" + str(p["id"]))]
        for p in items
    ] + [[InlineKeyboardButton(text="Orqaga", callback_data="back")]])
    await call.message.edit_text(cat, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data == "back")
async def back(call: CallbackQuery):
    cats = list(dict.fromkeys(p["cat"] for p in products))
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat, callback_data="c_" + cat)]
        for cat in cats
    ])
    await call.message.edit_text("Kategoriya tanlang:", reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("p_"))
async def show_product(call: CallbackQuery):
    pid = int(call.data[2:])
    p = next((x for x in products if x["id"] == pid), None)
    if not p:
        await call.answer("Topilmadi!")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Savatga qosh", callback_data="add_" + str(pid))],
        [InlineKeyboardButton(text="Orqaga", callback_data="c_" + p["cat"])]
    ])
    text = p["name"] + "\nNarx: " + str(p["price"]) + " som\nMavjud: " + str(p["stock"]) + " ta"
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()

@router.callback_query(F.data.startswith("add_"))
async def add_to_cart(call: CallbackQuery):
    uid = call.from_user.id
    pid = int(call.data[4:])
    carts.setdefault(uid, {})
    carts[uid][pid] = carts[uid].get(pid, 0) + 1
    p = next((x for x in products if x["id"] == pid), None)
    await call.answer(p["name"] + " savatga qoshildi!")

@router.message(F.text == "Savat")
async def show_cart(m: Message):
    uid = m.from_user.id
    cart = carts.get(uid, {})
    if not cart:
        await m.answer("Savat bosh!")
        return
    text = "Savatingiz:\n\n"
    total = 0
    for pid, qty in cart.items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            summa = p["price"] * qty
            total += summa
            text += "- " + p["name"] + " x" + str(qty) + " = " + str(summa) + " som\n"
    text += "\nJami: " + str(total) + " som"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Buyurtma berish", callback_data="order")],
        [InlineKeyboardButton(text="Savatni tozalash", callback_data="clear")]
    ])
    await m.answer(text, reply_markup=kb)

@router.callback_query(F.data == "clear")
async def clear_cart(call: CallbackQuery):
    carts[call.from_user.id] = {}
    await call.message.edit_text("Savat tozalandi!")
    await call.answer()

@router.callback_query(F.data == "order")
async def place_order(call: CallbackQuery):
    uid = call.from_user.id
    cart = carts.get(uid, {})
    if not cart:
        await call.answer("Savat bosh!")
        return
    text = "Yangi buyurtma!\nFoydalanuvchi ID: " + str(uid) + "\n\nMahsulotlar:\n"
    total = 0
    for pid, qty in cart.items():
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            summa = p["price"] * qty
            total += summa
            text += "- " + p["name"] + " x" + str(qty) + " = " + str(summa) + " som\n"
    text += "\nJami: " + str(total) + " som"
    await bot.send_message(ADMIN_ID, text)
    carts[uid] = {}
    await call.message.edit_text("Buyurtmangiz qabul qilindi!")
    await call.answer()

@router.message(F.text == "Aloqa")
async def contact(m: Message):
    await m.answer("Aloqa: @Xasanboy_produkt\nTel: +998972030307")

async def webhook_handler(request: web.Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(text="OK")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL + "/webhook")

    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
