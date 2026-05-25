import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import urllib.parse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def scrape_google_jobs(job_title="software engineer", location="remote", max_jobs=10):
    """
    Scrape jobs from Google Jobs (via SerpApi free alternative)
    """
    jobs = []
    
    # Build Google search URL for jobs
    query = f"{job_title} {location} jobs"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}&ibp=htl;jobs"
    
    logging.info(f"Searching Google Jobs: {query}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to load page: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Google Jobs uses different selectors
    # Find job cards
    job_cards = soup.find_all('div', class_='PwjeAc')
    
    if not job_cards:
        logging.warning("No jobs found via Google Jobs")
        # Try alternative selector
        job_cards = soup.find_all('li', class_='iFjolb')
    
    logging.info(f"Found {len(job_cards)} job listings")
    
    for i, card in enumerate(job_cards[:max_jobs], 1):
        try:
            # Extract title
            title_elem = card.find('div', class_='BjJfJf')
            if not title_elem:
                title_elem = card.find('h2')
            
            # Extract company
            company_elem = card.find('div', class_='vNEEBe')
            
            # Extract location
            location_elem = card.find('div', class_='Qk80Jf')
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                company = company_elem.get_text(strip=True) if company_elem else "Unknown"
                job_location = location_elem.get_text(strip=True) if location_elem else "Unknown"
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': job_location,
                    'source': 'Google Jobs'
                })
                
                logging.info(f"✓ Job {i}: {title} at {company}")
            
        except Exception as e:
            logging.error(f"Error parsing job {i}: {e}")
            continue
    
    return jobs

def save_to_csv(jobs, filename='jobs_google.csv'):
    if not jobs:
        logging.warning("No jobs to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'company', 'location', 'source'])
        writer.writeheader()
        writer.writerows(jobs)
    
    logging.info(f"✓ Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("GOOGLE JOBS SCRAPER")
    print("="*60 + "\n")
    
    jobs = scrape_google_jobs("business analyst", "remote", max_jobs=10)
    save_to_csv(jobs)
    
    print(f"\n{'='*60}")
    print(f"DONE: Found {len(jobs)} jobs")
    print(f"{'='*60}\n")
