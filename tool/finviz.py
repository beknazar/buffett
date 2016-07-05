import requests
from datetime import datetime

from models import Sector, Industry, Stock
from project.common import Script


class Finviz(Script):
    homepage_url = 'http://finviz.com/{0}'
    attr_map = ['ticker', 'name', 'sector', 'industry', 'market_cap',
                'ltdebt_equity', 'beta', 'ipo_date', ]
    results_count = 20

    def __init__(self, *args, **kwargs):
        # Initiate a new session
        self.client = requests.Session()

    def crawl(self, criteria, exchange):
        start = criteria.find('&c=')
        cols_count = len(criteria[start+3:].split(','))

        entries = []
        page = 0
        page_count = 1
        tree = self.get_tree(self.homepage_url.format(criteria))

        page_nums = tree.xpath('//a[@class="screener-pages"]/text()')
        if len(page_nums) > 0:
            page_count = int(page_nums[-1])
        while True:
            page += 1
            self.info('Crawling page: {0}/{1}'.format(page, page_count))

            tickers = tree.xpath('//a[@class="screener-link-primary"]/text()')
            attrs = tree.xpath('//td[@class="screener-body-table-nw"]//text()')
            index = 0
            for i in range(len(tickers)):
                entry = {}
                for j in range(cols_count):
                    key = self.attr_map[j]
                    entry[key] = self.convert(key, attrs[i * cols_count + j])
                entry['exchange'] = exchange
                entries.append(Stock(**entry))
            next_el = tree.xpath('//a[contains(., "next")]')
            if len(next_el) > 0:
                criteria = next_el[0].attrib['href']
                tree = self.get_tree(self.homepage_url.format(criteria))
            else:
                break
        # Create stocks in bulk
        Stock.objects.bulk_create(entries)

    def convert(self, kind, st):
        res = None
        if kind in ['ticker', 'name']:
            res = st
        elif kind == 'sector':
            res = Sector.objects.get(title=st)
        elif kind == 'industry':
            res = Industry.objects.get(title=st)
        elif kind == 'market_cap' and st != '-':
            res = self.convert_money(st)
        elif kind in ['ltdebt_equity', 'beta'] and st != '-':
            res = float(st)
        elif kind == 'ipo_date' and st != '-':
            res = datetime.strptime(st, '%m/%d/%Y')
        return res
