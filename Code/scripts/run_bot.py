from yaudit.models.search_query import SearchQuery
from yaudit.bot.bot import Bot
from yaudit.database import Session
from yaudit.models.topic import Topic
from yaudit.models.search_query import SearchQuery
import os

assert os.getenv('YOUTUBE_USERNAME') is not None
assert os.getenv('YOUTUBE_PASSWORD') is not None
assert os.getenv('TOPIC') is not None

session = Session()
topic = session.query(Topic).filter(Topic.name == os.getenv('TOPIC')).first()
assert topic is not None
search_queries = session.query(SearchQuery).filter(SearchQuery.topic == topic).all()
assert len(search_queries) > 0

configuration = {
    'queries': [q.query for q in search_queries]
}
print('Running with configuration:')
print(configuration)
with Bot(configuration) as bot:
    bot.run()
    bot.query_videos()
