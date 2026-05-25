import requests
from bs4 import BeautifulSoup
import csv
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_job_description(job_url):
    """
    Fetch full job description from Indeed job page
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(job_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Indeed stores job description in div with id="jobDescriptionText"
        desc_elem = soup.find('div', id='jobDescriptionText')
        
        if desc_elem:
            # Get all text, clean up whitespace
            description = desc_elem.get_text(separator=' ', strip=True)
            return description[:2000]  # Limit to 2000 chars
        else:
            logging.warning(f"No description found at {job_url}")
            return "Description not available"
            
    except Exception as e:
        logging.error(f"Failed to fetch description: {e}")
        return "Error fetching description"

def scrape_indeed_jobs_with_details(job_title="ai engineer", location="remote", max_jobs=5):
    """
    Scrape jobs AND their full descriptions
    """
    jobs = []
    url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location}&fromage=7"
    
    logging.info(f"Scraping: {url}")
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logging.error(f"Failed to load page: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    
    logging.info(f"Found {len(job_cards)} jobs")
    
    for i, card in enumerate(job_cards[:max_jobs], 1):
        try:
            title_elem = card.find('h2', class_='jobTitle')
            company_elem = card.find('span', {'data-testid': 'company-name'})
            location_elem = card.find('div', {'data-testid': 'text-location'})
            
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            job_location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            link_elem = title_elem.find('a')
            if link_elem and link_elem.get('href'):
                job_link = "https://indeed.com" + link_elem['href']
            else:
                logging.warning(f"No link for job {i}")
                continue
            
            logging.info(f"Job {i}: Fetching details for '{title}'...")
            
            # FETCH FULL DESCRIPTION
            description = get_job_description(job_link)
            
            jobs.append({
                'title': title,
                'company': company,
                'location': job_location,
                'url': job_link,
                'description': description
            })
            
            logging.info(f"✓ Saved {title} ({len(description)} chars)")
            
            # Be extra polite when clicking into job pages
            time.sleep(2)
            
        except Exception as e:
            logging.error(f"Error on job {i}: {e}")
            continue
    
    return jobs

def save_to_csv(jobs, filename='jobs_detailed.csv'):
    if not jobs:
        logging.warning("No jobs to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'company', 'location', 'url', 'description'])
        writer.writeheader()
        writer.writerows(jobs)
    
    logging.info(f"✓ Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    # Start with just 5 jobs to test
    jobs = scrape_indeed_jobs_with_details("python developer", "remote", max_jobs=5)
    save_to_csv(jobs)
    