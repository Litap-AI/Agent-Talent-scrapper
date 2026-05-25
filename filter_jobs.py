import csv
import logging
from classifier_direct import is_suitable_for_ai_agents
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def filter_jobs_with_ai(input_file='jobs_rss.csv', output_file='jobs_suitable.csv', min_confidence=70):
    """
    Read RSS jobs and filter with AI classifier
    """
    
    # Read input CSV
    jobs = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            jobs = list(reader)
    except Exception as e:
        logging.error(f"Failed to read {input_file}: {e}")
        return
    
    logging.info(f"Loaded {len(jobs)} jobs from {input_file}")
    
    # Filter with AI
    suitable_jobs = []
    
    for i, job in enumerate(jobs, 1):
        try:
            logging.info(f"\n[{i}/{len(jobs)}] Analyzing: {job['title']}")
            
            # Call AI classifier
            suitable, confidence, reason = is_suitable_for_ai_agents(
                job.get('description', ''),
                job['title']
            )
            
            # Add classification results to job data
            job['ai_suitable'] = 'YES' if suitable else 'NO'
            job['ai_confidence'] = confidence
            job['ai_reason'] = reason
            
            # Only keep jobs above confidence threshold
            if suitable and confidence >= min_confidence:
                suitable_jobs.append(job)
                logging.info(f"  ✓ SUITABLE ({confidence}%): {reason}")
            else:
                logging.info(f"  ✗ Not suitable ({confidence}%): {reason}")
            
            # Rate limiting - Groq free tier
            time.sleep(1)  # 1 second between API calls
            
        except Exception as e:
            logging.error(f"  Error on job {i}: {e}")
            continue
    
    # Save suitable jobs
    if suitable_jobs:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            # Include all fields plus AI classification
            fieldnames = list(suitable_jobs[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(suitable_jobs)
        
        logging.info(f"\n{'='*60}")
        logging.info(f"✓ SUCCESS: Saved {len(suitable_jobs)} suitable jobs to {output_file}")
        logging.info(f"Filtered: {len(jobs)} total → {len(suitable_jobs)} suitable ({len(suitable_jobs)/len(jobs)*100:.1f}%)")
        logging.info(f"{'='*60}\n")
    else:
        logging.warning("No suitable jobs found")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("AI JOB FILTERING PIPELINE")
    print("="*60 + "\n")
    
    # Process first 20 jobs to start (faster for testing)
    # Later change this to process all 75
    
    filter_jobs_with_ai(
        input_file='jobs_rss.csv',
        output_file='jobs_suitable.csv',
        min_confidence=70  # Only keep jobs with 70%+ confidence
    )
