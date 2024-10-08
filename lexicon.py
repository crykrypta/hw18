# Лексикон на русском языке
lexicon = {
    'ru': {
        'commands': {
            'start': 'Добро пожаловать, мой дорогой друг!',
            'help': 'Этот бот предназначен для обучения\n'
            'Принимает три вида сообщений:\n'
            '1. Текстовые сообщения\n'
            '2. Фото\n'
            '3. Голосовые сообщения',
        },
        'text': {
            'any_text': 'Текстовое сообщение получено!',
            'welcome': 'Добро пожаловать!',
        },
        'buttons': {
            'help': 'Помощь',
            'ch_lang': 'Сменить язык',
            'reset_requests': 'Сбросить запросы',
            'start_chat': 'Начать чат',
            'stop_chat': 'Выход',
        },
        'types': {
            'voice': 'Голосовое сообщение получено!',
            'photo': 'Фотография сохранена',
        },
        'error': {
            'user_not_found': 'Пользователь не найден, введите команду /start',
            'requests_limit': 'Превышен лимит запросов, купите еще',
        },
        'actions': {
            'reset_requests': 'Запросы сброшены',
            'chat_start': 'Чат запущен!',
            'chat_stop': 'Чат остановлен',
        }
    },
    # Лексикон на английском языке
    'eng': {
        'command': {
            'start': 'Welcome, my dear friend!',
            'help': 'This bot is designed for training\n'
            'Accepts three types of messages:\n'
            '1. Text messages\n'
            '2. Photos\n'
            '3. Voice messages',
        },
        'text': {
            'any_text': 'We’ve received a message from you!',
            'welcome': 'Hello! Here is the list of available commands:',
        },
        'buttons': {
            'help': 'Help',
            'ch_lang': 'Change language',
            'reset_requests': 'Reset requests',
            'start_chat': 'Start Chat',
            'stop_chat': 'Exit',
        },
        'types': {
            'voice': 'We’ve received a voice message from you!',
            'photo': 'Photo saved!'
        },
        'error': {
            'user_not_found': 'User not found, enter the command /start',
            'limit': 'Request limit exceeded, but you can buy more',
        },
        'actions': {
            'reset_requests': 'Requests reseted',
            'chat_start': 'Chat started, just start typing!', # noqa
            'chat_stop': 'Chat stopped',
        }
    }
}
