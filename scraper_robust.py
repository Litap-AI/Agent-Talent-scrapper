import requests
from bs4 import BeautifulSoup
import csv
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

def scrape_indeed_jobs(job_title="software engineer", location="remote", max_jobs=10):
    jobs = []
    url = f"https://www.indeed.com/jobs?q={job_title}&l={location}&fromage=7"
    
    logging.info(f"Starting scrape: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch page: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    
    logging.info(f"Found {len(job_cards)} job cards")
    
    for i, card in enumerate(job_cards[:max_jobs], 1):
        try:
            title_elem = card.find('h2', class_='jobTitle')
            company_elem = card.find('span', {'data-testid': 'company-name'})
            location_elem = card.find('div', {'data-testid': 'text-location'})
            
            if not title_elem:
                logging.warning(f"Job {i}: Missing title, skipping")
                continue
            
            title = title_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            job_location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            link_elem = title_elem.find('a')
            job_link = "https://indeed.com" + link_elem['href'] if link_elem and link_elem.get('href') else "N/A"
            
            jobs.append({
                'title': title,
                'company': company,
                'location': job_location,
                'url': job_link
            })
            
            logging.info(f"✓ Job {i}: {title} at {company}")
            
        except Exception as e:
            logging.error(f"✗ Job {i}: Parsing failed - {e}")
            continue
        
        time.sleep(1)
    
    logging.info(f"Scraping complete: {len(jobs)} jobs collected")
    return jobs

def save_to_csv(jobs, filename='jobs.csv'):
    if not jobs:
        logging.warning("No jobs to save")
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'company', 'location', 'url'])
            writer.writeheader()
            writer.writerows(jobs)
        logging.info(f"✓ Saved {len(jobs)} jobs to {filename}")
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")

if __name__ == "__main__":
    jobs = scrape_indeed_jobs("ai engineer", "remote", max_jobs=15)
    save_to_csv(jobs)
    