from yaudit.bot.bot import *
import os

account_id = os.getenv('YAUDIT_ACCOUNT_ID')
topic_id = os.getenv('YAUDIT_TOPIC_ID')
configuration_id = os.getenv('YAUDIT_CONFIGURATION_ID')
with Bot(account_id=account_id, topic_id=topic_id, configuration_id=configuration_id) as bot:
    try:
        bot.run()
    except Exception as e:
        bot.logger.exception('Unknown error occurred!')
        bot.save_page_source('unknown')
        raise
