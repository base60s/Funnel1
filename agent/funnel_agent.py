from services.claude_service import ClaudeService
from services.twitter_service import TwitterService
from services.blockchain_service import BlockchainService
import json
import logging

logger = logging.getLogger(__name__)

class FunnelAgent:
    def __init__(self):
        self.claude = ClaudeService()
        self.twitter = TwitterService()
        self.blockchain = BlockchainService()

    async def process_message(self, message: str):
        try:
            response = await self.claude.get_response(message)
            actions = await self._parse_actions(response)
            
            executed_actions = []
            for action in actions:
                try:
                    if action['type'] == 'tweet':
                        result = await self.twitter.post_tweet(action['content'])
                        executed_actions.append({
                            'type': 'tweet',
                            'status': 'success',
                            'result': result
                        })
                    elif action['type'] == 'blockchain':
                        result = await self.blockchain.execute_transaction(action['params'])
                        executed_actions.append({
                            'type': 'blockchain',
                            'status': 'success',
                            'result': result
                        })
                except Exception as e:
                    logger.error(f"Error executing action {action['type']}: {str(e)}")
                    executed_actions.append({
                        'type': action['type'],
                        'status': 'error',
                        'error': str(e)
                    })
            
            return response, executed_actions
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    async def _parse_actions(self, response: str):
        actions = []
        
        if 'TWEET:' in response:
            tweet_content = response.split('TWEET:')[1].split('\n')[0].strip()
            actions.append({
                'type': 'tweet',
                'content': tweet_content
            })

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