from django.db import models

class Airline(models.Model):
    airlineCode = models.CharField(max_length=3, unique=True, verbose_name='航空公司代碼')
    airlineName = models.CharField(max_length=100, verbose_name='航空公司名稱')
    country = models.CharField(max_length=50, verbose_name='國家')
    hubAirport = models.CharField(max_length=50, verbose_name='主要樞紐機場')
    alliance = models.CharField(max_length=30, null=True, blank=True, verbose_name='聯盟')
    foundedYear = models.IntegerField(null=True, blank=True, verbose_name='成立年份')
    website = models.URLField(null=True, blank=True, verbose_name='官網')
    logo = models.ImageField(upload_to='airlines/', null=True, blank=True, verbose_name='公司標誌')

    class Meta:
        verbose_name = '航空公司資訊'
        verbose_name_plural = '航空公司資訊'
        ordering = ['airlineCode']
        db_table = 'airline_info'

    def __str__(self):
        return f"{self.airlineCode} - {self.airlineName}"
