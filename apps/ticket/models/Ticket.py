from django.db import models
from .Airline import Airline

class Ticket(models.Model):
    flightCode = models.CharField(max_length=10, unique=True, verbose_name='航班代碼')
    airline = models.CharField(max_length=50, verbose_name='航空公司')
    depTime = models.TimeField(verbose_name='出發時間')
    arrTime = models.TimeField(verbose_name='抵達時間')
    depCity = models.CharField(null=True, blank=True, max_length=50, verbose_name='出發城市')
    arrCity = models.CharField(null=True, blank=True, max_length=50, verbose_name='抵達城市')
    depAirport = models.CharField(max_length=50, verbose_name='出發機場')
    arrAirport = models.CharField(max_length=50, verbose_name='抵達機場')
    depAirportCode = models.CharField(null=True, blank=True, max_length=5, verbose_name='出發機場代號')
    arrAirportCode = models.CharField(null=True, blank=True, max_length=5, verbose_name='抵達機場代號')
    airlineinfo = models.ForeignKey(
        Airline,
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='航空公司資訊',
        null=True, blank=True
    )
    
    class Meta:
        verbose_name = '航班資訊'
        verbose_name_plural = '航班資訊'
        ordering = ['depTime']
        db_table = 'ticket_info'

    def __str__(self):
        return f"{self.flightCode} - {self.airline}"