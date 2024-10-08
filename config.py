import logging
from environs import Env
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Config:
    tg_token: str
    db_url: str
    openai_key: str


def load_config() -> Config:
    logger.info('Loading configuration...')
    env = Env()
    env.read_env()
    return Config(tg_token=env.str('TG_API_KEY'),
                  db_url=env.str('DATABASE_URL'),
                  openai_key=env.str('OPENAI_API_KEY'))


logger.info('Configuration loaded!')
