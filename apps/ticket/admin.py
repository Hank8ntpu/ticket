from django.contrib import admin
from .models import Ticket, Price, Airline
from django.utils.html import format_html
from django.urls import reverse

# 註冊 Ticket Model 到 Admin
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('flightCode', 'airline', 'depTime', 'arrTime', 'depCity', 'depAirport', 'depAirportCode', 'arrCity', 'arrAirport', 'arrAirportCode')
    list_filter = ('depCity',)  # 篩選器
    search_fields = ('flightCode', 'depCity', 'arrCity')  # 搜尋欄位
    ordering = ('depTime',)  # 預設排序

@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_flight_code',   # ← 來自被關聯表 Ticket.flightCode
        'ticket_airline',       # ← 來自被關聯表 Ticket.airline
        'depDate', 'arrDate', 'Class', 'aircraftType', 'price', 'recPrice', 'currency'
    )
    # 重要：避免 N+1
    list_select_related = ('ticket',)
    list_filter = ('ticket__airline', 'Class',)  # 篩選器
    search_fields = ('ticket__flightCode', 'ticket__airline')  # 搜尋欄位
    ordering = ('price',)  # 預設排序
    
    @admin.display(description='航班代碼', ordering='ticket__flightCode')
    def ticket_flight_code(self, obj):
        return obj.ticket.flightCode if obj.ticket_id else '-'

    @admin.display(description='航空公司', ordering='ticket__airline')
    def ticket_airline(self, obj):
        return obj.ticket.airline if obj.ticket_id else '-'

# 註冊 Ticket Model 到 Admin
@admin.register(Airline)
class AirlineAdmin(admin.ModelAdmin):
    list_display = ('airlineCode', 'airlineName', 'country', 'hubAirport', 'alliance', 'foundedYear', 'website', 'logo')
    search_fields = ('airlineCode', 'airlineName', 'country')  # 搜尋欄位
    ordering = ('airlineCode',)  # 預設排序