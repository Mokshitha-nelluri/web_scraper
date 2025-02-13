# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AmazonProjectItem(scrapy.Item):
    product_name = scrapy.Field()
    product_brand = scrapy.Field()  # ✅ Add this line
    product_price = scrapy.Field()
    product_imagelink = scrapy.Field()
    product_link = scrapy.Field()
    pass