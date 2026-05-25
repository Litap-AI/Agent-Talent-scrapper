from playwright.sync_api import sync_playwright
import csv
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def scrape_with_browser(job_title="software engineer", location="remote", max_jobs=10):
    """
    Use real browser to scrape jobs (harder to block)
    """
    jobs = []
    
    with sync_playwright() as p:
        # Launch browser (headless=False shows the browser window)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Build search URL
        url = f"https://www.google.com/search?q={job_title}+{location}+jobs&ibp=htl;jobs"
        
        logging.info(f"Loading: {url}")
        
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for job cards to load
            page.wait_for_selector('div.PwjeAc', timeout=10000)
            
            # Find all job cards
            job_elements = page.query_selector_all('div.PwjeAc')
            
            logging.info(f"Found {len(job_elements)} jobs")
            
            for i, element in enumerate(job_elements[:max_jobs], 1):
                try:
                    # Click to expand job details
                    element.click()
                    time.sleep(2)  # Wait for details to load
                    
                    # Extract title
                    title_elem = page.query_selector('h2.KLsYvd')
                    title = title_elem.inner_text() if title_elem else "Unknown"
                    
                    # Extract company
                    company_elem = page.query_selector('div.nJlQNd')
                    company = company_elem.inner_text() if company_elem else "Unknown"
                    
                    # Extract location
                    location_elem = page.query_selector('div.RP0Xi')
                    job_location = location_elem.inner_text() if location_elem else "Unknown"
                    
                    # Extract description (first 500 chars)
                    desc_elem = page.query_selector('div.HBvzbc')
                    description = desc_elem.inner_text()[:500] if desc_elem else ""
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': job_location,
                        'description': description
                    })
                    
                    logging.info(f"✓ Job {i}: {title} at {company}")
                    
                except Exception as e:
                    logging.error(f"Error on job {i}: {e}")
                    continue
            
        except Exception as e:
            logging.error(f"Browser error: {e}")
        
        finally:
            browser.close()
    
    return jobs

def save_to_csv(jobs, filename='jobs_browser.csv'):
    if not jobs:
        logging.warning("No jobs to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'company', 'location', 'description'])
        writer.writeheader()
        writer.writerows(jobs)
    
    logging.info(f"✓ Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("BROWSER-BASED JOB SCRAPER")
    print("="*60 + "\n")
    
    jobs = scrape_with_browser("data analyst", "remote", max_jobs=5)
    save_to_csv(jobs)
    
    print(f"\n{'='*60}")
    print(f"DONE: Found {len(jobs)} jobs")
    print(f"{'='*60}\n")
    