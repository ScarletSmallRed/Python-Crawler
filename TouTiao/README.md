# Tou Tiao
Use python crawler to crawl the street photography (街拍) post on [Tou Tiao](https://www.toutiao.com/search/?keyword=%E8%A1%97%E6%8B%8D) website and save those relevant pictures.
Relevant code [here](./Spider.py).
## Main Python Libraries
1. Network request library: [requests](https://github.com/psf/requests)
2. Json format conversion library: json
3. Pattern matching: re, [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
4. Database connection library: [PyMongo](https://api.mongodb.com/python/current/)
## Work Process
1. Use Chrome's developer debugging tool to get ajax requests, and then extract the data related to the search results in the requests.
2. Parse the results returned in the above steps to get the url link for each specific page.
3. According to the specific url, add appropriate request header information in the code to simulate browser access to get the html text of the specific page.
4. Use the relevant pattern matching library to get the required image addresses, and use these addresses to download and save the relevant images to the local [folder](./images).
