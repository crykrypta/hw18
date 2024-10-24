import logging
from environs import Env
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Gigachat:
    auth: str


@dataclass
class RedisConfig:
    host: str
    port: int


@dataclass
class Config:
    tg_token: str
    db_url: str
    openai_key: str
    proxy: str
    fastapi_url: str
    redis: RedisConfig
    gigachat: Gigachat


def load_config() -> Config:
    logger.info('Loading configuration...')
    env = Env()
    env.read_env()
    return Config(tg_token=env.str('TG_API_KEY'),
                  db_url=env.str('DATABASE_URL'),
                  openai_key=env.str('OPENAI_API_KEY'),
                  proxy=env.str('PROXY'),
                  fastapi_url=env.str('FASTAPI_URL'),
                  redis=RedisConfig(host=env.str('REDIS_HOST'),
                                    port=env.int('REDIS_PORT')),
                  gigachat=Gigachat(auth=env.str('GIGACHAT_AUTH')))


logger.info('Configuration loaded!')
