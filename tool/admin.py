from django.contrib import admin

from models import Sector, Industry, Stock


class SectorAdmin(admin.ModelAdmin):
    list_display = ('value', 'title')


class IndustryAdmin(admin.ModelAdmin):
    list_display = ('value', 'title')


class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'exchange',
                    'sector', 'industry',
                    'market_cap', 'ltdebt_equity', 'beta',
                    'ipo_date', )

admin.site.register(Sector, SectorAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Stock, StockAdmin)
