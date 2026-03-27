from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str('BOT_TOKEN')
LOCATIONIQ_API_KEY = env.str('LOCATIONIQ_API_KEY')
LOCATIONIQ_BASE_URL = env.str('LOCATIONIQ_BASE_URL')
OPENWEATHER_API_KEY = env.str('OPENWEATHER_API_KEY')
OPENWEATHER_URL = env.str('OPENWEATHER_URL')

DB_URL = env.str('DB_URL')
ADMINS = env.list('ADMINS')
# PRIVATE_CHANNEL = env.str('PRIVATE_CHANNEL')
PRIVATE_CHANNEL = [int(i) for i in env.str("PRIVATE_CHANNEL").split(",")]
# CHANNEL_USERNAME = env.str('CHANNEL_USERNAME')
CHANNEL_USERNAME = env.str("CHANNEL_USERNAME").split(",")