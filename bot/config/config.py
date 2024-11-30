from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):

    API_ID: int = 4099059
    API_HASH: str = '68b3bbfef5cd0bea0cda557708971a41'

    USE_REF: bool = True
    REF_ID: str = 'f7505768028'

    USE_RANDOM_DELAY_IN_RUN: bool = True
    RANDOM_DELAY_IN_RUN: list[int] = [3, 120]

    SLEEP_TIME_IN_MINUTES: list[int] = [10, 17]

    ENABLE_AUTO_TASKS: bool = False
    ENABLE_AUTO_DRAW: bool = True
    ENABLE_JOIN_TG_CHANNELS: bool = False
    ENABLE_CLAIM_REWARD: bool = True
    ENABLE_AUTO_UPGRADE: bool = False

    ENABLE_SSL: bool = False

    BOOSTS_BLACK_LIST: list[str] = ['INVITE_FRIENDS', 'TON_TRANSACTION', 'BOOST_CHANNEL', 'ACTIVITY_CHALLENGE', 'CONNECT_WALLET']
    TASKS_TODO_LIST: list[str] = ["x:notcoin", "x:notpixel", "paint20pixels", "leagueBonusSilver", "invite3frens", "leagueBonusGold", "channel:notpixel_channel", "channel:notcoin", "premium"]

    USE_PROXY_FROM_FILE: bool = True

settings = Settings()