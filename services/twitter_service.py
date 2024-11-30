import os
import tweepy
import logging

logger = logging.getLogger(__name__)

class TwitterService:
    def __init__(self):
        # Initialize tweepy client
        self.client = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET')
        )

    async def post_tweet(self, content: str):
        """Post a tweet using tweepy"""
        try:
            # Validate tweet content
            if len(content) > 280:
                raise ValueError("Tweet exceeds 280 characters")

            # Post tweet
            response = self.client.create_tweet(text=content)
            
            return {
                'id': response.data['id'],
                'text': content
            }
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            raise