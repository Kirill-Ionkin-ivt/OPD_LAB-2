from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Текуший курс $')],
                                     [KeyboardButton(text='Ввод границ'),
                                      KeyboardButton(text='Текущие границы')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')
