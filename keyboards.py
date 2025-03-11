from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Define the keyboards
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/StartAnalysis')],
        [KeyboardButton(text='/FAQ')]
    ],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='/CancelRequest')]
    ],
    resize_keyboard=True
)