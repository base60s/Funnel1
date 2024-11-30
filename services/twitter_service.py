import os
from twitter.api import Twitter, OAuth
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)

class TwitterService:
    def __init__(self):
        self.auth_params = {
            'token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'token_secret': os.getenv('TWITTER_ACCESS_SECRET'),
            'consumer_key': os.getenv('TWITTER_API_KEY'),
            'consumer_secret': os.getenv('TWITTER_API_SECRET')
        }
        self.api = Twitter(auth=OAuth(**self.auth_params))

    async def post_tweet(self, content: str):
        try:
            if len(content) > 280:
                raise ValueError("Tweet exceeds 280 characters")

            response = await self._make_twitter_request('statuses/update.json', {'status': content})
            
            return {
                'id': response['id_str'],
                'text': response['text']
            }
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            raise

    async def _make_twitter_request(self, endpoint: str, params: dict):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f'https://api.twitter.com/1.1/{endpoint}',
                    params=params,
                    auth=OAuth1Session(**self.auth_params)
                ) as response:
                    if response.status != 200:
                        error_data = await response.text()
                        raise Exception(f"Twitter API error: {error_data}")
                    return await response.json()
        except Exception as e:
            logger.error(f"Twitter API request failed: {str(e)}")
            raise