EBooks
======


#it-ebooks.info spider

Parse a single ebook item
```bash
scrapy parse --spider=it-ebooks.info-incremental -c parse -d 1 -v http://it-ebooks.info/book/345/
```

Scrape all ebooks data into csv file
```bash
scrapy crawl it-ebooks.info-incremental -o it-ebooks.info.csv -t csv
```