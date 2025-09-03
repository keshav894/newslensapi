
import os
import json
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


def lambda_handler(event, context):
    # Parse input
    print("Lambda event received:", json.dumps(event))
    try:
        body = event.get('body')
        if isinstance(body, str):
            body = json.loads(body)
        # Check for mock mode
        is_mock = body.get('ismock', False)
        if is_mock:
            try:
                with open('mock/apiresponse.json', 'r') as f:
                    mock_data = json.load(f)
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps(mock_data)
                }
            except Exception as e:
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({'error': 'Failed to load mock response', 'details': str(e)})
                }
        clients = body.get('clients', [])
        categories = body.get('categories', [
            'Latest Headlines', 'Acquisitions', 'Management Updates', 'Financials'
        ])
    except Exception as e:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid input', 'details': str(e)})
        }

    # Validate clients
    valid_clients = []
    for client in clients:
        name = client.get('name')
        url = client.get('url', None)
        if not name:
            continue
        valid_clients.append({'name': name, 'url': url})

    if not valid_clients:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'No valid clients provided'})
        }

    # Date range: past quarter (not currently used in prompt, but can be integrated if needed)
    today = datetime.utcnow()
    past_quarter = today - timedelta(days=90)
    date_from = past_quarter.strftime('%Y-%m-%d')
    date_to = today.strftime('%Y-%m-%d')

    perplexity_api_key = os.environ.get('PERPLEXITY_API_KEY')
    if not perplexity_api_key:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Perplexity API key not set'})
        }

    def fetch_perplexity(client):
        name = client['name']
        url = client['url']
        categories_str = ', '.join(categories)
        user_content = (
            f"Provide a complete, valid JSON object with keys: usage, citations, search_results, AI_Summary about {name} company.\n"
            f"search_results is an array with objects having fields: category, title, url, date, last_updated, snippet.\n"
            f"Limit the number of news items to at most 3 per category for performance.\n"
            f"AI_Summary is a concise natural language summary (maximum 200 words) of the most relevant news in the search_results.\n"
            f"If no relevant data is found, reply with an empty search_results array and a snippet message indicating no data.\n"
            f"Do NOT include any 'about {name} company' section.\n"
            f"Return ONLY the JSON object with no extra introduction or extraneous text.\n"
            f"Example:\n"
            f'{{ "usage": {{}}, "citations": [], "search_results": [{{ "category": "Latest Headlines", '
            f'"title": "No relevant data found", "url": "", "date": "", "last_updated": "", "snippet": "No news available."}}],\n'
            f'"AI_Summary": "This is a short summary of the most relevant news for {name}." }}\n'
            f"\nFind and categorize the most relevant news about {name} published in the current quarter. "
            f"Focus on the following categories: {categories_str}."
        )
        payload = json.dumps({
            "model": "sonar",
            "messages": [
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        })
        headers = {
            'Authorization': f'Bearer {perplexity_api_key}',
            'Content-Type': 'application/json'
        }
        try:
            print(f"Requesting Perplexity API for client: {name}, payload: {payload}")
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                data=payload,
                timeout=300
            )
            print(f"Perplexity API response status: {response.status_code}")
            print(f"Perplexity API response body: {response.text}")
            response.raise_for_status()
            resp_json = response.json()
            content = resp_json['choices'][0]['message']['content']
            try:
                data_obj = json.loads(content)
            except json.JSONDecodeError:
                data_obj = {
                    "usage": {},
                    "citations": [],
                    "search_results": []
                }
            return {
                "Name": name,
                "url": url,
                "data": data_obj
            }
        except Exception as e:
            print(f"Error for client {name}: {str(e)}")
            return {
                "Name": name,
                "url": url,
                "error": str(e)
            }

    results_list = []
    with ThreadPoolExecutor(max_workers=min(10, len(valid_clients))) as executor:
        future_to_client = {executor.submit(fetch_perplexity, client): client for client in valid_clients}
        for future in as_completed(future_to_client):
            result = future.result()
            results_list.append(result)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'clients': results_list})
    }
