import scrapy
from ..items import AmazonProjectItem
import re

class AmazonSpiderSpider(scrapy.Spider):
    name = "amazon_spider"
    
    allowed_domains = ["amazon.com"]
    category = "headphones"
    start_urls = [f"https://www.amazon.com/s?k={category.replace(' ', '+')}"]

    def extract_brand(self, product_names, product_brandnames, product_links):
        product_brands = []
        products_to_scrape = []  # To store products with unknown brands
        
        for i, name in enumerate(product_names):
            if not name:
                product_brands.append("Unknown")
                continue
            
            words = name.split()
            words_lower = [word.lower() for word in words] 
            found_brand = "Unknown"
            
            for brand in product_brandnames:
                if brand.lower() in words_lower:
                    found_brand = brand
                    break
            
            product_brands.append(found_brand)
            
            # If brand is still unknown, store the link for further scraping
            if found_brand == "Unknown" and i < len(product_links):
                products_to_scrape.append((i, product_links[i]))
        
        return product_brands, products_to_scrape  # Return brands + products needing extra scraping
    
    def parse_price(self, response):
        prices = response.css('.s-main-slot .s-result-item span.a-price[data-a-color="base"] span.a-offscreen::text').getall()
        return [price.strip().replace("$", "") for price in prices]




    def parse_productlink(self, response):
        raw_links = response.css("a.a-link-normal.s-no-outline::attr(href)").getall()

        cleaned_links = []
        
        for link in raw_links:
            match = re.search(r'url=(%2F[^&]*)', link)
            if match:
                cleaned_link = match.group(1).replace('%2F', '/')  # Decode URL
                full_link = response.urljoin(cleaned_link)
                cleaned_links.append(full_link)
            else:
                cleaned_links.append(response.urljoin(link))  # Use the original if no match

        return cleaned_links

    def parse(self, response):
        items = AmazonProjectItem()

        product_name = response.css('.a-color-base.a-text-normal span::text').getall()
        product_price = self.parse_price(response)

        product_imagelink = response.css('.s-image::attr(src)').getall()
        product_brandnames = response.css('#p_123-title+ .a-spacing-medium .a-color-base::text').getall()
        product_links = self.parse_productlink(response)

        # Extract brands and get products that need further scraping
        product_brands, products_to_scrape = self.extract_brand(product_name, product_brandnames, product_links)

        print(f"Total Products Found: {len(product_name)}")
        print(f"Total Product Links Found: {len(product_links)}")
        print(f"Total Known Brands: {len(product_brands)}")
        print(f"Products Needing Extra Scraping: {len(products_to_scrape)}")
        print(f'price:{len(product_price)}')

        items['product_name'] = product_name
        items['product_brand'] = product_brands
        items['product_price'] = product_price
        items['product_imagelink'] = product_imagelink
        items['product_link'] = product_links
        
        yield items

        # Follow product links for unknown brands
        #for index, link in products_to_scrape:
            #yield response.follow(link, self.parse_product_page, meta={'index': index, 'items': items})

        # Handle pagination
        #next_page = response.css('.s-pagination-next::attr(href)').get()
        #if next_page:
         #   next_page_url = response.urljoin(next_page)
          #  self.logger.info(f"Scraping Next Page: {next_page_url}")
           # yield scrapy.Request(next_page_url, callback=self.parse)

   # def parse_product_page(self, response):
    #    """Extract brand name from the product page if missing"""
     #   items = response.meta['items']
      #  index = response.meta['index']

        # Extract brand from product page
       # product_brand = response.css('.po-brand .po-break-word::text').get()
        
        # Update the brand in the items list
        #if product_brand:
         #   items['product_brand'][index] = product_brand.strip()

       # yield items  # Yield updated item with extracted brand
