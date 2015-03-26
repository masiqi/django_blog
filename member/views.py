from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import cgxn.djangoxn as xiaonei
from share.models import Stock, Holder
from order.models import StockQueue, UserAccount
from tools import *

@xiaonei.require_login()
def index(request, template_name="member/show.html"):
    userid = request.xiaonei.uid
    return _user_stock_info(request, userid, template_name)
    
@xiaonei.require_login()
def show(request, userid, template_name="member/show.html"):
    return _user_stock_info(request, userid, template_name)
    
def _user_stock_info(request, userid, template_name):
    my_stocks = []
    holds = Holder.objects.filter(user = userid)
    ua = UserAccount(userid)
    sq = StockQueue()
    holds_queue = ua.getStocks()
    for key in holds_queue:
        stock_info = sq.getStockInfo(key)
        stock = Stock.objects.get(pk=key)
        price = stock_info['price'] if stock_info['price'] != None else  stock_info['prev_close']
        my_stock_detail = {
                        'id' : key,
                        'symbol' : stock.symbol,
                        'name' :  stock.name,
                        'market_value' : (stock.tradable + stock.nontradable) * price,
                        'price' : price,
                        'hold' : holds_queue[key]['a'],
                        'trend' : calcTrend(price, stock_info['prev_close']),
                        }
        my_stocks.append(my_stock_detail)
                
    for hold in holds:
        stock_info = sq.getStockInfo(hold.stock_id)
        price = stock_info['price'] if stock_info['price'] != None else  stock_info['prev_close']
        my_stock_detail = {
                        'id' : hold.stock_id,
                        'symbol' : hold.stock.symbol,
                        'name' :  hold.stock.name,
                        'market_value' : (hold.stock.tradable + hold.stock.nontradable) * price,
                        'price' : price,
                        'hold' : holds_queue[hold.stock_id]['a'] + hold.amount,
                        'trend' : calcTrend(price, stock_info['prev_close']),
                        }
        my_stocks.append(my_stock_detail)
    return render_to_response(template_name, {
                                              "stocks" : my_stocks,
    }, context_instance=RequestContext(request))