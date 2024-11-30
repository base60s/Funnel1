import os
import requests
from requests_oauthlib import OAuth2Session
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TwitterService:
    def __init__(self):
        self.api_base = 'https://api.twitter.com/2'
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_key_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_SECRET')
        
        # Set up session with OAuth 2.0
        self.session = self._create_oauth_session()

    def _create_oauth_session(self) -> requests.Session:
        """Create an OAuth2 session for X API v2"""
        session = requests.Session()
        session.headers.update({
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json',
        })
        return session

    async def post_tweet(self, content: str) -> Dict[str, Any]:
        """Post a tweet using X API v2"""
        try:
            # Validate tweet content
            if len(content) > 280:
                raise ValueError("Tweet exceeds 280 characters")

            # Prepare request
            url = f"{self.api_base}/tweets"
            payload = {
                'text': content
            }

            # Make request
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            
            return {
                'id': data['data']['id'],
                'text': data['data']['text'],
                'created_at': datetime.utcnow().isoformat()
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting tweet: {str(e)}")
            if hasattr(e.response, 'json'):
                error_data = e.response.json()
                logger.error(f"X API error: {error_data}")
            raise

    async def delete_tweet(self, tweet_id: str) -> bool:
        """Delete a tweet using X API v2"""
        try:
            url = f"{self.api_base}/tweets/{tweet_id}"
            response = self.session.delete(url)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting tweet: {str(e)}")
            return False

    async def get_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """Get tweet details using X API v2"""
        try:
            url = f"{self.api_base}/tweets/{tweet_id}"
            params = {
                'tweet.fields': 'created_at,public_metrics,entities'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting tweet: {str(e)}")
            raise

    async def get_user_tweets(self, user_id: str, max_results: int = 10) -> list:
        """Get tweets from a specific user"""
        try:
            url = f"{self.api_base}/users/{user_id}/tweets"
            params = {
                'max_results': max_results,
                'tweet.fields': 'created_at,public_metrics'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()['data']
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting user tweets: {str(e)}")
            raise

    async def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet using X API v2"""
        try:
            url = f"{self.api_base}/users/{self.user_id}/likes"
            payload = {
                'tweet_id': tweet_id
            }
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error liking tweet: {str(e)}")
            return False

    async def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet using X API v2"""
        try:
            url = f"{self.api_base}/users/{self.user_id}/retweets"
            payload = {
                'tweet_id': tweet_id
            }
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error retweeting: {str(e)}")
            return False