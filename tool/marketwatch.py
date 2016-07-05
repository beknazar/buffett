import requests

from django.conf import settings

from models import Stock
from yahoo import Yahoo
from project.common import Script


class MarketWatch(Script):
    homepage_url = 'http://www.marketwatch.com/investing/stock/{0}/financials/{1}'
    r_m = settings.AVG_MARKET_RETURN
    r_f = settings.RISK_FREE_RATE
    year_count = 5

    def __init__(self, *args, **kwargs):
        self.client = requests.Session()

    def update_wacc(self):
        qs = Stock.objects.all().order_by('ipo_date')
        all_count = qs.count()
        count = 0
        for stock in qs:
            if not stock.beta:
                self.warn('No beta: {0}'.format(stock.name))
                continue
            if stock.wacc:
                self.info('Wacc already found: {0}'.format(stock.name))
                continue
            wacc = self.get_wacc(stock)
            if wacc:
                stock.update(wacc=wacc)
                self.info('Processed {0}/{1}. Wacc: {2}'.format(count,
                          all_count, round(wacc, 2)))
            count += 1

    def get_wacc(self, stock):
        r_e = self.r_f + stock.beta * (self.r_m - self.r_f)
        lt_debt = self.get_info(stock.ticker, 'balance-sheet',
                                ['Long-Term Debt excl. Capitalized Leases',
                                 'LT Debt excl. Capitalized Leases',
                                 'LT Debt excl. Capital Lease Obligations'])
        if lt_debt is None:
            self.warn('Skipping {0}...'.format(stock.ticker))
            return None
        else:
            self.info('Good with {0}'.format(stock.ticker))

        st_debt = self.get_info(stock.ticker, 'balance-sheet',
                                ['Short Term Debt'])
        debt = lt_debt + st_debt
        interest_expense = self.get_info(stock.ticker, '',
                                         [' Interest Expense',
                                          ' Total Interest Expense',
                                          'Total Interest Expense',
                                          'Interest Expense',
                                          'Interest Expense, Net of Interest Capitalized'])
        r_d = 0
        if debt != 0:
            r_d = interest_expense / debt

        equity = stock.market_cap
        if equity < 1:
            equity = Yahoo().get_market_cap(stock)
            if equity:
                stock.update(market_cap=equity)
            else:
                return None

        value = equity + debt
        income_tax_3 = self.get_info(stock.ticker, '', ['Income Tax',
                                                        'Income Taxes'], 3)
        pretax_income_3 = self.get_info(stock.ticker, '', [' Pretax Income',
                                                           'Pretax Income'],
                                        3)
        t_c = sum(income_tax_3) / sum(pretax_income_3)
        wacc = (equity * r_e) / value + (debt * r_d * (1 - t_c)) / value
        return wacc

    def get_info(self, ticker, section, names, yrs=1):
        res = []

        start = self.year_count - yrs + 1
        end = self.year_count + 1

        url = self.homepage_url.format(ticker, section)
        tree = self.get_tree(url)
        for name in names:
            td = tree.xpath('//td[text()="{0}"]'.format(name))
            if td and len(td) == 1:
                break
        p = []
        if td and len(td) == 1:
            p = td[0].getparent()
        else:
            self.warn('Wrong: {0} - {1} - {2}'.format(ticker, section, name))
            return None
        for i in range(start, end):
            res.append(self.convert_money(p[i].text_content()))

        if yrs == 1:
            return res[0]
        return res
