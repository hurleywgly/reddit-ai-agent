import os
from dotenv import load_dotenv
import praw
import requests
from discord_webhook import DiscordWebhook

def test_env():
    load_dotenv()
    
    # Test environment variables
    required_vars = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "REDDIT_USER_AGENT",
        "DISCORD_WEBHOOK_URL",
        "HF_API_TOKEN"
    ]
    
    print("\n=== Testing Environment Variables ===")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set")
            # Print first/last few chars for verification
            print(f"   Value preview: {value[:4]}...{value[-4:]}")
        else:
            print(f"❌ {var} is missing!")

def test_reddit():
    print("\n=== Testing Reddit API ===")
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
        
        # Test connection by getting a subreddit
        subreddit = reddit.subreddit("CryptoMoonShots")
        post = next(subreddit.hot(limit=1))
        print(f"✅ Reddit connection successful")
        print(f"   Sample post title: {post.title}")
    except Exception as e:
        print(f"❌ Reddit connection failed: {str(e)}")

def test_discord():
    print("\n=== Testing Discord Webhook ===")
    try:
        webhook = DiscordWebhook(
            url=os.getenv("DISCORD_WEBHOOK_URL"),
            content="🤖 Test message from CryptoAIAgent"
        )
        response = webhook.execute()
        print(f"✅ Discord webhook test successful")
    except Exception as e:
        print(f"❌ Discord webhook test failed: {str(e)}")

def test_huggingface():
    print("\n=== Testing Hugging Face API ===")
    
    # Test multiple models in same order as agent.py
    models = [
        "facebook/bart-large-cnn",        # Primary model
        "google/flan-t5-base",           # Fallback option 1
        "sshleifer/distilbart-cnn-12-6"  # Fallback option 2
    ]
    
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}
    test_input = "Summarize this: AI technology is advancing rapidly."
    
    for model in models:
        print(f"\nTesting model: {model}")
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        
        try:
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": test_input}
            )
            
            if response.status_code == 200:
                print(f"✅ Success with {model}")
                print(f"   Response: {response.json()}")
                print(f"   This model is ready to use!")
                return  # Exit after finding first working model
            else:
                print(f"❌ Failed with {model}")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing {model}: {str(e)}")
    
    print("\n❌ No models were successful. Please check your token permissions.")

if __name__ == "__main__":
    test_env()
    test_reddit()
    test_discord()
    test_huggingface() 