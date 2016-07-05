from django.contrib import admin

from models import Sector, Industry, Stock


class SectorAdmin(admin.ModelAdmin):
    list_display = ('value', 'title')


class IndustryAdmin(admin.ModelAdmin):
    list_display = ('value', 'title')


class StockAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'name', 'exchange',
                    'sector', 'industry',
                    'market_cap', 'wacc', 'ltdebt_equity', 'beta',
                    'ipo_date', )

    list_filter = ('sector', 'industry', 'ipo_date', 'wacc')

admin.site.register(Sector, SectorAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Stock, StockAdmin)
