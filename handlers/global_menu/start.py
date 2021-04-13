import logging

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram import types
from aiogram.types import CallbackQuery
from aiogram.utils.emoji import emojize

from loader import dp, bot, _

from keyboards.reply.reply_kb import markup_general_menu, start_orange_invitation_kb
from keyboards.inline.inline_kb import inline_kb1, languages_markup
from states.menu_states import Menu, Invite
from models.db_service import DBService
from utils.functions import ref_info, get_status_emoji, get_all_info_text_user

logging.basicConfig(level=logging.INFO)

dbs = DBService()


async def create_user_start(lang):
    await dbs.users.create_user(language=lang)
    await dbs.statuses.create_pair()
    await dbs.rings_help.create_rings_help()
    # await dbs.requisites.create_requisite(name="спросить лично", value="")


async def start_red_invitation(message, user_to, state: FSMContext):
    intentions_list = await dbs.intentions.get_intentions(statuses=[11, 12], from_id=message.chat.id, to_id=user_to.tg_id)

    if intentions_list:
        bot_text = _('Вы уже помогаете участнику {}:'.format(user_to.name))
        for intention_one in intentions_list:
            if intention_one.status == 1:
                bot_text += "\n" + emojize(f"{intention_one.payment}:heart:")
            elif intention_one.status == 11:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:")
            elif intention_one.status == 12:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:→👍")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    markup = await start_orange_invitation_kb(user_to)

    bot_username = (await bot.me).username
    bot_text = await get_all_info_text_user(bot_username, user_to.tg_id)
    bot_text += '\nВы можете помочь этому участнику?'

    await Invite.start_red_invitation_check.set()
    await state.update_data(user_to_id=user_to.tg_id)

    await bot.send_message(message.chat.id, bot_text, reply_markup=markup, disable_web_page_preview=True)


async def start_orange_invitation(message, user_to, state: FSMContext):
    intentions_list = await dbs.intentions.get_intentions(statuses=[1, 11, 12], from_id=message.chat.id, to_id=user_to.tg_id)

    if intentions_list:
        bot_text = _('Вы уже помогаете участнику {}:'.format(user_to.name))
        for intention_one in intentions_list:
            if intention_one.status == 1:
                bot_text += "\n" + emojize(f"{intention_one.payment}:heart:")
            elif intention_one.status == 11:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:")
            elif intention_one.status == 12:
                bot_text += "\n" + emojize(f"{intention_one.payment}:handshake:→👍")
        await Menu.global_menu.set()
        markup = await markup_general_menu()
        await bot.send_message(message.chat.id, bot_text, reply_markup=markup)
        return

    markup = await start_orange_invitation_kb(user_to)

    bot_username = (await bot.me).username
    bot_text = await get_all_info_text_user(bot_username, user_to.tg_id)
    bot_text += '\nВы можете помочь этому участнику?'

    await Invite.start_orange_invitation_check.set()
    await state.update_data(user_to_id=user_to.tg_id)

    await bot.send_message(message.chat.id, bot_text, reply_markup=markup, disable_web_page_preview=True)


@dp.message_handler(CommandStart(), state='*')
async def cmd_start(message: types.Message, state: FSMContext):

    # Set state
    await Menu.global_menu.set()
    chat_id = message.from_user.id
    old_user = await dbs.users.get_user(chat_id)

    referral = message.get_args()
    if referral:
        referral = await ref_info(referral)
        user_from = await dbs.users.get_user(referral[0])
        user_to = await dbs.users.get_user(referral[1])
        user_to_status = await get_status_emoji(user_to.status)
        if old_user:
            if user_to.status == 'green':
                markup = await markup_general_menu()
                await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)
                return

            if referral[0] == referral[1]:
                bot_text = _('{} приглашает вас помогать себе').format(user_from.name)
            else:
                bot_text = _('{} приглашает вас помогать своим друзьям').format(user_from.name)

            await bot.send_message(message.chat.id, bot_text)

            if user_to.status == 'orange':
                await start_orange_invitation(message, user_to, state=state)
            elif 'red' in user_to.status:
                await start_red_invitation(message, user_to, state=state)

        else:
            await create_user_start("ru")

            if user_to.status == 'green':
                markup = await markup_general_menu()
                await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)

            if referral[0] == referral[1]:
                bot_text = _('{} приглашает вас помогать себе').format(user_from.name)
            else:
                bot_text = _('{} приглашает вас помогать своим друзьям').format(user_from.name)

            await bot.send_message(message.chat.id, bot_text)

            if user_to.status == 'orange':
                await start_orange_invitation(message, user_to, state=state)
            elif 'red' in user_to.status:
                await start_red_invitation(message, user_to, state=state)

    else:
        if old_user:
            markup = await markup_general_menu()
            await bot.send_message(message.chat.id, _('Меню'), reply_markup=markup)
        else:
            await bot.send_message(chat_id, "Приветствуем вас в Exodus Bot!\nВыберите язык.\n\nWelcome to Exodus "
                                            "Bot!\nSelect a language.", reply_markup=languages_markup)


@dp.callback_query_handler(text_contains="lang", state=Menu.global_menu)
async def change_language(call: CallbackQuery):
    await call.message.edit_reply_markup()
    # Достаем последние 2 символа (например ru)
    lang = call.data[-2:]

    # добавляем пользователя
    await create_user_start(lang)

    # После того, как мы поменяли язык, в этой функции все еще указан старый, поэтому передаем locale=lang
    await call.message.answer(_("Вы выбрали русский язык", locale=lang))

    markup = await markup_general_menu(lang=lang)
    await call.message.answer(_('Меню', locale=lang), reply_markup=markup)


@dp.message_handler(commands=['1'])
async def process_command_1(message: types.Message):
    await message.reply("Первая инлайн кнопка", reply_markup=inline_kb1)


@dp.callback_query_handler(lambda c: c.data == 'button1')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Нажата первая кнопка!')


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())