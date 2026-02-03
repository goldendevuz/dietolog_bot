import os
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

load_dotenv()

# -----------------------
# i18n (simple dict-based)
# -----------------------
I18N: Dict[str, Dict[str, str]] = {
    "uz": {
        "choose_lang": "Tilni tanlang:",
        "start": "Salom! Men BMI, kaloriya va oqsilni hisoblab beraman.\nBoshlash uchun /calc ni bosing.",
        "calc_intro": "Boshlaymiz. Iltimos, bo'yingizni sm da kiriting (masalan: 175).",
        "ask_weight": "Endi vazningizni kg da kiriting (masalan: 72.5).",
        "ask_age": "Yoshingizni kiriting (masalan: 27).",
        "ask_sex": "Jinsni tanlang:",
        "sex_m": "Erkak",
        "sex_f": "Ayol",
        "ask_activity": "Faollik darajangizni tanlang:",
        "act_sedentary": "1) Kamharakat (ofis) — 1.2",
        "act_light": "2) Yengil (1-3 mashq/hafta) — 1.375",
        "act_moderate": "3) O'rtacha (3-5 mashq/hafta) — 1.55",
        "act_very": "4) Faol (6-7 mashq/hafta) — 1.725",
        "act_extra": "5) Juda faol (og'ir mehnat + sport) — 1.9",
        "bad_number": "❌ Noto'g'ri qiymat. Iltimos, raqam kiriting.",
        "range_height": "❌ Bo'y 120–230 sm oralig'ida bo'lsin.",
        "range_weight": "❌ Vazn 30–250 kg oralig'ida bo'lsin.",
        "range_age": "❌ Yosh 10–90 oralig'ida bo'lsin.",
        "result_title": "✅ Hisob-kitob natijalari",
        "bmi": "• BMI: {bmi:.1f} ({bmi_cat})",
        "tdee": "• Kunlik kaloriya (TDEE): ~{tdee:.0f} kcal",
        "bmr": "• BMR: ~{bmr:.0f} kcal",
        "protein": "• Oqsil: {p1:.0f}–{p2:.0f} g/kun (odatiy) | {p3:.0f}–{p4:.0f} g/kun (vazn tashlash/fitness)",
        "disclaimer": "Eslatma: Bu umumiy hisob-kitob. Tibbiy tavsiya emas.",
        "again": "Yana hisoblash uchun /calc ni bosing.",
        "btn_calc": "Hisoblash",
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "start": "Привет! Я считаю BMI, калории и белок.\nДля старта нажмите /calc.",
        "calc_intro": "Начнем. Введите рост в см (например: 175).",
        "ask_weight": "Введите вес в кг (например: 72.5).",
        "ask_age": "Введите возраст (например: 27).",
        "ask_sex": "Выберите пол:",
        "sex_m": "Мужчина",
        "sex_f": "Женщина",
        "ask_activity": "Выберите уровень активности:",
        "act_sedentary": "1) Малоподвижный — 1.2",
        "act_light": "2) Легкий (1-3 трен./нед) — 1.375",
        "act_moderate": "3) Средний (3-5 трен./нед) — 1.55",
        "act_very": "4) Высокий (6-7 трен./нед) — 1.725",
        "act_extra": "5) Очень высокий — 1.9",
        "bad_number": "❌ Неверное значение. Введите число.",
        "range_height": "❌ Рост должен быть 120–230 см.",
        "range_weight": "❌ Вес должен быть 30–250 кг.",
        "range_age": "❌ Возраст должен быть 10–90.",
        "result_title": "✅ Результаты",
        "bmi": "• BMI: {bmi:.1f} ({bmi_cat})",
        "tdee": "• Суточные калории (TDEE): ~{tdee:.0f} kcal",
        "bmr": "• BMR: ~{bmr:.0f} kcal",
        "protein": "• Белок: {p1:.0f}–{p2:.0f} г/день (обычно) | {p3:.0f}–{p4:.0f} г/день (снижение веса/фитнес)",
        "disclaimer": "Примечание: Это общий расчет, не медицинская рекомендация.",
        "again": "Чтобы посчитать снова, нажмите /calc.",
        "btn_calc": "Рассчитать",
    },
    "en": {
        "choose_lang": "Choose language:",
        "start": "Hi! I calculate BMI, calories, and protein.\nPress /calc to start.",
        "calc_intro": "Let's start. Enter your height in cm (e.g., 175).",
        "ask_weight": "Enter your weight in kg (e.g., 72.5).",
        "ask_age": "Enter your age (e.g., 27).",
        "ask_sex": "Select sex:",
        "sex_m": "Male",
        "sex_f": "Female",
        "ask_activity": "Select activity level:",
        "act_sedentary": "1) Sedentary — 1.2",
        "act_light": "2) Light (1-3 workouts/wk) — 1.375",
        "act_moderate": "3) Moderate (3-5 workouts/wk) — 1.55",
        "act_very": "4) Very active (6-7 workouts/wk) — 1.725",
        "act_extra": "5) Extra active — 1.9",
        "bad_number": "❌ Invalid value. Please enter a number.",
        "range_height": "❌ Height must be 120–230 cm.",
        "range_weight": "❌ Weight must be 30–250 kg.",
        "range_age": "❌ Age must be 10–90.",
        "result_title": "✅ Results",
        "bmi": "• BMI: {bmi:.1f} ({bmi_cat})",
        "tdee": "• Daily calories (TDEE): ~{tdee:.0f} kcal",
        "bmr": "• BMR: ~{bmr:.0f} kcal",
        "protein": "• Protein: {p1:.0f}–{p2:.0f} g/day (general) | {p3:.0f}–{p4:.0f} g/day (fat loss/fitness)",
        "disclaimer": "Note: This is a general estimate, not medical advice.",
        "again": "To calculate again, press /calc.",
        "btn_calc": "Calculate",
    },
}

# Simple per-user language memory (MVP). Replace with DB later.
USER_LANG: Dict[int, str] = {}

def t(user_id: int, key: str) -> str:
    lang = USER_LANG.get(user_id, "uz")
    return I18N.get(lang, I18N["uz"]).get(key, I18N["uz"][key])

# -----------------------
# Calculation logic
# -----------------------
@dataclass
class CalcInput:
    height_cm: float
    weight_kg: float
    age: int
    sex: str  # "m" or "f"
    activity: float

def bmi_value(weight_kg: float, height_cm: float) -> float:
    h_m = height_cm / 100.0
    return weight_kg / (h_m * h_m)

def bmi_category(bmi: float, lang: str) -> str:
    # Categories are generic; keep simple and non-clinical
    if bmi < 18.5:
        return {"uz": "Kam vazn", "ru": "Недостаточный вес", "en": "Underweight"}.get(lang, "Underweight")
    if bmi < 25:
        return {"uz": "Me'yor", "ru": "Норма", "en": "Normal"}.get(lang, "Normal")
    if bmi < 30:
        return {"uz": "Ortiqcha vazn", "ru": "Избыточный вес", "en": "Overweight"}.get(lang, "Overweight")
    return {"uz": "Semizlik", "ru": "Ожирение", "en": "Obesity"}.get(lang, "Obesity")

def bmr_mifflin(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    # Mifflin-St Jeor
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "m" else base - 161

def tdee(bmr: float, activity: float) -> float:
    return bmr * activity

def protein_ranges(weight_kg: float) -> Tuple[float, float, float, float]:
    # general: 1.2–1.6 g/kg
    # fat loss/fitness: 1.6–2.2 g/kg
    return (
        1.2 * weight_kg,
        1.6 * weight_kg,
        1.6 * weight_kg,
        2.2 * weight_kg,
    )

# -----------------------
# FSM States
# -----------------------
class CalcStates(StatesGroup):
    height = State()
    weight = State()
    age = State()
    sex = State()
    activity = State()

# -----------------------
# Keyboards
# -----------------------
def kb_language():
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇿 UZ", callback_data="lang:uz")
    kb.button(text="🇷🇺 RU", callback_data="lang:ru")
    kb.button(text="🇬🇧 EN", callback_data="lang:en")
    kb.adjust(3)
    return kb.as_markup()

def kb_sex(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(user_id, "sex_m"), callback_data="sex:m")
    kb.button(text=t(user_id, "sex_f"), callback_data="sex:f")
    kb.adjust(2)
    return kb.as_markup()

def kb_activity(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(user_id, "act_sedentary"), callback_data="act:1.2")
    kb.button(text=t(user_id, "act_light"), callback_data="act:1.375")
    kb.button(text=t(user_id, "act_moderate"), callback_data="act:1.55")
    kb.button(text=t(user_id, "act_very"), callback_data="act:1.725")
    kb.button(text=t(user_id, "act_extra"), callback_data="act:1.9")
    kb.adjust(1)
    return kb.as_markup()

# -----------------------
# Router / Handlers
# -----------------------
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    if user_id not in USER_LANG:
        USER_LANG[user_id] = "uz"
    await message.answer(t(user_id, "choose_lang"), reply_markup=kb_language())

@router.callback_query(F.data.startswith("lang:"))
async def on_lang(call: CallbackQuery):
    user_id = call.from_user.id
    lang = call.data.split(":", 1)[1]
    USER_LANG[user_id] = lang if lang in ("uz", "ru", "en") else "uz"
    await call.answer()
    await call.message.answer(t(user_id, "start"))
    # optional quick start:
    await call.message.answer(f"👉 /calc")

@router.message(Command("calc"))
async def cmd_calc(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.clear()
    await state.set_state(CalcStates.height)
    await message.answer(t(user_id, "calc_intro"))

def parse_float(text: str) -> Optional[float]:
    try:
        # allow comma decimal
        return float(text.replace(",", ".").strip())
    except Exception:
        return None

@router.message(CalcStates.height)
async def step_height(message: Message, state: FSMContext):
    user_id = message.from_user.id
    val = parse_float(message.text or "")
    if val is None:
        return await message.answer(t(user_id, "bad_number"))
    if not (120 <= val <= 230):
        return await message.answer(t(user_id, "range_height"))
    await state.update_data(height_cm=val)
    await state.set_state(CalcStates.weight)
    await message.answer(t(user_id, "ask_weight"))

@router.message(CalcStates.weight)
async def step_weight(message: Message, state: FSMContext):
    user_id = message.from_user.id
    val = parse_float(message.text or "")
    if val is None:
        return await message.answer(t(user_id, "bad_number"))
    if not (30 <= val <= 250):
        return await message.answer(t(user_id, "range_weight"))
    await state.update_data(weight_kg=val)
    await state.set_state(CalcStates.age)
    await message.answer(t(user_id, "ask_age"))

@router.message(CalcStates.age)
async def step_age(message: Message, state: FSMContext):
    user_id = message.from_user.id
    val = parse_float(message.text or "")
    if val is None:
        return await message.answer(t(user_id, "bad_number"))
    age = int(val)
    if not (10 <= age <= 90):
        return await message.answer(t(user_id, "range_age"))
    await state.update_data(age=age)
    await state.set_state(CalcStates.sex)
    await message.answer(t(user_id, "ask_sex"), reply_markup=kb_sex(user_id))

@router.callback_query(CalcStates.sex, F.data.startswith("sex:"))
async def step_sex(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    sex = call.data.split(":", 1)[1]
    if sex not in ("m", "f"):
        await call.answer()
        return
    await state.update_data(sex=sex)
    await state.set_state(CalcStates.activity)
    await call.answer()
    await call.message.answer(t(user_id, "ask_activity"), reply_markup=kb_activity(user_id))

@router.callback_query(CalcStates.activity, F.data.startswith("act:"))
async def step_activity(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    act_raw = call.data.split(":", 1)[1]
    act = parse_float(act_raw)
    if act is None:
        await call.answer()
        return

    data = await state.get_data()
    ci = CalcInput(
        height_cm=float(data["height_cm"]),
        weight_kg=float(data["weight_kg"]),
        age=int(data["age"]),
        sex=str(data["sex"]),
        activity=float(act),
    )

    bmi = bmi_value(ci.weight_kg, ci.height_cm)
    bmr = bmr_mifflin(ci.weight_kg, ci.height_cm, ci.age, ci.sex)
    tdee_val = tdee(bmr, ci.activity)
    p1, p2, p3, p4 = protein_ranges(ci.weight_kg)
    lang = USER_LANG.get(user_id, "uz")

    text = []
    text.append(t(user_id, "result_title"))
    text.append(t(user_id, "bmi").format(bmi=bmi, bmi_cat=bmi_category(bmi, lang)))
    text.append(t(user_id, "bmr").format(bmr=bmr))
    text.append(t(user_id, "tdee").format(tdee=tdee_val))
    text.append(t(user_id, "protein").format(p1=p1, p2=p2, p3=p3, p4=p4))
    text.append("")
    text.append(t(user_id, "disclaimer"))
    text.append(t(user_id, "again"))

    await call.answer()
    await call.message.answer("\n".join(text))
    await state.clear()

# -----------------------
# Entrypoint
# -----------------------
async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set. Put it into .env")

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
