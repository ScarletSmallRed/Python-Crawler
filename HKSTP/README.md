# HKSTP
Use the python crawler framework [pyspider](http://docs.pyspider.org/en/latest/) to crawl this website, [HKSTP](https://www.hkstp.org/en/reach-us/company-directory/), to get company information in the Hong Kong Science Park.
## Work Process
1. Start `pyspider` using the command line `pyspider`.
2. on_start: get the main page information.
3. index_page: get each page.
4. detail_page: get specific information about each company in the specific page link.