# Лексикон на русском языке
lexicon = {
    'ru': {
        'commands': {
            'start': 'Добро пожаловать, мой дорогой друг!',
            'help': 'Это тестовый бот для доступа к <b>ChatGPT</b>\n'
                    '- Хранит информацию о пользователях в <b>PostgreSQL</b>\n'
                    '- Считает количество запросов пользователя за сутки\n'
                    '- Каждые новые сутки счетчик сбрасывается\n',
        },
        'text': {
            'any_text': 'Текстовое сообщение получено!',
            'welcome': 'Добро пожаловать!',
            'main_menu': 'Главное меню',
        },
        'buttons': {
            'help': 'Помощь',
            'ch_lang': 'Сменить язык',
            'reset_requests': 'Сбросить запросы',
            'start_chat': 'Начать чат',
            'stop_chat': 'Выход',
            'to_main': 'Главное меню'
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
            'ch_lang': 'Смена языка',
        }
    },
    # Лексикон на английском языке
    'eng': {
        'commands': {
            'start': 'Welcome, my dear friend!',
            'help': 'This is a test bot for accessing <b>ChatGPT</b>\n'
                    '- Stores information about the user in <b>PostgreSQL</b>\n' # noqa
                    '- Counts the number of user requests per day\n'
                    '- Every new day the counter is reset\n',
        },
        'text': {
            'any_text': 'We’ve received a message from you!',
            'welcome': 'Hello! Here is the list of available commands:',
            'main_menu': 'Main menu',
        },
        'buttons': {
            'help': 'Help',
            'ch_lang': 'Change language',
            'reset_requests': 'Reset requests',
            'start_chat': 'Start Chat',
            'stop_chat': 'Exit',
            'to_main': 'Main menu'
        },
        'types': {
            'voice': 'We’ve received a voice message from you!',
            'photo': 'Photo saved!'
        },
        'error': {
            'user_not_found': 'User not found, enter the command /start',
            'limit': 'Request limit exceeded, but you can buy more',
            'requests_limit': 'Request limit exceeded, but you can buy more',
        },
        'actions': {
            'reset_requests': 'Requests reseted',
            'chat_start': 'Chat started, just start typing!', # noqa
            'chat_stop': 'Chat stopped',
            'ch_lang': 'Choosing language',
        }
    },
    'none': {
        'choose_lang': 'Выберите язык / Choose language',
    }
}
