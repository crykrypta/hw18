from environs import Env
from dataclasses import dataclass


@dataclass
class Config:
    tg_token: str
    db_url: str


def load_config() -> Config:
    env = Env()
    env.read_env()
    return Config(tg_token=env.str('TG_API_KEY'),
                  db_url=env.str('DATABASE_URL'))
