from groq import Groq
import logging
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


logging.basicConfig(level=logging.INFO, format='%(message)s')

# Hardcode the key temporarily
API_KEY = "api_key"

client = Groq(api_key=API_KEY)

def is_suitable_for_ai_agents(job_description, job_title):
    prompt = f"""Is this job suitable for AI agents?

Job: {job_title}
Description: {job_description[:500]}

Answer: SUITABLE: YES/NO
CONFIDENCE: 0-100
REASON: brief explanation"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=100
        )
        
        result = response.choices[0].message.content.strip()
        
        suitable = 'YES' in result.upper()
        
        # Try to extract confidence
        confidence = 75  # Default
        if 'CONFIDENCE:' in result:
            try:
                conf_line = [l for l in result.split('\n') if 'CONFIDENCE' in l][0]
                confidence = int(''.join(filter(str.isdigit, conf_line)))
            except:
                pass
        
        # Extract reason
        reason = result.split('REASON:')[-1].strip() if 'REASON:' in result else result[:100]
        
        return suitable, confidence, reason
        
    except Exception as e:
        return False, 0, f"Error: {e}"

if __name__ == "__main__":
    # Quick test
    suitable, conf, reason = is_suitable_for_ai_agents(
        "Build Python APIs. Remote work. FastAPI.",
        "Backend Engineer"
    )
    print(f"Suitable: {suitable}, Confidence: {conf}%")
    print(f"Reason: {reason}")

