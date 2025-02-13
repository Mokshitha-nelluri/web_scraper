import scrapy
from ..items import AmazonProjectItem

class AmazonSpiderSpider(scrapy.Spider):
    name = "amazon_spider"
    
    allowed_domains = ["amazon.com"]
    category = "over+ear+headphones"
    start_urls = [f"https://www.amazon.com/s?k={category.replace(' ', '+')}"]


    def extract_brand(self, product_names, product_brandnames, product_links):
        product_brands = []
        products_to_scrape = []  # To store products with unknown brands
        
        for i, name in enumerate(product_names):
            if not name:
                product_brands.append("Unknown")
                continue
            
            name_str = " ".join(name)  # Convert list to string
            words = name_str.split()   # Now safe to split
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
        
        return product_brands, products_to_scrape


    def parse(self, response):
        items = AmazonProjectItem()
        
        product_containers = response.css('.puisg-row')
        product_names = []
        product_prices = []
        product_imagelinks = []
        product_links = []
        product_brand = []
        
        for product in product_containers:
            product_name = product.css('.a-color-base.a-text-normal span::text').extract()
            price = product.css(".a-price[data-a-color='base'] .a-offscreen::text").get()
            imagelink = product.css(".s-image::attr(src)").get()
            link = product.css("a.a-link-normal.s-no-outline::attr(href)").get()

            if product_name and price and link:  # Ensuring all three exist to avoid ads/promoted items
                product_names.append(product_name)
                product_prices.append(price)
                product_imagelinks.append(imagelink)
                product_links.append(response.urljoin(link))
        
        # Extract brands and get products that need further scraping
        product_brandnames = response.css('#p_123-title+ .a-spacing-medium .a-color-base::text').getall()
        product_brand, products_to_scrape = self.extract_brand(product_names, product_brandnames, product_links)
        
        items["product_name"] = product_names
        items["product_price"] = product_prices
        items["product_imagelink"] = product_imagelinks
        items["product_link"] = product_links
        items["product_brand"]= product_brand
        
        print(f"Products Scraped: {len(product_names)}")
        print(f"Prices Scraped: {len(product_prices)}")
        print(f"Links Scraped: {len(product_links)}")
        print(f"brands: {len(product_brand)}")

     

    # Handle pagination
        next_page = response.css('.s-pagination-next::attr(href)').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            self.logger.info(f"Scraping Next Page: {next_page_url}")
            yield scrapy.Request(next_page_url, callback=self.parse)

        yield items