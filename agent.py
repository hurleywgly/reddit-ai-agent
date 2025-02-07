import os  
import praw  
import logging  
from dotenv import load_dotenv  
from apscheduler.schedulers.blocking import BlockingScheduler  
from discord_webhook import DiscordWebhook  
import requests
from datetime import datetime, timedelta

# Create logs directory if missing
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Configure logging  
logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[  
        logging.StreamHandler()  # This will output to Render's log stream
    ]  
)

logger = logging.getLogger(__name__)  

class CryptoAIAgent:  
    def __init__(self):  
        load_dotenv()  
        self.reddit = praw.Reddit(  
            client_id=os.getenv("REDDIT_CLIENT_ID"),  
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),  
            user_agent="CryptoAIAgent/1.0"  # More specific user agent
        )  
        self.scheduler = BlockingScheduler()
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.hf_api_token = os.getenv("HF_API_TOKEN")
        
    def summarize_with_api(self, text):
        """Use Hugging Face API to summarize text"""
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {self.hf_api_token}"}
        
        # Truncate text if too long (API limit)
        max_length = 500
        truncated_text = text[:max_length] + "..." if len(text) > max_length else text
        
        # BART-specific prompt format
        prompt = f"""Analyze this cryptocurrency post and determine if it's AI-related:
        {truncated_text}
        
        If it mentions AI/ML technology, provide key points. If not AI-related or seems like a scam, state that clearly."""

        try:
            response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
            
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return "Error analyzing post content."
                
            summary = response.json()[0]['summary_text'].strip()
            return summary
                
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return "Error analyzing post content."

    def analyze_post(self, post):
        """Analyze a single Reddit post for AI-related content"""
        try:
            # Only consider posts from last 24 hours
            post_time = datetime.fromtimestamp(post.created_utc)
            if datetime.now() - post_time > timedelta(hours=24):
                return None
                
            # Increased minimum score threshold to 200
            if post.score < 200:  # Filter out low-engagement posts
                return None
                
            # Basic criteria for AI-related content
            ai_keywords = [
                'ai', 'artificial intelligence', 'machine learning', 'neural', 
                'deep learning', 'llm', 'language model', 'transformer',
                'agent', 'autonomous', 'gpt', 'claude', 'gemini'
            ]
            
            # Safely get post content
            title = getattr(post, 'title', '').lower()
            selftext = getattr(post, 'selftext', '').lower()
            content = f"{title} {selftext}"
            
            ai_related = any(keyword in content for keyword in ai_keywords)
            
            if ai_related:
                # Get LLM summary
                summary = self.summarize_with_api(f"{post.title}\n{post.selftext}")
                
                # Extract contract address
                contract_address = None
                import re
                contract_pattern = r'0x[a-fA-F0-9]{40}'
                contract_matches = re.findall(contract_pattern, post.selftext)
                if contract_matches:
                    contract_address = contract_matches[0]
                
                return {
                    'title': post.title,
                    'url': f"https://reddit.com{post.permalink}",
                    'score': post.score,
                    'contract': contract_address,
                    'summary': summary,
                    'created_utc': post.created_utc
                }
        except Exception as e:
            logger.error(f"Error analyzing post: {str(e)}")
        return None

    def send_to_discord(self, insights):
        """Send formatted insights to Discord"""
        if not insights:
            logger.info("No insights to send to Discord")
            return
            
        # Split insights into chunks to respect Discord's 2000 char limit
        def create_message_chunk(insights_subset):
            message = "🤖 **AI Crypto Updates**\n\n"
            for insight in insights_subset:
                chunk = (
                    f"📊 **{insight['title']}**\n"
                    f"💡 {insight['summary']}\n"
                    f"🔗 {insight['url']}\n"
                    f"⭐ Score: {insight['score']}\n"
                )
                if insight['contract']:
                    chunk += f"📝 Contract: `{insight['contract']}`\n"
                chunk += "\n"
                
                # Check if adding this chunk would exceed limit
                if len(message + chunk) > 1900:  # Leave some margin
                    return message
                message += chunk
            return message

        # Split insights into multiple messages if needed
        current_chunk = []
        for insight in insights:
            current_chunk.append(insight)
            if len(current_chunk) >= 5:  # Send max 5 insights per message
                try:
                    message = create_message_chunk(current_chunk)
                    webhook = DiscordWebhook(url=self.discord_webhook_url, content=message)
                    response = webhook.execute()
                    logger.info("Successfully sent message chunk to Discord")
                except Exception as e:
                    logger.error(f"Failed to send to Discord: {str(e)}")
                current_chunk = []
        
        # Send any remaining insights
        if current_chunk:
            try:
                message = create_message_chunk(current_chunk)
                webhook = DiscordWebhook(url=self.discord_webhook_url, content=message)
                response = webhook.execute()
                logger.info("Successfully sent final message chunk to Discord")
            except Exception as e:
                logger.error(f"Failed to send to Discord: {str(e)}")

    def job(self):  
        try:  
            logger.info("Starting daily analysis")
            
            # Get posts from CryptoMoonShots, focusing on hot posts
            subreddit = self.reddit.subreddit('CryptoMoonShots')
            hot_posts = subreddit.hot(limit=50)  # Increased from 25 to get more potential high-scoring posts
            
            # Analyze posts
            insights = []
            for post in hot_posts:
                analysis = self.analyze_post(post)
                if analysis:
                    insights.append(analysis)
            
            # Send to Discord
            if insights:
                logger.info(f"Found {len(insights)} relevant posts")
                self.send_to_discord(insights)
            else:
                logger.info("No relevant posts found")
                
            logger.info("Analysis completed")
        except Exception as e:  
            logger.error(f"Job failed: {str(e)}")  

    def health_check(self):
        """Verify all connections are working"""
        try:
            # Test Reddit connection
            self.reddit.user.me()
            
            # Test Discord webhook
            test_webhook = DiscordWebhook(
                url=self.discord_webhook_url,
                content="🟢 CryptoAIAgent health check"
            )
            test_webhook.execute()
            
            logger.info("Health check passed - all connections working")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def run(self):
        try:
            logger.info("Starting one-time job execution...")
            if self.health_check():
                self.job()
                logger.info("Job completed successfully")
            else:
                raise Exception("Health check failed")
        except Exception as e:
            logger.error(f"Error in run method: {str(e)}")
            raise

if __name__ == "__main__":  
    # Remove test_mode=True to run in production mode
    CryptoAIAgent().run()