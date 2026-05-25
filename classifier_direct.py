import requests
import logging
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

logging.basicConfig(level=logging.INFO, format='%(message)s')

API_KEY = "api_key"
API_URL = "api_url"

def is_suitable_for_ai_agents(job_description, job_title):
    """
    Call Groq API directly without using their library
    """
    
    prompt = f"""Is this job suitable for AI agents?

Job: {job_title}
Description: {job_description[:500]}

Answer in this format:
SUITABLE: YES or NO
CONFIDENCE: 0-100
REASON: brief explanation"""

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        # Parse response
        suitable = 'YES' in content.upper() and 'SUITABLE:' in content.upper()
        
        # Extract confidence
        confidence = 75  # Default
        for line in content.split('\n'):
            if 'CONFIDENCE:' in line.upper():
                try:
                    confidence = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
        
        # Extract reason
        reason = "AI analysis complete"
        for line in content.split('\n'):
            if 'REASON:' in line.upper():
                reason = line.split(':', 1)[1].strip()
                break
        
        return suitable, confidence, reason
        
    except Exception as e:
        logging.error(f"API error: {e}")
        return False, 0, f"Error: {e}"

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING DIRECT API CLASSIFIER")
    print("="*60 + "\n")
    
    # Test
    suitable, conf, reason = is_suitable_for_ai_agents(
        "Build Python APIs and data pipelines. Remote work. FastAPI, PostgreSQL, Docker.",
        "Backend Python Engineer"
    )
    
    print(f"Job: Backend Python Engineer")
    print(f"Suitable: {suitable}")
    print(f"Confidence: {conf}%")
    print(f"Reason: {reason}")
    print("\n" + "="*60)
