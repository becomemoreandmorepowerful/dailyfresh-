from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import View
from django_redis import get_redis_connection

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

from goods.models import GoodsSKU
from order.models import OrderGoods


class IndexView(View):
    '''显示首页'''
    def get(self,request):
        # 尝试获取缓存
        context = cache.get('index_page_data')
        if context is None:
            print('33333')
            # 获取商品种类信息
            types = GoodsType.objects.all()

            # 获取轮播商品的信息
            goods_banners = IndexGoodsBanner.objects.all().order_by('index')

            # 获取促销活动的信息
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            # 获取商品分类的展示信息
            # type_goods_banners = IndexTypeGoodsBanner.objects.all()
            for type in types:
                # 获取到type种类首页分类的图片的展示信息
                image_banner = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1).order_by('index')
                # 获取到type种类首页分类的图片的文字信息
                title_banner = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0).order_by('index')
                # 给type 动态的添加属性
                type.image_banners = image_banner
                type.title_banners = title_banner

            # 对于不会变化的数据设置缓存
            context = {'types': types,
                       'goods_banners': goods_banners,
                       'promotion_banners': promotion_banners,}
            # 设置缓存
            # key  value timeout
            cache.set('index_page_data', context, 3600)
        # 获取首页购物车的商品的数目
        # 只有在用户登陆的情况下才能获取到用户的购物车的商品书目
        user = request.user
        # print('缓存中获取数据')
        cart_count = 0
        # 如果用户已经登陆
        if user.is_authenticated():
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' %user.id
            cart_count = conn.hlen(cart_key)
        else:
            cart_count = 0
        context.update(cart_count=cart_count)
        # 返回应答
        return render(request,'index.html',context)


# /goods/商品id
class DetailView(View):
    '''详情页'''
    def get(self, request, goods_id):
        '''显示详情页'''
        try:
            sku = GoodsSKU.objects.get(id=goods_id)
        except GoodsSKU.DoesNotExist:
            # 商品不存在
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取商品的评论信息
        sku_orders = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]

        # 获取同一个SPU的其他规格商品
        # same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)
        same_spu_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=goods_id)
        # 获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        if user.is_authenticated():
            # 用户已登录
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' % user.id
            cart_count = conn.hlen(cart_key)

            # 添加用户的历史记录
            conn = get_redis_connection('default')
            history_key = 'history_%d' %user.id
            # 移除列表中的goods_id
            conn.lrem(history_key, 0, goods_id)
            # 把goods_id插入到列表的左侧
            conn.lpush(history_key, goods_id)
            # 只保存用户最新浏览的5条信息
            conn.ltrim(history_key, 0, 4)

        # 组织模板上下文
        context = {'sku':sku, 'types':types,
                   'sku_orders':sku_orders,
                   'new_skus':new_skus,
                   'same_spu_skus':same_spu_skus,
                   'cart_count':cart_count}

        # 使用模板
        return render(request, 'detail.html', context)


class ListView(View):
    '''列表页'''
    def get(self,request, type_id, page):
        # 获取种类信息
        try:

            type = GoodsType.objects.get(id=type_id)

        except Exception as res:
            return redirect(reverse('goods:index'))

        # 获取商品的分类信息
        types = GoodsType.objects.all()

        # 获取新品信息
        new_skus = GoodsSKU.objects.filter(type=type).order_by('-create_time')[:2]

        # 获取浏览器地址栏sort
        sort = request.GET.get('sort')
        if sort == 'hot':
            skus = GoodsSKU.objects.filter(type=type).order_by('sales')
        elif sort == 'price':
            skus = GoodsSKU.objects.filter(type=type).order_by('price')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=type).order_by('id')

        # 对商品进行分页显示
        paginator = Paginator(skus, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        num_pages = paginator.num_pages
        # 对总页数和当前页进行判断
        # 如果总页数小于5,显示所有页数
        if num_pages<5:
            pages = range(1,num_pages+1)

        # 如果当前页小于等于3,则显示前五页
        elif int(page)<=3:
            pages = range(1,6)

        # 如果总页数减去当前页小于等于2,则显示后五页
        elif num_pages-int(page) <= 2:
            pages = range(num_pages-4,num_pages+1)

        else:
            pages = range(page-2,page+3)
        # 获取第page页的Page实例对象
        skus_page = paginator.page(page)
        # 显示购物车的商品数目
        cart_count = 0
        user = request.user
        if user.is_authenticated():
            conn = get_redis_connection('default')
            cart_key = 'cart_%d' %user.id
            cart_count = conn.hlen(cart_key)

        # 组织模板上下文
        context = {
            'type':type,'types':types,
            'cart_count':cart_count,
            'pages':pages,
            'new_skus':new_skus,
            # 'num_pages':num_pages
            'sort':sort,
            'skus_page':skus_page
        }
        # 返回应答
        return render(request,'list.html',context)


