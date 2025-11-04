# app/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max, F
from datetime import datetime

import json
from .models import Ticket, Price  # 調整成你的實際匯入路徑

def quote_search_page(request):
    """
    使用 GET 參數進行篩選，直接渲染結果清單。
    支援：關鍵字、IATA 機場代碼、城市、航空公司、艙等、出發日期、價格區間、排序、分頁。
    """
    params = request.GET

    # --- 讀取 GET 參數 ---
    q         = params.get('q', '').strip()
    dep_code  = params.get('dep_airport', '').strip().upper()
    arr_code  = params.get('arr_airport', '').strip().upper()
    dep_city  = params.get('dep_city', '').strip()
    arr_city  = params.get('arr_city', '').strip()
    airline   = params.get('airline', '').strip()
    cabin     = params.get('cabin', '').strip()
    dep_date  = params.get('dep_date', '').strip()
    min_p     = params.get('min_price', '').strip()
    max_p     = params.get('max_price', '').strip()
    order_by  = params.get('order_by', 'depDate').strip()  # 預設依出發日
    page      = params.get('page', '1').strip()
    recommend_only = params.get('recommend_only', '').strip()


    # --- 白名單排序，避免惡意欄位 ---
    ORDERABLE = {
        'depDate': 'depDate', '-depDate': '-depDate',
        'price': 'price', '-price': '-price',
        'recPrice': 'recPrice', '-recPrice': '-recPrice',
    }
    order_expr = ORDERABLE.get(order_by, 'depDate')

    # --- 基礎 QuerySet（帶外鍵）---
    qs = (
        Price.objects
        .select_related('ticket')
        .all()
    )

    # --- 精準篩選（IATA 代碼）---
    if dep_code:
        qs = qs.filter(ticket__depAirportCode__iexact=dep_code)
    if arr_code:
        qs = qs.filter(ticket__arrAirportCode__iexact=arr_code)

    # --- 城市模糊 ---
    if dep_city:
        qs = qs.filter(ticket__depCity__icontains=dep_city)
    if arr_city:
        qs = qs.filter(ticket__arrCity__icontains=arr_city)

    # --- 航空公司、艙等 ---
    if airline:
        qs = qs.filter(ticket__airline__icontains=airline)
    if cabin:
        qs = qs.filter(Class__iexact=cabin)

    # --- 出發日期（格式錯就忽略）---
    if dep_date:
        try:
            d = datetime.strptime(dep_date, '%Y-%m-%d').date() #
            qs = qs.filter(depDate=d)
        except ValueError:
            pass

    # --- 價格區間 ---
    if min_p.isdigit():
        qs = qs.filter(price__gte=int(min_p)) #
    if max_p.isdigit():
        qs = qs.filter(price__lte=int(max_p))

    # 只顯示「當前價 < 建議價」的推薦清單
    if recommend_only in ('1', 'true', 'on', 'yes'):
        qs = qs.filter(price__lt=F('recPrice')) #

    # --- 關鍵字（航班代碼 / 城市 / 機場名稱）---
    if q:
        qs = qs.filter(
            Q(ticket__flightCode__icontains=q) |
            Q(ticket__depCity__icontains=q)   |
            Q(ticket__arrCity__icontains=q)   |
            Q(ticket__depAirport__icontains=q)|
            Q(ticket__arrAirport__icontains=q)
        )

    # --- 排序 ---
    qs = qs.order_by(order_expr)

    # --- 分頁 ---
    paginator = Paginator(qs, 20)  # 每頁 20 筆
    page_obj = paginator.get_page(page)

    # --- 下拉選單資料：來自資料庫現有值（distinct）---
    dep_airport_choices = (
        Ticket.objects.exclude(depAirportCode__isnull=True).exclude(depAirportCode__exact='')
        .values_list('depAirportCode', flat=True).distinct().order_by('depAirportCode')
    )
    arr_airport_choices = (
        Ticket.objects.exclude(arrAirportCode__isnull=True).exclude(arrAirportCode__exact='')
        .values_list('arrAirportCode', flat=True).distinct().order_by('arrAirportCode')
    )
    dep_city_choices = (
        Ticket.objects.exclude(depCity__isnull=True).exclude(depCity__exact='')
        .values_list('depCity', flat=True).distinct().order_by('depCity')
    )
    arr_city_choices = (
        Ticket.objects.exclude(arrCity__isnull=True).exclude(arrCity__exact='')
        .values_list('arrCity', flat=True).distinct().order_by('arrCity')
    )
    airline_choices = (
        Ticket.objects.exclude(airline__isnull=True).exclude(airline__exact='')
        .values_list('airline', flat=True).distinct().order_by('airline')
    )
    cabin_choices = (
        Price.objects.exclude(Class__isnull=True).exclude(Class__exact='')
        .values_list('Class', flat=True).distinct().order_by('Class')
    )
    date_choices = (
        Price.objects.values_list('depDate', flat=True).distinct().order_by('depDate')
    )

    # --- 價格建議區間（顯示在 UI）---
    agg = Price.objects.aggregate(min_price=Min('price'), max_price=Max('price'))

    context = {
        'page_obj': page_obj,
        'total_count': paginator.count,
        'current': {  # 回填目前查詢值，模板可直接拿來 selected/value
            'q': q, 'dep_airport': dep_code, 'arr_airport': arr_code,
            'dep_city': dep_city, 'arr_city': arr_city,
            'airline': airline, 'cabin': cabin, 'dep_date': dep_date,
            'min_price': min_p, 'max_price': max_p, 'order_by': order_by,
            'recommend_only': recommend_only,
        },
        'dep_airport_choices': dep_airport_choices,
        'arr_airport_choices': arr_airport_choices,
        'dep_city_choices': dep_city_choices,
        'arr_city_choices': arr_city_choices,
        'airline_choices': airline_choices,
        'cabin_choices': cabin_choices,
        'date_choices': date_choices,
        'price_min_suggest': agg['min_price'] or 0,
        'price_max_suggest': agg['max_price'] or 0,
        'order_whitelist': ORDERABLE.keys(),
    }
    return render(request, "ticket/quote_search.html", context)


# @require_http_methods(["POST"])
# def quote_calc_api(request):
#     # 讀 JSON
#     try:
#         data = json.loads(request.body.decode("utf-8"))
#     except Exception:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     required = ["dep_date", "arr_date", "cabin", "dep_city", "dep_airport", "arr_city", "arr_airport"]
#     missing = [k for k in required if not data.get(k)]
#     if missing:
#         return JsonResponse({"error": f"缺少欄位: {', '.join(missing)}"}, status=400)

#     # 解析日期
#     try:
#         dep_date = datetime.strptime(data["dep_date"], "%Y-%m-%d").date()
#         arr_date = datetime.strptime(data["arr_date"], "%Y-%m-%d").date()
#     except ValueError:
#         return JsonResponse({"error": "日期格式需為 YYYY-MM-DD"}, status=400)

#     if arr_date < dep_date:
#         return JsonResponse({"error": "抵達日期不可早於出發日期"}, status=400)

#     # 清理文字輸入
#     cabin = data["cabin"].strip()
#     dep_city = data["dep_city"].strip()
#     arr_city = data["arr_city"].strip()
#     dep_airport_code = (data["dep_airport"] or "").upper().strip()  # 建議用 IATA
#     arr_airport_code = (data["arr_airport"] or "").upper().strip()

#     # ---- 1) 先從 Ticket 依條件縮小範圍 ----
#     ticket_q = Ticket.objects.all()

#     # 優先用 IATA 代碼（你的 Ticket 有 depAirportCode / arrAirportCode）
#     code_filter = Q()
#     if dep_airport_code:
#         code_filter &= Q(depAirportCode__iexact=dep_airport_code)
#     if arr_airport_code:
#         code_filter &= Q(arrAirportCode__iexact=arr_airport_code)

#     # 若沒代碼或無匹配，再用城市/機場名稱輔助
#     # 這裡先不下去「或」查，避免把範圍拉太大；找不到時再做第二輪放寬。
#     ticket_q1 = ticket_q.filter(code_filter) if code_filter else ticket_q.none()

#     if not ticket_q1.exists():
#         # 放寬條件：用城市/機場名稱模糊（避免全表）
#         name_filter = Q()
#         if dep_city:
#             name_filter &= Q(depCity__icontains=dep_city)
#         if arr_city:
#             name_filter &= Q(arrCity__icontains=arr_city)
#         # 也可輔助用機場中文名稱關鍵字
#         if dep_airport_code and len(dep_airport_code) > 3:
#             name_filter &= Q(depAirport__icontains=dep_airport_code)
#         if arr_airport_code and len(arr_airport_code) > 3:
#             name_filter &= Q(arrAirport__icontains=arr_airport_code)

#         ticket_q1 = ticket_q.filter(name_filter)

#     if not ticket_q1.exists():
#         return JsonResponse({"error": "找不到符合航段的航班（請檢查城市/機場代碼）"}, status=404)

#     # ---- 2) 在 Price 表挑指定日期＋艙等 的報價（唯一性：ticket+depDate+Class）----
#     # cabin 可能是「經濟艙 / 商務艙 …」；用 iexact 避免大小寫/全半形困擾
#     price_q = (
#         Price.objects
#         .filter(
#             ticket__in=ticket_q1,
#             depDate=dep_date,
#             Class__iexact=cabin  # 與你的模型欄位對齊
#         )
#         .select_related("ticket")
#         .order_by("price")  # 由便宜到貴
#     )

#     if not price_q.exists():
#         return JsonResponse({"error": "此日期/艙等沒有價格資料"}, status=404)

#     # 規則：取「當前價最低」的那一筆作為代表
#     best = price_q.first()

#     current_price = float(best.price)       # Decimal -> float/str 皆可
#     recommended_price = float(best.recPrice)

#     is_good_to_book = recommended_price > current_price
#     advice = "當前價格較優惠，推薦立即下訂該航段機票。" if is_good_to_book else "當前價格較高，可以再等等。"

#     # 回傳更多上下文（航班資訊）
#     t = best.ticket
#     return JsonResponse({
#         "dep_date": str(best.depDate),
#         "arr_date": str(best.arrDate),
#         "cabin": best.Class,
#         "dep_city": t.depCity,
#         "arr_city": t.arrCity,
#         "dep_airport": t.depAirportCode or t.depAirport,
#         "arr_airport": t.arrAirportCode or t.arrAirport,
#         "flight_code": t.flightCode,
#         "airline": t.airline,
#         "current_price": current_price,
#         "recommended_price": recommended_price,
#         "is_good_to_book": is_good_to_book,
#         "advice": advice,
#     })