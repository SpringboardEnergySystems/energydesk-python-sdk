import logging
import os
from energydeskapi.copilot.copilot_api import CopilotApi
from energydeskapi.sdk.common_utils import init_api
import openai, requests, json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    handlers=[logging.FileHandler("energydesk_client.log"),
                              logging.StreamHandler()])

def get_copilot_contextx(api_conn):

    data= CopilotApi.get_available_contexts(api_conn)
    return data

def ask_copilot_question(api_conn, context_url, question):
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    headers = {"Authorization": "Token " + api_conn.get_token()}
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    mcp_response = requests.get(context_url)
    mcp_context = mcp_response.json()
    print(json.dumps(mcp_context, indent=2))

    #  Extract all endpoints from the MCP context, they may be at any level in the JSON structure
    if 'endpoints' in mcp_context:
        all_endpoints = mcp_context['endpoints']
    else:
        # If endpoints are nested, we need to find them
        def extract_endpoints(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == 'endpoints':
                        return value
                    elif isinstance(value, (dict, list)):
                        result = extract_endpoints(value)
                        if result:
                            return result
            elif isinstance(data, list):
                for item in data:
                    result = extract_endpoints(item)
                    if result:
                        return result
            return []

        all_endpoints = extract_endpoints(mcp_context)

    list_endpoint = next((ep for ep in all_endpoints), None)
    if list_endpoint:
        available_params = [p['name'] for p in list_endpoint.get('query_params', [])]
    else:
        available_params = []

    # Step 3: Use OpenAI to interpret the question and suggest an API call
    prompt = (
        f"Given the following MCP context: {mcp_context}\n"
        f"The available query parameters for the query are: {available_params}\n"
        f"How would you call the API to: {question}?\n"
        f"Respond with the full URL including the most relevant query parameters and method only."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    ai_suggestion = response.choices[0].message.content
    print("AI Suggestion:", ai_suggestion, response.choices[0].message)
    method, url = ai_suggestion.split(" ")
    final_url = api_conn.get_base_url() + url
    print("Final URL:", final_url)
    data = requests.get(final_url, headers=headers)
    for res in data.json()['results']:
        print("Description:", res.get('description', 'No description available'))


if __name__ == '__main__':
    api_conn=init_api()
    contexts=get_copilot_contextx(api_conn)
    for ctx in contexts:
        if ctx.description=="Assets":
            ask_copilot_question(api_conn, ctx.context_url, "What are the asset types available in the system?")


