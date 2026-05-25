import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
from classifier import is_suitable_for_ai_agents

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def scrape_and_classify(job_title="software engineer", max_jobs=10):
    """
    Scrape jobs and filter with AI
    """
    # ... (use scraping code from earlier)
    
    jobs = []
    url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}&l=remote&fromage=7"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    
    suitable_jobs = []
    
    for i, card in enumerate(job_cards[:max_jobs], 1):
        try:
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            company = card.find('span', {'data-testid': 'company-name'}).get_text(strip=True)
            
            link_elem = title_elem.find('a')
            job_link = "https://indeed.com" + link_elem['href']
            
            # Fetch description
            logging.info(f"{i}/{max_jobs}: Fetching {title}...")
            desc_response = requests.get(job_link, headers=headers, timeout=10)
            desc_soup = BeautifulSoup(desc_response.content, 'html.parser')
            desc_elem = desc_soup.find('div', id='jobDescriptionText')
            description = desc_elem.get_text(separator=' ', strip=True)[:2000] if desc_elem else ""
            
            # AI Classification
            suitable, reason = is_suitable_for_ai_agents(description, title)
            
            job_data = {
                'title': title,
                'company': company,
                'url': job_link,
                'description': description,
                'suitable': suitable,
                'reason': reason
            }
            
            if suitable:
                suitable_jobs.append(job_data)
                logging.info(f"✓ SUITABLE: {title} - {reason}")
            else:
                logging.info(f"✗ Not suitable: {title} - {reason}")
            
            time.sleep(3)  # 3 sec between jobs (LLM + scraping)
            
        except Exception as e:
            logging.error(f"Error on job {i}: {e}")
            continue
    
    return suitable_jobs

def save_suitable_jobs(jobs, filename='suitable_jobs.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'company', 'url', 'description', 'reason'])
        writer.writeheader()
        for job in jobs:
            writer.writerow({
                'title': job['title'],
                'company': job['company'],
                'url': job['url'],
                'description': job['description'][:500],  # Truncate for CSV
                'reason': job['reason']
            })
    logging.info(f"✓ Saved {len(jobs)} suitable jobs to {filename}")

if __name__ == "__main__":
    suitable = scrape_and_classify("data analyst", max_jobs=10)
    save_suitable_jobs(suitable)
    print(f"\nFound {len(suitable)} suitable jobs out of 10 scraped")

    