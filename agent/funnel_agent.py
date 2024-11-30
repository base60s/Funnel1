from services.claude_service import ClaudeService
from services.twitter_service import TwitterService
from services.blockchain_service import BlockchainService
from utils.monitoring import ActivityMonitor
import json
import logging
import re

logger = logging.getLogger(__name__)

class FunnelAgent:
    def __init__(self):
        self.claude = ClaudeService()
        self.twitter = TwitterService()
        self.blockchain = BlockchainService()
        self.monitor = ActivityMonitor()

    async def process_message(self, message: str):
        try:
            # Get AI response
            response = await self.claude.get_response(message)
            await self.monitor.log_activity('claude_request', {
                'message': message,
                'response_length': len(response)
            })

            # Parse and execute actions
            actions = await self._parse_actions(response)
            executed_actions = []
            
            for action in actions:
                try:
                    if action['type'] == 'tweet':
                        if 'reply_to' in action:
                            # Handle reply to tweet
                            result = await self.twitter.post_tweet(
                                content=action['content'],
                                reply_to=action['reply_to']
                            )
                        else:
                            # Regular tweet
                            result = await self.twitter.post_tweet(action['content'])
                        
                        await self.monitor.log_activity('twitter', {
                            'content': action['content'],
                            'result': result
                        })
                        executed_actions.append({
                            'type': 'tweet',
                            'status': 'success',
                            'result': result
                        })
                        
                    elif action['type'] == 'blockchain':
                        result = await self.blockchain.execute_transaction(action['params'])
                        await self.monitor.log_activity('blockchain', {
                            'params': action['params'],
                            'result': result
                        })
                        executed_actions.append({
                            'type': 'blockchain',
                            'status': 'success',
                            'result': result
                        })
                        
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Error executing action {action['type']}: {error_msg}")
                    await self.monitor.log_activity('error', {
                        'action_type': action['type'],
                        'error': error_msg
                    })
                    executed_actions.append({
                        'type': action['type'],
                        'status': 'error',
                        'error': error_msg
                    })
            
            return response, executed_actions
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.monitor.log_activity('error', {
                'error_type': 'process_message',
                'error': str(e)
            })
            raise

    async def _parse_actions(self, response: str):
        actions = []
        
        # Parse tweet actions with advanced patterns
        tweet_patterns = [
            r'TWEET: (?P<content>[^\n]+)(?:\nREPLY_TO: (?P<reply_to>[^\n]+))?',
            r'RETWEET: (?P<tweet_id>[^\n]+)',
            r'LIKE: (?P<like_tweet_id>[^\n]+)'
        ]
        
        for pattern in tweet_patterns:
            matches = re.finditer(pattern, response)
            for match in matches:
                action = {'type': 'tweet'}
                if 'content' in match.groupdict():
                    action['content'] = match.group('content').strip()
                if 'reply_to' in match.groupdict() and match.group('reply_to'):
                    action['reply_to'] = match.group('reply_to').strip()
                if 'tweet_id' in match.groupdict():
                    action['type'] = 'retweet'
                    action['tweet_id'] = match.group('tweet_id').strip()
                if 'like_tweet_id' in match.groupdict():
                    action['type'] = 'like'
                    action['tweet_id'] = match.group('like_tweet_id').strip()
                actions.append(action)

        # Parse blockchain actions
        if 'BLOCKCHAIN:' in response:
            try:
                blockchain_section = response.split('BLOCKCHAIN:')[1].split('\n')[0].strip()
                params = json.loads(blockchain_section)
                actions.append({
                    'type': 'blockchain',
                    'params': params
                })
            except json.JSONDecodeError:
                logger.error("Failed to parse blockchain parameters")
                
        return actions

    async def get_activity_report(self):
        """Generate a report of recent activities"""
        return await self.monitor.generate_report()