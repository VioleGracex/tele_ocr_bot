""" keyboards.py """
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Define the start keyboard with ReplyKeyboardMarkup
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/StartAnalysis')],
        [KeyboardButton(text='/FAQ')],
        [KeyboardButton(text='/Modes')]
    ],
    resize_keyboard=True
)

# Define the cancel keyboard with ReplyKeyboardMarkup
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/CancelRequest')]
    ],
    resize_keyboard=True
)

# Define the start over keyboard with InlineKeyboardMarkup
start_over_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать заново", callback_data="start")]
])

# Define the modes keyboard with InlineKeyboardMarkup
modes_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Только OCR", callback_data="set_mode_ocr_only")],
    [InlineKeyboardButton(text="OCR и анализ GPT", callback_data="set_mode_ocr_and_gpt")]
])