import feedparser
import csv
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def scrape_rss_jobs(max_jobs=20):
    """
    Scrape jobs from RSS feeds (legal, no blocking)
    """
    jobs = []
    
    # List of job board RSS feeds
    feeds = [
        # RemoteOK (remote jobs)
        'https://remoteok.com/remote-dev-jobs.rss',
        
        # We Work Remotely
        'https://weworkremotely.com/categories/remote-programming-jobs.rss',
        
        # Stack Overflow Jobs
        'https://stackoverflow.com/jobs/feed',
        
        # GitHub Jobs (if still active)
        'https://jobs.github.com/positions.atom',
    ]
    
    for feed_url in feeds:
        try:
            logging.info(f"Fetching: {feed_url}")
            
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                logging.warning(f"No entries in {feed_url}")
                continue
            
            logging.info(f"Found {len(feed.entries)} jobs in feed")
            
            for entry in feed.entries[:max_jobs]:
                # Extract job data
                title = entry.get('title', 'No title')
                link = entry.get('link', '')
                
                # Some feeds have different field names
                company = entry.get('author', 'Unknown')
                if not company or company == 'Unknown':
                    company = entry.get('company', 'Unknown')
                
                # Get description/summary
                description = entry.get('summary', entry.get('description', ''))
                
                # Get publication date
                pub_date = entry.get('published', 'Unknown')
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'url': link,
                    'description': description[:500],  # First 500 chars
                    'published': pub_date,
                    'source': feed_url.split('/')[2]  # Extract domain
                })
                
                logging.info(f"✓ {title} at {company}")
                
        except Exception as e:
            logging.error(f"Error with feed {feed_url}: {e}")
            continue
    
    return jobs

def save_to_csv(jobs, filename='jobs_rss.csv'):
    if not jobs:
        logging.warning("No jobs to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'company', 'url', 'description', 'published', 'source'])
        writer.writeheader()
        writer.writerows(jobs)
    
    logging.info(f"\n✓ SUCCESS: Saved {len(jobs)} jobs to {filename}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RSS FEED JOB SCRAPER (Legal & Reliable)")
    print("="*60 + "\n")
    
    jobs = scrape_rss_jobs(max_jobs=50)
    save_to_csv(jobs)
    
    print(f"\n{'='*60}")
    print(f"TOTAL JOBS COLLECTED: {len(jobs)}")
    print(f"{'='*60}\n")

