from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _

from project.common import TimestampedModel


class Sector(TimestampedModel):
    value = models.CharField(_('value'), max_length=60)
    title = models.CharField(_('title'), max_length=100)

    def __unicode__(self):
        return self.title


class Industry(TimestampedModel):
    value = models.CharField(_('value'), max_length=60)
    title = models.CharField(_('title'), max_length=100)

    def __unicode__(self):
        return self.title


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
    ipo_date = models.DateField(_('ipo date'), blank=True, null=True)

    market_cap = models.BigIntegerField(_('market cap'), default=0)
    ltdebt_equity = models.FloatField(_('long term debt to equity'),
                                      blank=True, null=True)
    net_debt = models.BigIntegerField(_('net debt'), default=0)
    dcf_value = models.FloatField(_('dcf value'), blank=True, null=True)

    beta = models.FloatField(_('beta'), blank=True, null=True)
    wacc = models.FloatField(_('weighted average cost of capital'),
                             blank=True, null=True)
