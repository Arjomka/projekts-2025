from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties
import asyncio

BOT_TOKEN = "7572786254:AAHmgnb8uTXolh18hKwIcBJ3DX9doznAS6s"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# Главная клавиатура
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/new")],
        [KeyboardButton(text="/saved")],
        [KeyboardButton(text="/start")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Izvēlies komandu..."
)

class AddProduct(StatesGroup):
    entering_name = State()
    entering_macros = State()
    entering_weight = State()

class UserProfileSetup(StatesGroup):
    entering_height = State()
    entering_weight = State()
    entering_age = State()
    entering_fat = State()
    entering_activity = State()
    entering_goal = State()

user_profiles = {}
user_products = {}
user_daily_totals = {}

@dp.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    await message.answer("👤 Ievadīsim tavu profilu.\n📏 Ievadi savu augumu (cm):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserProfileSetup.entering_height)

@dp.message(UserProfileSetup.entering_height)
async def input_height(message: Message, state: FSMContext):
    try:
        height = float(message.text.strip())
        await state.update_data(height=height)
        await message.answer("⚖️ Ievadi savu svaru (kg):")
        await state.set_state(UserProfileSetup.entering_weight)
    except:
        await message.answer("❌ Lūdzu ievadi pareizu augumu (piemēram: 180)")

@dp.message(UserProfileSetup.entering_weight)
async def input_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.strip())
        await state.update_data(weight=weight)
        await message.answer("🎂 Ievadi savu vecumu:")
        await state.set_state(UserProfileSetup.entering_age)
    except:
        await message.answer("❌ Lūdzu ievadi pareizu svaru (piemēram: 75)")

@dp.message(UserProfileSetup.entering_age)
async def input_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        await state.update_data(age=age)
        await message.answer("📉 Ievadi savu ķermeņa tauku procentu (piemēram: 15):")
        await state.set_state(UserProfileSetup.entering_fat)
    except:
        await message.answer("❌ Lūdzu ievadi korektu vecumu")

@dp.message(UserProfileSetup.entering_fat)
async def input_fat(message: Message, state: FSMContext):
    try:
        fat = float(message.text.strip())
        await state.update_data(fat=fat)
        await message.answer(
            "🏃‍♂️ Izvēlies aktivitātes līmeni (ievadi ciparu):\n"
            "1. Sēdošs dzīvesveids\n"
            "2. Aktīvs bez treniņiem\n"
            "3. Treniņi 1 reizi nedēļā\n"
            "4. Treniņi 2-3 reizes nedēļā\n"
            "5. Treniņi 4-5 reizes nedēļā"
        )
        await state.set_state(UserProfileSetup.entering_activity)
    except:
        await message.answer("❌ Lūdzu ievadi tauku procentu korekti")

@dp.message(UserProfileSetup.entering_activity)
async def input_activity(message: Message, state: FSMContext):
    try:
        choice = int(message.text.strip())
        activity_map = {
            1: 1.2,
            2: 1.375,
            3: 1.55,
            4: 1.7,
            5: 1.9
        }
        factor = activity_map.get(choice)
        if not factor:
            raise ValueError

        await state.update_data(activity_factor=factor)
        await message.answer(
            "🎯 Kāds ir tavs mērķis? (ievadi ciparu):\n"
            "1. Zaudēt svaru\n"
            "2. Uzturēt svaru\n"
            "3. Palielināt svaru"
        )
        await state.set_state(UserProfileSetup.entering_goal)
    except:
        await message.answer("❌ Izvēlies no 1 līdz 5!")

@dp.message(UserProfileSetup.entering_goal)
async def input_goal(message: Message, state: FSMContext):
    try:
        goal_choice = int(message.text.strip())
        goal_modifier_map = {
            1: -300,
            2: 0,
            3: 300
        }
        goal_modifier = goal_modifier_map.get(goal_choice)
        if goal_modifier is None:
            raise ValueError

        await state.update_data(goal_modifier=goal_modifier)
        data = await state.get_data()

        lbm = data["weight"] * (1 - data["fat"] / 100)
        bmr = 370 + 21.6 * lbm
        tdee = bmr * data["activity_factor"] + goal_modifier

        protein = data["weight"] * 2.0
        fat = data["weight"] * 1.0
        remaining_calories = tdee - (protein * 4 + fat * 9)
        carbs = remaining_calories / 4

        user_id = message.from_user.id
        user_profiles[user_id] = {
            "kcal": tdee,
            "protein": protein,
            "fat": fat,
            "carbs": carbs
        }
        user_daily_totals[user_id] = {"p": 0, "f": 0, "c": 0}

        await message.answer(f"✅ Dienas mērķi aprēķināti:\n"
                             f"🔥 Kalorijas: {tdee:.0f} kcal\n"
                             f"🅿️ Proteīns: {protein:.0f} g\n"
                             f"🧈 Tauki: {fat:.0f} g\n"
                             f"🍞 Ogļhidrāti: {carbs:.0f} g\n\n"
                             f"Izmanto komandas no izvēlnes zemāk vai raksti manuāli.",
                             reply_markup=main_menu)
        await state.clear()
    except:
        await message.answer("❌ Izvēlies 1, 2 vai 3")

@dp.message(F.text == "/new")
async def new_handler(message: Message, state: FSMContext):
    await message.answer("📝 Ieraksti produkta nosaukumu:")
    await state.set_state(AddProduct.entering_name)

@dp.message(AddProduct.entering_name)
async def name_input_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.text.strip()
    products = user_products.get(user_id, {})
    if name in products:
        await state.update_data(name=name, macros=products[name])
        await state.set_state(AddProduct.entering_weight)
        await message.answer("⚖️ Ievadi svaru gramos:")
    else:
        await state.update_data(name=name)
        await message.answer("✍️ Ieraksti makro uz 100g (P F C), piemēram: 20 5 0")
        await state.set_state(AddProduct.entering_macros)

@dp.message(AddProduct.entering_macros)
async def macros_input_handler(message: Message, state: FSMContext):
    try:
        p, f, c = map(float, message.text.strip().split())
        await state.update_data(macros=(p, f, c))
        data = await state.get_data()
        user_id = message.from_user.id
        name = data["name"]
        if user_id not in user_products:
            user_products[user_id] = {}
        user_products[user_id][name] = (p, f, c)

        await message.answer("⚖️ Ievadi svaru gramos:")
        await state.set_state(AddProduct.entering_weight)
    except:
        await message.answer("🚫 Nepareizs formāts. Ieraksti trīs skaitļus (P F C), piemēram: 20 5 0")

@dp.message(AddProduct.entering_weight)
async def weight_input_handler(message: Message, state: FSMContext):
    try:
        weight_text = message.text.strip().replace(",", ".")
        weight = float(weight_text)

        data = await state.get_data()
        p100, f100, c100 = data["macros"]
        p = p100 * weight / 100
        f = f100 * weight / 100
        c = c100 * weight / 100
        kcal = p * 4 + f * 9 + c * 4

        user_id = message.from_user.id
        user_daily_totals[user_id]["p"] += p
        user_daily_totals[user_id]["f"] += f
        user_daily_totals[user_id]["c"] += c

        target = user_profiles[user_id]
        left_p = target["protein"] - user_daily_totals[user_id]["p"]
        left_f = target["fat"] - user_daily_totals[user_id]["f"]
        left_c = target["carbs"] - user_daily_totals[user_id]["c"]

        response = f"✅ {int(weight)}g <b>{data['name']}</b>:\n" \
                   f"🔥 {kcal:.1f} kcal\n" \
                   f"🅿️ {p:.2f}g P\n" \
                   f"🧈 {f:.2f}g F\n" \
                   f"🍞 {c:.2f}g C\n\n"

        def warn(nutrient, left):
            if left < 0:
                return f"⚠️ Tu esi pārsniedzis {nutrient} par {-left:.1f}g"
            else:
                return f"✅ Atlikušais {nutrient}: {left:.1f}g"

        response += warn("proteīns", left_p) + "\n"
        response += warn("tauki", left_f) + "\n"
        response += warn("ogļhidrāti", left_c)

        await message.answer(response, reply_markup=main_menu)
        await state.clear()
    except:
        await message.answer("🚫 Lūdzu ievadi pareizu svaru gramos, piemēram: 150 vai 150,5")


@dp.message(F.text == "/saved")
async def saved_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    products = user_products.get(user_id, {})
    if not products:
        await message.answer("📭 Saglabātu produktu vēl nav. Izmanto /new, lai pievienotu!")
        return
    product_list = "\n".join(f"- {name}" for name in products)
    await message.answer(f"📦 Saglabātie produkti:\n{product_list}\n\n✏️ Ieraksti produkta nosaukumu, kuru izvēlēties:")
    await state.set_state(AddProduct.entering_name)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
