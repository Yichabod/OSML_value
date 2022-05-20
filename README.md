# OSML_value
Estimating the economic value of open source machine learning repositories by scraping Github.

This is the code repository for an upcoming paper by Max Langenkamp and Daniel Yue on estimating the value of open source ML repositories

### File explanations:
`Copy of List of tools for MLOps_v4 - Tools.csv`: the csv containing the ML repos of interest including links to the relevant Github repositories
`scraped_contributor_information_for_repos.csv`: the file containing the scraped contributor information. At first this should not exist, but as the script runs/ inevitably has to rerun as Github rate limits the scraping, this file will be used to avoid duplicating effort.
`scrape_ml_repo.py`: contains all the code to scrape. It is very messy (in large part because of rush + Github rate limiting)

### Quick start instructions
1. Git clone repo

2. Create virtualenv and install dependencies
`python3 -m venv env && source env/bin/activate`
`pip3 install -r requirements.txt`

3. If you want to run the scraping file from scratch, you should rename or delete `scraped_contributor_information_for_repos.csv` otherwise no scraping will happen.


Cautionary note: Github rate limits prevent you from scraping all the repos in our list at once. You can either wait an hour to continue again or else use a VPN once you detect blocking.
