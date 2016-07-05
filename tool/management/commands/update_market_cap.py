import logging

from django.core.management.base import BaseCommand

from tool.yahoo import Yahoo
from tool.models import Stock

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update market_cap info of all stocks'

    def handle(self, *args, **options):
        qs = Stock.objects.all()

        tickers = []
        for stock in qs:
            tickers.append(stock.ticker)
            res = Yahoo().get_market_cap(tickers)

        if len(res) != qs.count():
            logger.error('Problem with lens')
            return 0

        all_count = qs.count()
        count = 0
        for stock in qs:
            stock.update(market_cap=res[count])
            count += 1
            self.info('Processed {0}/{1}'.format(count, all_count))
