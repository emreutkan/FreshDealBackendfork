import os
import requests
import json
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    logger.error("GROQ_API_KEY not found")
    exit(1)

logger.info(f"API key found (starts with {api_key[:8]}...)")

base_url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Test with a simple prompt
test_payload = {
    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
    "messages": [{"role": "user",
                  "content": "Please analyze these customer comments and categorize them into good and bad aspects: ['Food was great!', 'Service was slow']. Format as JSON with good_aspects and bad_aspects keys."}],
    "temperature": 0.3
}

try:
    logger.info("Sending test request to Groq API...")
    response = requests.post(base_url, headers=headers, json=test_payload)

    logger.info(f"Response status code: {response.status_code}")

    # Print full response for debugging
    if response.status_code != 200:
        logger.error(f"API Error: {response.text}")
    else:
        result = response.json()
        logger.info(f"Success! Response: {json.dumps(result, indent=2)[:500]}...")

        # Check if we can extract the content
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            logger.info(f"Content: {content[:500]}...")

            # Try to parse as JSON
            try:
                parsed_content = json.loads(content)
                logger.info(f"Parsed as JSON: {json.dumps(parsed_content, indent=2)}")
            except json.JSONDecodeError as e:
                logger.error(f"Could not parse content as JSON: {e}")

                # Try simple extraction
                good_aspects = []
                bad_aspects = []
                lines = content.split('\n')
                current_section = None

                for line in lines:
                    line = line.strip()
                    if 'good aspects' in line.lower() or 'positive aspects' in line.lower():
                        current_section = 'good'
                        logger.info(f"Found good aspects section: {line}")
                    elif 'bad aspects' in line.lower() or 'negative aspects' in line.lower():
                        current_section = 'bad'
                        logger.info(f"Found bad aspects section: {line}")
                    elif line.startswith('- ') or line.startswith('* '):
                        item = line[2:].strip()
                        if current_section == 'good':
                            good_aspects.append(item)
                        elif current_section == 'bad':
                            bad_aspects.append(item)

                logger.info(f"Extracted good aspects: {good_aspects}")
                logger.info(f"Extracted bad aspects: {bad_aspects}")
        else:
            logger.error(f"Unexpected API response format: {result}")

except requests.exceptions.RequestException as e:
    logger.error(f"Request failed: {e}")
    if hasattr(e, 'response') and e.response is not None:
        logger.error(f"Response text: {e.response.text}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")