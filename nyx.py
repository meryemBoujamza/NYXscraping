import scrapy
import urllib.parse
from PIL import ImageColor


def clean_hex_code(code_hex):
    code_hex = code_hex.replace('background-color:', '')
    code_hex = code_hex.replace(';', '')
    return code_hex

class NyxSpider(scrapy.Spider):
    name = 'nyx'
    allowed_domains = ['www.nyxcosmetics.com']
    start_urls = ['https://www.nyxcosmetics.com/face/foundation']

    def parse(self, response):
        products = response.xpath('//h2[@class="c-product-tile__name"]')
        for prod in products:
            prod_rel_link = prod.xpath('.//a/@href').get()
            prod_link = urllib.parse.urljoin(
                'https://www.nyxcosmetics.com', prod_rel_link[1:])
            yield response.follow(url=prod_link, callback=self.parse_prod)

    def parse_prod(self, response):
        shades = response.xpath('//a[@class="c-swatch  m-large"]')
        for shade in shades:
            shade_link = shade.xpath('.//@href').get()
            yield response.follow(url=shade_link, callback=self.parse_final)

    def parse_final(self, response):
        prod_name = response.xpath(
            '//h1[@class="c-product-main__name"]/text()').get()
        prod_shade = response.xpath(
             '//div[@class="c-swatches-grouped__group"]/a[contains(@class,"c-swatch") and contains(@class,"m-selected")]/@data-js-value').get()
        prod_hex = response.xpath(
            '//div[@class="c-swatches-grouped__group"]/a[contains(@class,"c-swatch") and contains(@class,"m-selected")]/@style').get()
        prod_hex = clean_hex_code(prod_hex)
        r, g, b = ImageColor.getcolor(prod_hex, 'RGB')
        prod_price = response.xpath(
            '(//span[@class="c-product-price__value"])[1]/text()').get()
        prod_img = response.xpath(
            '//div[@class="c-carousel__item "]/img/@src').get()
        yield {
            "brand": "NYX",
            "name":  prod_name,
            "range": "foundation",
            "shade": prod_shade,
            "r": r,
            "g": g,
            "b": b,
            "price": prod_price,
            "img": prod_img
        }
