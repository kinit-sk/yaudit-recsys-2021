from yaudit.database import Session
from yaudit.models.topic import Topic
from yaudit.models.search_query import SearchQuery
from yaudit.models.channel import Channel
from yaudit.models.video import Video
from yaudit.models.seed_video import SeedVideo
import pandas as pd

session = Session()

print('Deleting old data')
session.query(SeedVideo).delete()
session.query(Video).delete()
session.query(Channel).delete()
session.query(SearchQuery).delete()
session.query(Topic).delete()

videos_df = pd.read_csv('seed_data/videos.csv')

## Channels
channels_df = videos_df[['channel_title', 'channel_id']].drop_duplicates()
channels = [
    Channel(youtube_id=channel['channel_id'], name=channel['channel_title'])
    for _, channel in channels_df.iterrows()
]
channels_by_youtube_id = {c.youtube_id: c for c in channels}
print(f'Saving {len(channels)} channels')
for channel in channels:
    session.add(channel)

## Videos
print(f'Saving {len(videos_df)} videos')
videos_by_youtube_id = {}
for _, video_info in videos_df.iterrows():
    video = Video(youtube_id=video_info['youtube_id'])
    video.title = video_info['title']
    video.description = video_info['description']
    video.duration_seconds = int(video_info['duration_seconds'])
    video.channel = channels_by_youtube_id[video_info['channel_id']]
    video.num_likes = video_info['num_likes']
    video.num_dislikes = video_info['num_dislikes']
    video.num_views = video_info['num_views']
    video.num_comments = video_info['num_comments']
    videos_by_youtube_id[video.youtube_id] = video
    session.add(video)

## Topics
topics_df = pd.read_csv('seed_data/topics.csv')
print(f'Saving {len(topics_df)} topics')
topics_by_name = {}
for _, topic_info in topics_df.iterrows():
    topic = Topic(name=topic_info['topic'])
    topic.full_name = topic_info['full_name']
    topics_by_name[topic.name] = topic
    session.add(topic)

## Seed videos
seed_videos_df = pd.read_csv('seed_data/seed_videos.csv')
seed_video_stances = {0: 'neutral', -1: 'debunking', 1: 'promoting'}
print(f'Saving {len(seed_videos_df)} seed videos')
for _, seed_video_info in seed_videos_df.iterrows():
    seed_video = SeedVideo()
    seed_video.stance = seed_video_stances[seed_video_info['stance']]
    seed_video.topic = topics_by_name[seed_video_info['topic']]
    seed_video.video = videos_by_youtube_id[seed_video_info['youtube_id']]
    session.add(seed_video)

## Search queries
search_queries_df = pd.read_csv('seed_data/search_queries.csv')
print(f'Saving {len(search_queries_df)} search queries')
for _, search_query_info in search_queries_df.iterrows():
    search_query = SearchQuery(
        topic=topics_by_name[search_query_info['topic']],
        query=search_query_info['query']
    )
    session.add(search_query)

session.commit()

print('Done')
