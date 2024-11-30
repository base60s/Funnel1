import os
import requests
from requests_oauthlib import OAuth2Session
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class TwitterService:
    def __init__(self):
        self.api_base = 'https://api.twitter.com/2'
        self.oauth2_base = 'https://api.twitter.com/oauth2'
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

    async def post_tweet(self, content: str, reply_to: Optional[str] = None, media_ids: List[str] = None) -> Dict[str, Any]:
        """Post a tweet using X API v2"""
        try:
            # Validate tweet content
            if len(content) > 280:
                raise ValueError("Tweet exceeds 280 characters")

            # Prepare request
            url = f"{self.api_base}/tweets"
            payload = {'text': content}

            # Add reply settings if replying to a tweet
            if reply_to:
                payload['reply'] = {
                    'in_reply_to_tweet_id': reply_to
                }

            # Add media if provided
            if media_ids:
                payload['media'] = {
                    'media_ids': media_ids
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

    async def upload_media(self, media_path: str) -> str:
        """Upload media to X"""
        try:
            # X's media upload endpoint is still v1.1
            url = 'https://upload.twitter.com/1.1/media/upload.json'
            
            files = {
                'media': open(media_path, 'rb')
            }
            
            response = requests.post(
                url,
                files=files,
                auth=OAuth2Session(
                    self.api_key,
                    token={
                        'access_token': self.access_token,
                        'token_type': 'bearer'
                    }
                )
            )
            response.raise_for_status()
            
            return response.json()['media_id_string']
            
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            raise

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information by username"""
        try:
            url = f"{self.api_base}/users/by/username/{username}"
            params = {
                'user.fields': 'description,public_metrics,profile_image_url,verified'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()['data']
            
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise

    async def search_tweets(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search tweets using X API v2"""
        try:
            url = f"{self.api_base}/tweets/search/recent"
            params = {
                'query': query,
                'max_results': max_results,
                'tweet.fields': 'created_at,public_metrics,entities',
                'expansions': 'author_id',
                'user.fields': 'username,verified'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()['data']
            
        except Exception as e:
            logger.error(f"Error searching tweets: {str(e)}")
            raise

    async def create_poll(self, question: str, options: List[str], duration_minutes: int = 1440) -> Dict[str, Any]:
        """Create a poll tweet"""
        try:
            url = f"{self.api_base}/tweets"
            payload = {
                'text': question,
                'poll': {
                    'options': options,
                    'duration_minutes': duration_minutes
                }
            }
            
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            return response.json()['data']
            
        except Exception as e:
            logger.error(f"Error creating poll: {str(e)}")
            raise

    async def get_tweet_metrics(self, tweet_id: str) -> Dict[str, Any]:
        """Get detailed metrics for a tweet"""
        try:
            url = f"{self.api_base}/tweets/{tweet_id}"
            params = {
                'tweet.fields': 'public_metrics,non_public_metrics,organic_metrics'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            return response.json()['data']['public_metrics']
            
        except Exception as e:
            logger.error(f"Error getting tweet metrics: {str(e)}")
            raise

    async def manage_list(self, action: str, list_id: str = None, name: str = None, description: str = None) -> Dict[str, Any]:
        """Manage X lists (create, update, delete)"""
        try:
            if action == 'create':
                url = f"{self.api_base}/lists"
                payload = {
                    'name': name,
                    'description': description
                }
                response = self.session.post(url, json=payload)
            
            elif action == 'update':
                url = f"{self.api_base}/lists/{list_id}"
                payload = {}
                if name:
                    payload['name'] = name
                if description:
                    payload['description'] = description
                response = self.session.put(url, json=payload)
            
            elif action == 'delete':
                url = f"{self.api_base}/lists/{list_id}"
                response = self.session.delete(url)
            
            else:
                raise ValueError(f"Invalid action: {action}")
            
            response.raise_for_status()
            return response.json().get('data', {'success': True})
            
        except Exception as e:
            logger.error(f"Error managing list: {str(e)}")
            raise