from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Define the start keyboard with ReplyKeyboardMarkup
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/StartAnalysis')],
        [KeyboardButton(text='/FAQ')]
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