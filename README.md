# NewLens API

NewLens API is an AI-powered solution designed to search, analyze, and intelligently summarize the latest news on companies, helping you stay informed with concise and relevant insights.

## Features
- **AI-Powered News Search:** Automatically finds the latest news articles about companies.
- **Intelligent Summarization:** Uses advanced AI models to generate concise, relevant summaries of news content.
- **Company-Focused Insights:** Tailored to deliver actionable information about businesses and organizations.
- **Mock Mode for Testing:** Supports mock responses for development and testing.
- **Cloud-Ready:** Designed for deployment as an AWS Lambda function.

## Usage
- Deploy the Lambda function to AWS.
- Send a request with the company name to receive summarized news insights.
- Use the `ismock` flag in the event payload to enable mock mode for testing.

## Technologies
- **Python** (AWS Lambda)
- **Perplexity AI API** for news analysis and summarization
- **requests** library for HTTP calls

## Getting Started
1. Install dependencies listed in `requirements.txt`.
2. Package the Lambda function with dependencies and the `mock` folder.
3. Deploy to AWS Lambda and configure triggers as needed.

## Repository Structure
- `lambda_function.py`: Main Lambda handler and API integration
- `requirements.txt`: Python dependencies
- `mock/apiresponse.json`: Mock response data for testing

## License
This project is licensed under the MIT License.

# Architecture Decision Record

## Why AWS Lambda for Client Intelligence API

### Selection Criteria

After evaluating multiple deployment options including Google Cloud Run, Azure Container Instances, Railway, and traditional server hosting, AWS Lambda emerged as the optimal choice for this client intelligence aggregation system.

### Key Decision Factors

**1. Pay-Per-Execution Model**
- Lambda's pricing aligns perfectly with our usage pattern of periodic weekly analysis
- Only charged for actual compute time during client analysis (~30 seconds per client)
- No costs during idle periods between scheduled runs
- Estimated monthly cost: <$2 for 100 clients with weekly analysis

**2. Serverless Architecture Benefits**
- Zero infrastructure management overhead
- Automatic scaling based on demand
- Built-in high availability across multiple AZs
- Perfect fit for event-driven intelligence gathering workflow

**3. Ecosystem Integration**
- Native integration with API Gateway for REST endpoints
- CloudWatch for monitoring and logging out-of-the-box
- EventBridge for scheduling weekly analysis tasks
- Seamless integration with MCP (Model Context Protocol) servers
- IAM for fine-grained security controls

**4. Development Velocity**
- Rapid deployment using AWS SAM or Serverless Framework
- Local testing capabilities with SAM Local
- Version management and rollback capabilities
- CI/CD integration with GitHub Actions

**5. Cost Predictability**
- Transparent pricing model with detailed cost breakdown
- Free tier covers development and initial testing (1M requests monthly)
- No surprise charges from always-running instances
- Cost scales linearly with actual usage

### What I Considered But Didn't Choose

**Railway/Render**: These look cool and are easy to use, but they cost $5-20/month even when my app isn't doing anything. That's too much for a student budget when Lambda can do the same thing for free.

**Google Cloud Run**: Pretty similar to Lambda and also cheap, but AWS has better tutorials and more resources for beginners like me.

**Regular Web Hosting**: Would cost $10+ per month and I'd have to learn a bunch of server management stuff that's not really relevant to my project goals.

### Technical Stuff That Matters

- **15-minute timeout**: More than enough time for my app to analyze one client's information
- **Memory**: Can allocate up to 10GB if I need it for heavy AI processing
- **Speed**: A few seconds of startup delay is fine since this isn't a user-facing website
- **No Database Needed**: I can use other AWS services or external databases easily

### Perfect for Learning

This choice lets me focus on the fun parts like building AI agents and web scraping, instead of spending time on boring server maintenance. Plus, if my project actually gets used by real companies, Lambda will scale automatically without me having to rewrite everything.

**Bottom line**: As a student, I get professional-grade hosting for basically free, and I can put "AWS Lambda" on my resume! 🚀


# How to Call the API

To use the NewLens API, you must pass your own PerplexityAI API Key as a Bearer token in the `Authorization` header. Do **not** share your API key publicly.

## Sample CURL Request

```bash
curl --location 'https://b0sceka65j.execute-api.us-east-1.amazonaws.com/dev/getnews' \
	--header 'Authorization: Bearer <YOUR_PERPLEXITY_API_KEY>' \
	--header 'Content-Type: application/json' \
	--data '{
		"ismock": false,
		"clients": [
			{
				"name": "RLDatix Life Sciences",
				"url": "https://www.rldatixlifesciences.com/"
			}
		],
		"categories": [
			"Latest Headlines",
			"Press Release",
			"Financial News"
		]
	}'
```

Replace `<YOUR_PERPLEXITY_API_KEY>` with your own key.

## Sample Python Request

```python
import requests

url = "https://b0sceka65j.execute-api.us-east-1.amazonaws.com/dev/getnews"
headers = {
		"Authorization": "Bearer <YOUR_PERPLEXITY_API_KEY>",
		"Content-Type": "application/json"
}
payload = {
		"ismock": False,
		"clients": [
				{
						"name": "RLDatix Life Sciences",
						"url": "https://www.rldatixlifesciences.com/"
				}
		],
		"categories": [
				"Latest Headlines",
				"Press Release",
				"Financial News"
		]
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

Replace `<YOUR_PERPLEXITY_API_KEY>` with your own key.
