import logging
from typing import List

logger = logging.getLogger(__name__)


def fabric_user_prompt(username: str, dialog_context: List[str], topic: str) -> str:  # noqa
    """"Фабрикует user-промпт
    Args:
    - username(str) - имя пользователя
    - dialog_context(str) - контекст диалога
    - topic(str) - вопрос пользователя
    Returns:
    - {, user: content}
    """
    try:
        user_message = 'Имя пользователя: {0}\n Контекст диалога: {1}\nОтветь на вопрос: {2}'.format( # noqa
            username, ';'.join(dialog_context), topic
        )
        logger.info('Message has been formed (SUCCESS) ')
        return user_message
    except Exception as e:
        logger.error(f'Ошибка при формировании сообщения пользователя: {e}') # noqa
        return 'None'
