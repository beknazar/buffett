import requests

from project.common import Script


class Yahoo(Script):
    homepage_url = 'http://download.finance.yahoo.com/d/quotes.csv?s={0}&f={1}'

    def __init__(self, *args, **kwargs):
        self.client = requests.Session()

    def get_market_cap(self, stock):
        r = self.request('get', self.homepage_url.format(stock.ticker, 'j1'))
        return self.convert_money(r.content[:-1])

    def get_net_debt(self, stock):
        cash = self.get_info(stock.ticker, 'bs', 'Cash And Cash Equivalents')
        return cash

    def get_info(self, ticker, section, name, yrs=1, is_annual=False):
        res = []

        annual = is_annual and 'annual' or ''

        url = 'https://finance.yahoo.com/q/{0}?s={1}&{2}'.format(section,
                                                                 ticker,
                                                                 annual)
        tree = self.get_tree(url)
        el = tree.xpath('//td[text()="{0}"]'.format(name))
        if el and len(el) == 1:
            p = el[0].getparent()
        else:
            self.warn('Wrong: {0} - {1} - {2}'.format(ticker, section, name))
            return None
        for el in p[1:yrs+1]:
            st = el.text_content().replace(u'\xa0', u'')
            res.append(self.convert_money(st))

        if yrs == 1:
            return res[0]

        return res
