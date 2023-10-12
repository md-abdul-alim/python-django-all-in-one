import scrapy
from luluscraper.items import ProductItem


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
        # Retrieve product wise details
        product_item = ProductItem()

        product_item['title'] = response.css('h1.product-name ::text').get()
        product_item['price'] = response.css('div.price-tag div span span span small::text').get() + ' ' + response.css('div.price-tag div span span span::text').get(),

        yield product_item

        # yield {
        #     'title': response.css('h1.product-name ::text').get(),
        #     'price': response.css('div.price-tag div span span span small::text').get() + ' ' + response.css('div.price-tag div span span span::text').get(),
        # }

