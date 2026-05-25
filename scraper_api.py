import requests
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def scrape_adzuna_jobs(job_title="python developer", location="us", max_jobs=10):
    """
    Use Adzuna API (free tier: 1000 calls/month)
    Get API key at: https://developer.adzuna.com/signup
    """
    
    # You need to sign up for free API key
    APP_ID = "YOUR_APP_ID"  # Get from Adzuna
    APP_KEY = "YOUR_APP_KEY"
    
    url = f"https://api.adzuna.com/v1/api/jobs/{location}/search/1"
    
    params = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'results_per_page': max_jobs,
        'what': job_title,
        'where': 'remote',
        'content-type': 'application/json'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        jobs = []
        for result in data.get('results', []):
            jobs.append({
                'title': result.get('title'),
                'company': result.get('company', {}).get('display_name', 'Unknown'),
                'location': result.get('location', {}).get('display_name', 'Unknown'),
                'description': result.get('description', '')[:500],
                'url': result.get('redirect_url', '')
            })
            
            logging.info(f"✓ {result.get('title')} at {result.get('company', {}).get('display_name')}")
        
        return jobs
        
    except Exception as e:
        logging.error(f"API error: {e}")
        return []

def save_to_csv(jobs, filename='jobs_api.csv'):
    if not jobs:
        logging.warning("No jobs to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'company', 'location', 'description', 'url'])
        writer.writeheader()
        writer.writerows(jobs)
    
    logging.info(f"✓ Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    # Note: You need to sign up for Adzuna API first
    jobs = scrape_adzuna_jobs("software engineer", max_jobs=10)
    save_to_csv(jobs)
    