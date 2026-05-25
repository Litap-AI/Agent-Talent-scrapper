import requests
from bs4 import BeautifulSoup
import csv
import time
import logging

# Set up logging so you can see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def scrape_indeed_jobs(job_title="python developer", location="remote", max_jobs=10):
    """
    Scrape jobs from Indeed
    """
    jobs = []
    
    # Build the Indeed search URL
    url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location}&fromage=7"
    
    logging.info(f"Scraping: {url}")
    
    # Pretend to be a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
    
    }
    
    try:
        # Download the page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to load page: {e}")
        return []
    
    # Parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all job cards on the page
    job_cards = soup.find_all('div', class_='job_seen_beacon')
    
    if not job_cards:
        logging.warning("No job cards found. Indeed might have changed their HTML structure.")
        return []
    
    logging.info(f"Found {len(job_cards)} job cards")
    
    # Extract data from each job card
    for i, card in enumerate(job_cards[:max_jobs], 1):
        try:
            # Find the job title element
            title_elem = card.find('h2', class_='jobTitle')
            if not title_elem:
                logging.warning(f"Job {i}: No title found, skipping")
                continue
            
            # Find company name
            company_elem = card.find('span', {'data-testid': 'company-name'})
            
            # Find location
            location_elem = card.find('div', {'data-testid': 'text-location'})
            
            # Extract text
            title = title_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            job_location = location_elem.get_text(strip=True) if location_elem else "Unknown"
            
            # Get the job URL
            link_elem = title_elem.find('a')
            if link_elem and link_elem.get('href'):
                job_link = "https://indeed.com" + link_elem['href']
            else:
                job_link = "N/A"
            
            # Store the job data
            jobs.append({
                'title': title,
                'company': company,
                'location': job_location,
                'url': job_link
            })
            
            logging.info(f"✓ Job {i}/{max_jobs}: {title} at {company}")
            
        except Exception as e:
            logging.error(f"✗ Job {i}: Error - {e}")
            continue
        
        # Be polite - wait 3 second between extractions
        time.sleep(3)
    
    return jobs

def save_to_csv(jobs, filename='jobs.csv'):
    """
    Save jobs to CSV file
    """
    if not jobs:
        logging.warning("No jobs to save")
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'company', 'location', 'url'])
            writer.writeheader()
            writer.writerows(jobs)
        
        logging.info(f"\n✓ SUCCESS: Saved {len(jobs)} jobs to {filename}")
        
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")

# Main execution
if __name__ == "__main__":
    print("\n" + "="*60)
    print("INDEED JOB SCRAPER")
    print("="*60 + "\n")
    
    # Scrape jobs
    jobs = scrape_indeed_jobs(
    job_title="data analyst",  # Try this instead
    location="remote",
    max_jobs=5  # Start with fewer jobs
  )
    
    
    # Save to CSV
    save_to_csv(jobs)
    
    print(f"\n{'='*60}")
    print(f"DONE: Found {len(jobs)} jobs")
    print(f"{'='*60}\n")
