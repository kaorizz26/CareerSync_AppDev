from jobspy import scrape_jobs
import pandas as pd # Import pandas to adjust display settings

# Set options to display all columns and prevent truncation
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', None)

jobs = scrape_jobs(
    site_name=['LinkedIn'],
    search_term='Python Data Analysis Machine Learning',
    
    location='Philippines, Manila',
    results_limit=10
)
print(jobs.head())

# Optional: Reset settings after printing
pd.reset_option('display.max_columns')
pd.reset_option('display.width')
pd.reset_option('display.max_colwidth')
