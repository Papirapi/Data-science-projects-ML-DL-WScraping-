# -*- coding: utf-8 -*-
import scrapy
import re
from elasticsearch import Elasticsearch
from datetime import datetime


elastic_connexion = Elasticsearch("localhost:9200", TimeoutError=3000.0)

class ShoesySpider(scrapy.Spider):
    name = 'shoesy'
    allowed_domains = ['fr.sportsdirect.com']
    start_urls = ['https://fr.sportsdirect.com/football/football-boots/mens-football-boots/']
    counter=1

    def parse(self,response):
        products = response.css('.s-productthumbbox')
        item = dict()
        for p in products:
            brand=( p.css('.productdescriptionbrand::text').extract_first()).title()
            productname=(p.css('.productdescriptionname::text').extract_first()).title()
            price=( p.css('.curprice::text').extract_first())
            price = (re.findall(r'[\d,.]+', price)[0]).replace(",",".")
            item['brand'] = (brand)
            item['name'] = (productname)
            item['price'] = float(price)
            item['provider'] = ('sportdirect')
            item['timestamp'] = (str(datetime.now()).replace(' ','T')[:19])
            self.counter+=1
            yield item        
            
            elastic_connexion.index(index='shoes',doc_type='product',id="%s-%s"%(self.counter,"SD"),body=item)

        nextPageLinkSelector = response.css('.NextLink::attr("href")')
        if nextPageLinkSelector:
            nextPageLink = nextPageLinkSelector.extract()[0]
            yield scrapy.Request(url=nextPageLink,callback= self.parse)