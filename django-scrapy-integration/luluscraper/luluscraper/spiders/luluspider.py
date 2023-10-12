import scrapy
from threading import Thread
from luluscraper.items import ProductItem, DjangoScraperItem, Product


def save_product(title, price):
    try:
        Product.objects.create(
            title=title,
            price=price,
        )
    except Exception as e:
        raise e

class LuluspiderSpider(scrapy.Spider):
    name = "luluspider"
    allowed_domains = ["www.luluhypermarket.com"]
    start_urls = ["https://www.luluhypermarket.com/en-ae/electronics"]

    def parse(self, response):
        # Retrieve all electronics sub categories
        sub_categories = response.css('section.recommended-for-you div.col-lg-2')

        for sub_category in sub_categories:
            relative_url = sub_category.css('div.col-lg-2 a').attrib['href']
            sub_category_url = "https://www.luluhypermarket.com/en-ae" + relative_url

            yield response.follow(sub_category_url, callback=self.parse_product_page)

    def parse_product_page(self, response):
        # Retrieve category wise products urls
        products = response.css('div.product-img')

        for product in products:
            relative_url = product.css('a ::attr(href)').get()
            product_url = "https://www.luluhypermarket.com" + relative_url

            yield response.follow(product_url, callback=self.parse_product_details)

    def parse_product_details(self, response):
        ## Retrieve product wise details
        product_item = ProductItem()

        ## For unknown case using DjangoItem package Django model saving is not working.
        # product_item = DjangoScraperItem()

        title = response.css('h1.product-name ::text').get()
        price = response.css('div.price-tag div span span span small::text').get() + ' ' + response.css('div.price-tag div span span span::text').get()

        ## For now using thread for this error: django.core.exceptions.SynchronousOnlyOperation. Also, we can use async
        Thread(target=save_product, args=(title, price)).start()

        ## Used this to save scrapping data in database direct in django created product model using scrapy pipelines. Uncomment the scrapy settings item pipelines to make this work.
        # product_item['title'] = title
        # product_item['price'] = price
        # yield product_item

        ## This part was for testing purpose. Checking data scrapping is ok or not.
        # yield {
        #     'title': response.css('h1.product-name ::text').get(),
        #     'price': response.css('div.price-tag div span span span small::text').get() + ' ' + response.css('div.price-tag div span span span::text').get(),
        # }

