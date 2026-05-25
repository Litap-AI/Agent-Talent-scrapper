from groq import Groq
import logging
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


logging.basicConfig(level=logging.INFO, format='%(message)s')

# Load API key - simple approach
try:
    # Try importing from config.py first
    from config import GROQ_API_KEY
    API_KEY = "api_key"
except ImportError:
    # If config.py doesn't exist, try .env
    import os
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("ERROR: No API key found in config.py or .env file")

# Initialize Groq client with just the API key
client = Groq(api_key=API_KEY)

def is_suitable_for_ai_agents(job_description, job_title):
    """
    Use LLM to classify if job can be done by AI agents
    
    Returns: (suitable: bool, confidence: int, reason: str)
    """
    
    prompt = f"""Analyze if this job can be performed by AI agents.

AI agents CAN do:
- Software development (APIs, web apps, scripts)
- Data analysis and processing
- Content writing and editing  
- Research and data gathering
- Customer support via chat/email
- Document processing and automation
- API integrations
- Quality assurance testing
- Social media management
- Basic graphic design

AI agents CANNOT do:
- Physical tasks (delivery, construction, healthcare)
- In-person meetings or presentations
- Jobs requiring licenses (medical, legal, accounting)
- Hardware installation
- Jobs explicitly requiring "human touch"
- Management roles requiring strategic decisions

Job Title: {job_title}

Job Description (excerpt):
{job_description[:800]}

Respond in EXACTLY this format:
SUITABLE: YES or NO
CONFIDENCE: (0-100)
REASON: (one sentence)

Example:
SUITABLE: YES
CONFIDENCE: 85
REASON: Role focuses on API development and automated testing, both well-suited for AI agents.

Now analyze:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=150
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse response
        lines = result.split('\n')
        
        suitable = False
        confidence = 0
        reason = "Unable to parse response"
        
        for line in lines:
            if line.startswith('SUITABLE:'):
                suitable = 'YES' in line.upper()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = int(''.join(filter(str.isdigit, line)))
                except:
                    confidence = 50
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()
        
        return suitable, confidence, reason
        
    except Exception as e:
        logging.error(f"LLM error: {e}")
        return False, 0, f"Error: {e}"

# Test function
if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING AI CLASSIFIER")
    print("="*60 + "\n")
    
    # Test case 1: Good for AI
    test1 = "We need a Python developer to build REST APIs and automate data pipelines. Fully remote. Tech: FastAPI, PostgreSQL, Docker."
    suitable, conf, reason = is_suitable_for_ai_agents(test1, "Backend Python Developer")
    print(f"Test 1: Backend Developer")
    print(f"  → Suitable: {suitable}")
    print(f"  → Confidence: {conf}%")
    print(f"  → Reason: {reason}\n")
    
    # Test case 2: Not good for AI  
    test2 = "Looking for a nurse to work in our ICU. Must have active RN license. In-person 12-hour shifts."
    suitable, conf, reason = is_suitable_for_ai_agents(test2, "ICU Nurse")
    print(f"Test 2: ICU Nurse")
    print(f"  → Suitable: {suitable}")
    print(f"  → Confidence: {conf}%")
    print(f"  → Reason: {reason}\n")
    
    print("="*60)
