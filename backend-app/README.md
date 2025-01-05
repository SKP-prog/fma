# Python Selenium HLJ Crawler

## Description
Following Comamnds on how to run Crawler
```commandline
# Run Default Crawler
python manage.py crawl

# Run Crawler in Dev Mode
python manage.py crawl --dev 1
```

### Dev Mode
There are three levels for dev mode.
- 0 = Run in production mode.
- 1 = Run the crawling process of the script.
- 2 = run Dev mode for processing dataframe (Note that you need to have the pickle file for this. Pickle file can be generated using mode 1 or 2.)