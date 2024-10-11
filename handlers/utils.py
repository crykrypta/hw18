def message_and_requests(message: str,
                         request_count: int,
                         limit: int = 5) -> str:
    """Формирует сообщение для пользователя
    Args:
        message (str): Ответ модели
        request_count (int): Количество запросов
        limit (int): Лимит запросов
    Returns:
        Осталось запросов: {request_count}\n\n{message}
    """
    return f'Осталось запросов: {limit-request_count}\n\n{message}'


def fabric_context_message(user: str, model: str) -> str:
    """Формирует контекст диалога
    Args:
        user (str): Сообщение пользователя
        model (str): Ответ модели
    Returns:
        user: {user}\nmodel: {model}
    """
    return f'user: {user}\nmodel: {model}'


async def answer_and_remove_keyboard(bot, message, state, text):
    """Отправляет сообщение и удаляет клавиатуру предыдущего сообщения бота

    Args:
        bot (Bot): Экземпляр бота (dp.bot)
        message (): Текущее сообщение пользователя
        state (_type_): Состояние FSMContext
        text (_type_): Текст сообщение, которое будет отправлено ботом
    """
    # Получаем данные из состояния
    data = await state.get_data()
    previous_message_id = data.get('last_bot_message_id')

    # Обновляем клавиатуру в предыдущем сообщении
    if previous_message_id:
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=previous_message_id,
            reply_markup=None
        )

    # Отправляем сообщение без клавиатуры
    generating_msg = await message.answer(
        text=text,
        reply_markup=None
    )

    # Сохраняем идентификатор текущего сообщения в состоянии
    await state.update_data(last_bot_message_id=generating_msg.message_id)