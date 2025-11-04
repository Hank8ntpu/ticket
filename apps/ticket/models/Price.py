from django.db import models
from .Ticket import Ticket 

class Price(models.Model):
    #使用ForeignKey建立一對多關聯
    # PROTECT 不允許刪掉仍有價格的航班（保留歷史價）
    ticket = models.ForeignKey( 
        Ticket, 
        on_delete=models.CASCADE, 
        related_name='prices', 
        verbose_name='航班資訊',
        null=True, blank=True         # 先允許為空，等搬完資料再鎖回來
    )
    depDate = models.DateField(verbose_name='出發日期')
    arrDate = models.DateField(verbose_name='抵達日期')
    Class = models.CharField(max_length=10, verbose_name='艙等')
    aircraftType = models.CharField(max_length=20, verbose_name='機型')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='當前票價')
    recPrice = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='推薦票價')
    currency = models.CharField(max_length=3, default='TWD', verbose_name='幣別')

    class Meta:
        verbose_name = '票價'
        verbose_name_plural = '票價'
        constraints = [
            models.UniqueConstraint(fields=['ticket', 'depDate', 'Class'],
                                    name='uniq_ticket_date_cabin'),
            models.CheckConstraint(check=models.Q(price__gte=0), name='price_non_negative'),
            models.CheckConstraint(check=models.Q(recPrice__gte=0), name='recprice_non_negative'),
        ]
        indexes = [
            models.Index(fields=['ticket', 'depDate']),
            models.Index(fields=['depDate']),
        ]

    def __str__(self):
        return f'{self.ticket.flightCode}    {self.depDate}     {self.price}'