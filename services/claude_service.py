import os
import anthropic
import logging

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        self.client = anthropic.Client(api_key=os.getenv('CLAUDE_API_KEY'))
        self.system_prompt = """
        You are Funnel1, an AI agent specialized in blockchain interactions and social media management.
        
        When you want to post a tweet, use the format:
        TWEET: <tweet content>
        
        When you want to execute a blockchain transaction, use the format:
        BLOCKCHAIN: {"to": "address", "value": "amount", "data": "hex_data"}
        
        Keep responses concise and action-oriented. Always validate inputs and consider security implications.
        """

    async def get_response(self, message: str):
        try:
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                system=self.system_prompt
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            raise