# from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse

from dailyfresh import settings
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
import re
from django.views.generic import View

from goods.models import GoodsSKU
from user.models import User, Address
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired
from celery_tasks import tasks
from django_redis import get_redis_connection


# Create your views here.
from utils.mixin import LoginRequiredMixin


# def register(request):
#     '''显示注册页面'''
#     # 请求方式是get显示注册页面
#     if request.method == 'get':
#         return render(request,'register.html')
#     # 请求方式是post 表单提交
#     else:
#         # 获取参数
#         username = request.POST.get('user_name')
#         password = request.POST.get('pwd')
#         email = request.POST.get('email')
#         allow = request.POST.get('allow')
#         # 校验参数
#         # 完整性校验，输入内容不能为空
#         if not all([username, email, password]):
#             return render(request, 'register.html', {'errormsg': '注册失败，请输入完整'})
#         # 业务逻辑处理
#         # 匹配邮箱
#         if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
#             return render(request, 'register.html', {'errormsg': '你输入的邮箱格式不正确，请重新输入'})
#         # 让用户选择同意使用协议
#         if allow != 'on':
#             return render(request, 'register.html', {'errormsg': '请选择同意用户使用协议'})
#         # 返回应答
#         # 从数据库获取数据，判断用户名是否重复
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             # 用户名不存在
#             user = None
#
#         # 如果数据库中已经存在用户名,返回注册页面让用户重新注册
#         if user:
#             return render(request, 'register.html', {'errormsg': '该用户名已经被注册，请重新注册'})
#         # 如果注册成功，生成User对象，并在数据库中产生一条记录，保存用户的信息
#         user = User.objects.create_user(username, email, password)
#         # 用户信息未激活
#         user.is_active = 0
#         user.save()
#
#         # 注册成功跳转到首页
#         return redirect(reverse('goods:index'))
#
#
#
# def register_handle(request):
#     '''注册提交处理'''
#     # 获取参数
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#     allow = request.POST.get('allow')
#     # 校验参数
#     # 完整性校验，输入内容不能为空
#     if not all([username, email, password]):
#         return render(request, 'register.html', {'errormsg': '注册失败，请输入完整'})
#     # 业务逻辑处理
#     # 匹配邮箱
#     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
#         return render(request, 'register.html', {'errormsg': '你输入的邮箱格式不正确，请重新输入'})
#     # 让用户选择同意使用协议
#     if allow != 'on':
#         return render(request, 'register.html', {'errormsg': '请选择同意用户使用协议'})
#     # 返回应答
#     # 从数据库获取数据，判断用户名是否重复
#     try:
#         user = User.objects.get(username=username)
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#
#     # 如果数据库中已经存在用户名,返回注册页面让用户重新注册
#     if user:
#         return render(request, 'register.html', {'errormsg': '该用户名已经被注册，请重新注册'})
#     # 如果注册成功，生成User对象，并在数据库中产生一条记录，保存用户的信息
#     user = User.objects.create_user(username, email, password)
#     # 用户信息未激活
#     user.is_active = 0
#     user.save()
#
#     # 注册成功跳转到首页
#     return redirect(reverse('goods:index'))

# /register
from order.models import OrderInfo

from order.models import OrderGoods


class RegisterView(View):
    '''定义类试图，处理请求方式'''
    def get(self,request):
        return render(request, 'register.html')

    def post(self,request):
        # 获取参数
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 校验参数
        # 完整性校验，输入内容不能为空
        if not all([username, email, password]):
            return render(request, 'register.html', {'errmsg': '注册失败，请输入完整'})
        # 业务逻辑处理
        # 匹配邮箱
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}', email):
            return render(request, 'register.html', {'errmsg': '你输入的邮箱格式不正确，请重新输入'})
        # 让用户选择同意使用协议
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请选择同意用户使用协议'})
        # 返回应答
        # 从数据库获取数据，判断用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        # 如果数据库中已经存在用户名,返回注册页面让用户重新注册
        if user:
            return render(request, 'register.html', {'errmsg': '该用户名已经被注册，请重新注册'})
        # 如果注册成功，生成User对象，并在数据库中产生一条记录，保存用户的信息
        user = User.objects.create_user(username, email, password)
        # 用户信息未激活
        user.is_active = 0
        user.save()
        # 邮箱验证
        # 创建一个加密的对象，第一个参数是密钥，第二个参数是过期时间
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        # 调用对象的dump方法对用户的id进行加密,token接收加密的信息
        token = serializer.dumps(info)
        token = token.decode()
        # 发送邮件
        # subject = '天天生鲜欢迎信息'
        # message = ''
        # sender = settings.EMAIL_FROM
        # receiver = [email]
        # # 激活链接
        # html_message = '<h1>%s,欢迎您访问天天生鲜！</h1>请点击下面链接进行激活：<br><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' %(username,token,token)
        # # 发送邮件
        # send_mail(subject,message,sender,receiver,html_message=html_message)

        # delay函数可以实现把任务放到任务队列
        tasks.send_register_active_email.delay(email,username,token)

        # 注册成功跳转到首页
        return redirect(reverse('goods:index'))

# /active
class ActiveView(View):
    '''用户信息激活'''
    def get(self,request,token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            # 获取加密的信息
            info = serializer.loads(token)
            # 获取用户的id
            user_id = info['confirm']
            # 从数据库中获取获取用户的信息
            user = User.objects.get(id=user_id)
            # 然后对用户信息进行激活
            user.is_active = 1
            user.save()
            # 用户信息激活 跳转登陆页面
            return redirect(reverse("user:login"))

        except SignatureExpired as result:
            # 链接过期 返回结果
            return HttpResponse('链接已经过期')

# /loginui8
class LoginView(View):
    '''登陆'''
    def get(self,request):
        '''显示登陆页面'''
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request,'login.html',{'username':username,'checked':checked})

    def post(self,request):
        # 获取参数
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        remember = request.POST.get('remember')
        # 校验参数
        # 用户名为空
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'请输入用户名和密码'})
        # 业务逻辑处理，认证用户名和密码是否正确，如果正确返回一个user对象
        user = authenticate(username=username,password=password)
        # 用户不为空，说明数据库已经存在这个用户
        if user is not None:
            # 用户已经激活
            if user.is_active:
                # 记住用户登陆
                login(request,user)
                # 获取登陆后跳转的地址 如果为空，走默认值即reverse('goods:index')重定向到首页
                # next_url = request.GET.get('next', reverse('goods:index'))
                next_url = request.GET.get('next',reverse('goods:index'))
                response = redirect(next_url)
                if remember == 'on':
                    response.set_cookie('username',username,max_age=7*24*3600)
                else:
                    response.delete_cookie('username')
                return response
            else:
                return render(request,'login.html',{'errmsg':'账户未激活'})

        else:
            return render(request,'login.html',{'errmsg':'用户名或者密码不正确'})

# /logout
class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect(reverse('goods:index'))


# /user
class UserInfoView(LoginRequiredMixin, View):
    '''用户信息页面'''
    def get(self,request):
        '''显示'''
        # Django会给request对象添加一个属性request.user
        # 如果用户未登录->user是AnonymousUser类的一个实例对象
        # 如果用户登录->user是User类的一个实例对象
        # request.user.is_authenticated()

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        # from redis import StrictRedis
        # sr = StrictRedis(host='172.16.179.130', port='6379', db=9)
        # 从django-redis中导入下面的方法
        con = get_redis_connection('default')
        # history记录用户的浏览记录
        history_key = 'history_%d' % user.id

        # 获取用户最新浏览的5个商品的id，第一个参数是查询集，第二呵第三个参数是查询的范围
        sku_ids = con.lrange(history_key, 0, 4)  # [2,3,1]

        # 从数据库中查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # 遍历获取用户浏览的商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li}

        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件
        return render(request, 'user_center_info.html', context)

# /order
class UserOrderView(LoginRequiredMixin,View):
    '''用户订单页面'''
    def get(self, request, page):
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        for order in orders :
            order_skus = OrderGoods.objects.filter(order_id= order.order_id)
            # print(order_skus)
            for order_sku in order_skus:
                amount = order_sku.price * order_sku.count
                order_sku.amount = amount
            # 动态增加属性
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            order.order_skus = order_skus

        paginator = Paginator(orders, 1)
        try :
            page = int(page)
        except Exception as e:
            page = 1

        # 获取第page页的实例对象
        order_page = paginator.page(page)
        # 获取总页数
        num_pages = paginator.num_pages
        if page > num_pages:
            page =1
        if page <= 3:
            pages = range(1, 6)
        elif num_pages < 5:
            pages = range(1, num_pages+1)
        elif num_pages - page <= 2:
            pages = range(num_pages-4,num_pages+1)
        else:
            pages = range(page-2,page+3)

        context = {
            'pages':pages,
            'page':'order',
            'order_page':order_page
        }

        return render(request,'user_center_order.html',context)

# /user
class AddressView(LoginRequiredMixin,View):
    '''用户收货地址页面'''
    def get(self,request):
        # 获取登陆用户的user对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        #
        # except address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        return render(request,'user_center_site.html',{'page':'address','address':address})

    def post(self,request):
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver, addr, phone]):
            return render(request,'user_center_site.html',{'errmsg':'请输入完整'})

        if not re.match(r'1[3|4|5|6|7|8|9][0-9]{9}$',phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机号输入不正确，请重新输入'})
        # 如果已经有默认的收货地址，则添加的地址不作为默认收货地址
        # 获取登陆用户的user对象
        user = request.user
        # try :
        #     address = Address.objects.get(user=user,is_default=True)
        #
        # except address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False

        else:
            is_default = True
        # 在数据库记录数据
        Address.objects.create(user = user,
                               phone = phone,
                               zip_code = zip_code,
                               addr = addr,
                               is_default = is_default,
                               receiver = receiver)
        return redirect(reverse('user:address'))