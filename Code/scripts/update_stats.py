from yaudit.database import Session
from yaudit.models.topic import Topic
from yaudit.models.video_stat import VideoStat
from yaudit.models.api_search_result import APISearchResult
from yaudit.models.video import Video
from yaudit.models.channel import Channel

import os
import time
from youtube_api import YoutubeDataApi
from datetime import datetime

assert os.getenv('TOPIC_ID') is not None
assert os.getenv('YOUTUBE_API_KEY') is not None

session = Session()
topic = session.query(Topic).filter(Topic.id == os.getenv('TOPIC_ID')).first()
print('topic', topic.name)

youtube_data_api = YoutubeDataApi(os.getenv('YOUTUBE_API_KEY'))

i = 0
while True:
    i += 1
    print('Iteration', i)

    # get stats for seed videos
    seed_videos = topic.get_most_popular_videos()
    seed_videos = seed_videos['promoting'] + seed_videos['debunking']
    print('updating stats for', len(seed_videos), 'seed videos')
    for seed_video in seed_videos:
        video_metas = youtube_data_api.get_video_metadata(
            video_id=seed_video.get('youtube_id')
        )
        if not isinstance(video_metas, list):
            video_metas = [video_metas]

        for video_meta in video_metas:
            video_stat = VideoStat(video_id=seed_video.get('video_id'))
            video_stat.num_views = video_meta.get('video_view_count', 0)
            video_stat.num_comments = video_meta.get('video_comment_count', 0)
            video_stat.num_likes = video_meta.get('video_like_count', 0)
            video_stat.num_dislikes = video_meta.get('video_dislike_count', 0)
            session.add(video_stat)

    session.commit()
    print('video stats updated')

    # run search queries for topic
    search_queries = topic.search_queries
    print('searching', len(search_queries), 'search queries')
    for search_query in search_queries:
        results = youtube_data_api.search(
            q=search_query.query,
            max_results=25
        )
        searched_at = datetime.utcnow()

        print(search_query.query, '–', len(results), 'search results')
        for i, result in enumerate(results):
            youtube_id = result['video_id']
            video = session.query(Video).filter(Video.youtube_id == youtube_id).first()
            if video is None:
                video = Video(youtube_id=youtube_id)
                video.title = result['video_title']
                video.description = result['video_description']
                channel = session.query(Channel).filter(Channel.youtube_id == result['channel_id']).first()
                if channel is None:
                    channel = Channel(
                        youtube_id=result['channel_id'],
                        name=result['channel_title']
                    )
                    session.add(channel)
                video.channel = channel
                session.add(video)

            api_search_result = APISearchResult(
                position=i,
                search_query_id=search_query.id,
                searched_at=searched_at
            )
            api_search_result.video = video
            session.add(api_search_result)

    session.commit()

    # sleep 2 hours
    print('sleeping')
    time.sleep(2 * 60 * 60)
