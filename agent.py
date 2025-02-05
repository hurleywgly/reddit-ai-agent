import os  
import praw  
import logging  
from dotenv import load_dotenv  
from apscheduler.schedulers.blocking import BlockingScheduler  
from discord_webhook import DiscordWebhook  

# Configure logging  
logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[  
        logging.FileHandler('logs/app.log'),  
        logging.StreamHandler()  
    ]  
)  

logger = logging.getLogger(__name__)  

class CryptoAIAgent:  
    def __init__(self):  
        load_dotenv()  
        self.reddit = praw.Reddit(  
            client_id=os.getenv("REDDIT_CLIENT_ID"),  
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),  
            user_agent=os.getenv("REDDIT_USER_AGENT")  
        )  
        self.scheduler = BlockingScheduler()  

    # ... (keep previous analyze_post, send_to_discord methods)  

    def job(self):  
        try:  
            logger.info("Starting daily analysis")  
            # ... (your existing job logic)  
            logger.info("Analysis completed")  
        except Exception as e:  
            logger.error(f"Job failed: {str(e)}")  

    def run(self):  
        self.scheduler.add_job(self.job, 'interval', hours=24)  
        self.scheduler.start()  

if __name__ == "__main__":  
    CryptoAIAgent().run()  