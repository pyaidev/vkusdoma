from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

product_cb = CallbackData('product', 'id', 'action','current_count','price')


def product_markup(idx, count, price):
    global product_cb

    markup = InlineKeyboardMarkup()

    back_btn = InlineKeyboardButton('⬅️', callback_data=product_cb.new(id=idx,
                                                                       action='decrease',current_count=count,price=price))

    count_btn = InlineKeyboardButton(count,
                                     callback_data=product_cb.new(id=idx,
                                                                  action='count',current_count=count,price=price))

    next_btn = InlineKeyboardButton('➡️', callback_data=product_cb.new(id=idx,
                                                                       action='increase',current_count=count,price=price))
    add_cart = InlineKeyboardButton(f'🛒 Добавить в корзину  - {round(int(count)*int(price),2)}€', callback_data=product_cb.new(id=idx,
                                                                       action='add',current_count=count,price=price))
    
    markup.row(back_btn, count_btn, next_btn)
    if int(count) >= 1:
        markup.row(
            add_cart
        )
    
    return markup




# def make_callback_data(item_id, current_count):
#     return korzina_cd.new(
#         item_id=item_id, current_count=current_count
#     )

# korzina_cd = CallbackData("add_korzina", "item_id", "current_count",)
# count_item = CallbackData("count", "item_id", "current_count",)
# add_item = CallbackData("plus", "item_id", "current_count",)
# subtraction_item = CallbackData("minus", "item_id", "current_count",)

# async def item_keyboard(item_id, current_count):
#     CURRENT_LEVEL = 3
#     markup = InlineKeyboardMarkup(row_width=3)
#     markup.row(
#         InlineKeyboardButton(
#             text=f"-", callback_data=subtraction_item.new(item_id=item_id, current_count=current_count), 
#         ),
#         InlineKeyboardButton(
#             text=f"{current_count}", callback_data=count_item.new(item_id=item_id, current_count=current_count)
#         ),
#         InlineKeyboardButton(
#             text=f"+", callback_data=add_item.new(item_id=item_id, current_count=current_count)
#         )
#     )
#     markup.row(
#         InlineKeyboardButton(
#             text="🛒 Добавить в корзину",
#             callback_data=make_callback_data(
#                 item_id=item_id, current_count=current_count
#             ),
#         )
#     )
#     return markup