# -*- coding: utf-8 -*-
import scrapy
import re
from elasticsearch import Elasticsearch
from datetime import datetime


elastic_connexion = Elasticsearch("localhost:9200", TimeoutError=3000.0)

class ShooesySpider(scrapy.Spider):
    name = 'shooesy'
    allowed_domains = ['littlewoodsireland.ie']
    start_urls = ['http://www.littlewoodsireland.ie/sports-leisure/mens-sports-shoes/football-boots/e/b/2890.end']
    counter=1
    
    def parse(self,response):
        products = response.css('.product')
        item = dict()
        for p in products:
            brand = (p.css('.productTitle>h3>em::text').extract_first()).title()
            productname = (p.css('.productTitle>h3>span::text').extract_first()).title()
            price = (p.xpath(".//dd[@class='productPrice' or @class='productNowPrice']/text()").extract_first())
            price = re.findall(r'[\d,.]+', price)[0]
            item['brand'] = (brand)
            item['name'] = (productname)
            item['price'] = float(price)
            item['provider'] = ('littlewoodsireland.ie')
            item['timestamp'] = (str(datetime.now()).replace(' ','T')[:19])
            self.counter+=1
            yield item

            elastic_connexion.index(index='shoes',doc_type='product',id="%s-%s"%(self.counter,"LWI"),body=item)

        nextPageLinkSelector = response.css('.paginationNext::attr("href")')
        if nextPageLinkSelector:
            nextPageLink = "http://www.littlewoodsireland.ie" + nextPageLinkSelector.extract()[0]
            yield scrapy.Request(url=nextPageLink,callback= self.parse)