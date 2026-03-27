# Race-Finder
A race finder built with Python that uses LLMs to find and summarize upcoming races that match certain criteria I'm looking for.

## Problem statement: 

Finding a race in the area that matches multiple criteria is super annoying
You have to search across multiple sites to find the races that you would like to run,
figure out where they are, figure out practicalities like pricing, how you will get there,
how to train, etc.

What if you were able to give a generalized query to an LLM, combined with a webscraper, 
that could figure out many of these things for you?

Traditional web scrapers do quite well in terms of gathering and finding information.
In fact, you should be able to find much of the information that you need and be able to format
it by iterating through versions of web scrapers which parse online information for you.

However, traditional web scrapers have limitations:
1. Defining the breadth of websites to search on
    Sources of truth for racing change over time, and new websites
    from new clubs or race organizers crop up all the time. This list of
    new sites needs to be maintained as time goes on, and requires manual searching.
2. Adapting the tooling to various formats across different websites
    Traditional webscrapers are hard to adapt across generalized formats. For a
    specific website, it often makes sense to adapt the script to how that website is formatted.
    However, when you introduce a new source of truth to a web-scraper, it must adapt to whatever
    tooling you give
3. Queries on very specific information
    Webscrapers are often used to query for very specific, tabular data, which severely limits
    the scope of queries you can run on it.

## Proposal:

This tool is a mix of web-scraping and LLM API calls which classify a query, use a web-scraper to find
relevant information, and then pull that information. 

Sample questions:

In the DMV area, what are some races that I would find that would be interesting?
Limit it to just those which are duathlons, 5ks, 10ks, and half-marathons

I am gunning for a race in late June / early July. I am thinking of it being a duathlon, but 
would be open to running a half-marathon or 10k. Can you find some races close to DC that would be
good for a newcomer?
