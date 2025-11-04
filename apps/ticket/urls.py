from django.urls import path
from . import views

app_name = 'ticket'

urlpatterns = [
    path('quote/', views.quote_search_page, name='quote_search'),      # ✅ 以 GET 篩選的頁面
    # path('quote/calc/', views.quote_calc_api, name='quote_calc'), # JSON 計算 API
]