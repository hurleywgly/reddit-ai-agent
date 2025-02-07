# Reddit AI Agent Requirements Document

## 1. System Overview
The Reddit AI Agent is an automated system designed to monitor cryptocurrency subreddits for AI-related content and relay relevant information to Discord. The system operates continuously, performing periodic checks and filtering content based on specific criteria.

## 2. Functional Requirements

### 2.1 Data Collection
- **Source Integration**
  - Must connect to Reddit using PRAW API
  - Must access specified subreddits (e.g., r/CryptoMoonShots)
  - Must retrieve a configurable number of "hot" posts (currently 50)

### 2.2 Content Filtering
- **Time-based Filtering**
  - Must only process posts from the last 24 hours
  - Must track post creation timestamps

- **Engagement Filtering**
  - Must filter posts based on minimum upvote threshold (200 upvotes)
  - Must be able to access post score/upvote data

- **Content Relevance Filtering**
  - Must identify AI-related content using keyword matching
  - Must maintain a list of AI-related keywords:
    - Basic AI terms (ai, artificial intelligence)
    - Technical terms (machine learning, neural, deep learning)
    - Product names (gpt, claude, gemini)
    - Concept terms (agent, autonomous)

### 2.3 Content Analysis
- **Text Processing**
  - Must extract and combine post title and body
  - Must handle text safely using getattr for missing attributes
  - Must process text case-insensitively

- **Smart Summarization**
  - Must integrate with Hugging Face API
  - Must generate concise summaries of relevant posts
  - Must handle API limits (500 character limit)
  - Must include error handling for failed API calls

- **Metadata Extraction**
  - Must extract post URLs
  - Must extract post scores
  - Must identify and extract cryptocurrency contract addresses
  - Must capture post creation timestamps

### 2.4 Output Distribution
- **Discord Integration**
  - Must send formatted messages to Discord via webhook
  - Must handle Discord's character limits (2000 chars)
  - Must batch messages appropriately
  - Must include relevant post metadata in messages

### 2.5 Scheduling
- **Automated Execution**
  - Must run automatically at fixed intervals (24 hours)
  - Must maintain continuous operation
  - Must handle scheduling errors gracefully

## 3. Non-Functional Requirements

### 3.1 Performance
- Must process 50 posts within reasonable time
- Must handle API rate limits appropriately
- Must operate with minimal memory footprint

### 3.2 Reliability
- Must implement comprehensive error handling
- Must log all operations and errors
- Must recover from failures automatically
- Must maintain operation across system restarts

### 3.3 Security
- Must secure API credentials using environment variables
- Must not expose sensitive information in logs
- Must handle API tokens securely

### 3.4 Maintainability
- Must use clear code structure and documentation
- Must implement modular design for easy updates
- Must use consistent logging practices
- Must follow Python best practices

## 4. Technical Requirements

### 4.1 Dependencies
- Python 3.10+
- Required packages:
  - praw (Reddit API)
  - python-dotenv (Environment management)
  - apscheduler (Task scheduling)
  - discord-webhook (Discord integration)
  - requests (API calls)

### 4.2 Environment Variables
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- DISCORD_WEBHOOK_URL
- HF_API_TOKEN

### 4.3 Deployment
- Must support containerized deployment
- Must handle cloud platform constraints
- Must maintain logs in appropriate directory

## 5. Monitoring and Maintenance

### 5.1 Logging
- Must log all major operations
- Must include timestamp in logs
- Must log both to file and console
- Must maintain organized log files

### 5.2 Error Handling
- Must catch and log all exceptions
- Must provide meaningful error messages
- Must continue operation after non-critical errors

## 6. Future Considerations
- Support for multiple subreddits
- Configurable filtering criteria
- Advanced AI content detection
- Additional output platforms
- Real-time monitoring capabilities