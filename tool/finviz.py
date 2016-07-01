from lxml import html
import requests
from datetime import datetime

from models import Sector, Industry, Stock
from project.common import LogMixin


class Finviz(LogMixin):
    homepage_url = 'http://finviz.com/{0}'
    default_header = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/48.0.2564.116 Safari/537.36'
    }
    attr_map = ['ticker', 'name', 'sector', 'industry', 'market_cap',
                'ltdebt_equity', 'beta', 'ipo_date', ]
    results_count = 20

    def crawl(self, criteria, exchange):
        start = criteria.find('&c=')
        cols_count = len(criteria[start+3:].split(','))

        # Initiate a new session
        self.client = requests.Session()

        entries = []
        page = 0
        page_count = 1
        r = self.request('get', self.homepage_url.format(criteria))
        self.default_header = r.request.headers
        tree = html.fromstring(r.content)

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
            next_el = tree.xpath('//a[@class="tab-link"]/b')[0]
            if next_el.text_content() == 'next':
                criteria = next_el.getparent().attrib['href']
                r = self.request('get', self.homepage_url.format(criteria))
                tree = html.fromstring(r.content)
            else:
                break
        # Create stocks in bulk
        Stock.objects.bulk_create(entries)

    def convert(self, kind, st):
        self.info('Kind: {0}, St: {1}'.format(kind, st))
        res = None
        if kind in ['ticker', 'name']:
            res = st
        elif kind == 'sector':
            try:
                res = Sector.objects.get(title=st)
            except Sector.DoesNotExist:
                self.warn('Sector.DoesNotExist: title: {0}'.format(st))
        elif kind == 'industry':
            try:
                res = Industry.objects.get(title=st)
            except Industry.DoesNotExist:
                self.warn('Industry.DoesNotExist: title: {0}'.format(st))
        elif kind == 'market_cap' and st != '-':
            mult = st[-1] == 'B' and 10**9 or 10**6
            res = float(st[:-1]) * mult
        elif kind in ['ltdebt_equity', 'beta'] and st != '-':
            res = float(st)
        elif kind == 'ipo_date' and st != '-':
            res = datetime.strptime(st, '%m/%d/%Y')
        return res

    def request(self, method, url, data=None, stream=False):
        r = None
        try:
            if method == 'post':
                r = self.client.post(url, data=data,
                                     headers=self.default_header)
            else:
                r = self.client.get(url, headers=self.default_header,
                                    stream=stream)
        except requests.exceptions.ConnectionError as e:
            self.warn('Error inside request: {0}'.format(e))
        return r
