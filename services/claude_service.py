import os
import anthropic
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        self.client = anthropic.Client(api_key=os.getenv('CLAUDE_API_KEY'))
        self.system_prompt = """
        You are Funnel1, an AI agent specialized in blockchain interactions and X (formerly Twitter) social media management.
        
        When crafting social media actions, use the following formats:
        
        1. Post a new tweet:
        TWEET: <tweet content>
        
        2. Reply to a tweet:
        TWEET: <tweet content>
        REPLY_TO: <tweet_id>
        
        3. Retweet:
        RETWEET: <tweet_id>
        
        4. Like a tweet:
        LIKE: <tweet_id>
        
        For blockchain transactions:
        BLOCKCHAIN: {"to": "address", "value": "amount", "data": "hex_data"}
        
        Keep responses concise and action-oriented. Always validate inputs and consider security implications.
        When crafting tweets, ensure they follow X's guidelines and character limits (280 chars).
        For blockchain transactions, always confirm values and addresses carefully.
        """

    async def get_response(self, message: str, context: Dict[str, Any] = None) -> str:
        try:
            # Prepare messages with context if provided
            messages = [{
                "role": "system",
                "content": self.system_prompt
            }]

            if context:
                # Add relevant context to the conversation
                context_message = "Context:\n"
                for key, value in context.items():
                    context_message += f"{key}: {value}\n"
                messages.append({
                    "role": "assistant",
                    "content": context_message
                })

            # Add user message
            messages.append({
                "role": "user",
                "content": message
            })

            # Get response from Claude
            response = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=messages,
                temperature=0.7
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            raise

    async def validate_tweet_content(self, content: str) -> tuple[bool, str]:
        """Validate tweet content using Claude's understanding of X's policies"""
        try:
            prompt = f"""Please validate if this tweet content follows X's guidelines and policies. 
Tweet content: {content}

Respond with either 'VALID' or 'INVALID: <reason>'"""
            
            response = await self.get_response(prompt)
            is_valid = response.startswith('VALID')
            message = response.split(':', 1)[1].strip() if not is_valid else "Valid tweet content"
            
            return is_valid, message

        except Exception as e:
            logger.error(f"Error validating tweet content: {str(e)}")
            return False, str(e)

    async def suggest_tweet_improvements(self, content: str) -> str:
        """Suggest improvements for tweet content"""
        try:
            prompt = f"""Please suggest improvements for this tweet while maintaining its core message: 
{content}

Consider:
- Engagement potential
- Clarity
- Hashtag usage
- Call to action"""

            response = await self.get_response(prompt)
            return response

        except Exception as e:
            logger.error(f"Error suggesting tweet improvements: {str(e)}")
            raise

    async def analyze_blockchain_transaction(self, transaction: Dict[str, Any]) -> tuple[bool, str]:
        """Analyze and validate blockchain transaction parameters"""
        try:
            prompt = f"""Please analyze this blockchain transaction for security and validity:
{transaction}

Respond with either 'SAFE' or 'UNSAFE: <reason>'"""

            response = await self.get_response(prompt)
            is_safe = response.startswith('SAFE')
            message = response.split(':', 1)[1].strip() if not is_safe else "Transaction appears safe"

            return is_safe, message

        except Exception as e:
            logger.error(f"Error analyzing blockchain transaction: {str(e)}")
            return False, str(e)
