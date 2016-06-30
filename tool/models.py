from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from project.common import TimestampedModel


class Sector(TimestampedModel):
    title = models.CharField(_('title'), max_length=30)


class Industry(TimestampedModel):
    title = models.CharField(_('title'), max_length=30)


class Stock(TimestampedModel):
    XNYS = 'xnys'
    XNAS = 'xnas'
    EXCHANGES = (
        (XNYS, 'xnys'),
        (XNAS, 'xnas'),
    )
    ticker = models.CharField(_('ticker'), max_length=10)
    name = models.CharField(_('company name'), max_length=80)
    exchange = models.CharField(choices=EXCHANGES, max_length=10)

    sector = models.ForeignKey(Sector, blank=True, null=True,
                               related_name='stocks')
    industry = models.ForeignKey(Industry, blank=True, null=True,
                                 related_name='stocks')

    market_cap = models.BigIntegerField(_('market cap'), default=0)
