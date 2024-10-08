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
