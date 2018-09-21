# 使用celery
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader, RequestContext
from celery import Celery
import time
import os
import django
# django初始化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()
# 导入的类要在django初始化的下方
from goods.models import GoodsType,IndexGoodsBanner,IndexPromotionBanner,IndexTypeGoodsBanner
from django_redis import get_redis_connection
# 创建一个celery对象,第一个参数是路径，第二个参数是中间人。即redis
app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/2')


# 第一个参数是邮件发给谁，第二个参数是发给谁的用户名，第三个参数是链接的token信息
@app.task
def send_register_active_email(to_email, username, token):
    '''发送激活邮件'''
    # 组织邮件信息
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    # 激活链接   带有html标签的发送内容使用html_message发送
    html_message = '<h1>%s,欢迎您访问天天生鲜！</h1>请点击下面链接进行激活：<br><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    # 发送邮件
    send_mail(subject, message, sender, receiver, html_message=html_message)
    # time.sleep(5)

#
# @app.task
# def generate_static_index_html():
#     '''产生首页静态页面'''
#     # 获取商品的种类信息
#     types = GoodsType.objects.all()
#
#     # 获取首页轮播商品信息
#     goods_banners = IndexGoodsBanner.objects.all().order_by('index')
#
#     # 获取首页促销活动信息
#     promotion_banners = IndexPromotionBanner.objects.all().order_by('index')
#
#     # 获取首页分类商品展示信息
#     for type in types:  # GoodsType
#         # 获取type种类首页分类商品的图片展示信息
#         image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
#         # 获取type种类首页分类商品的文字展示信息
#         title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')
#
#         # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
#         type.image_banners = image_banners
#         type.title_banners = title_banners
#
#     # 组织模板上下文
#     context = {'types': types,
#                'goods_banners': goods_banners,
#                'promotion_banners': promotion_banners}
#
#     # 使用模板
#     # 1.加载模板文件，返回模板对象
#     temp = loader.get_template('static_index.html')
#     # 2.定义模板上下文
#     # context = RequestContext(request, context)
#     # 3.模板渲染
#     static_index_html = temp.render(context)
#
#     # 生成首页对应的静态文件
#     save_path = os.path.join(settings.BASE_DIR,'static/index.html')
#     with open(save_path, 'w') as f:
#         f.write(static_index_html)
@app.task
def generate_static_index_html():
    '''产生首页静态页面'''
    # 获取商品的种类信息
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息
    for type in types:  # GoodsType
        # 获取type种类首页分类商品的图片展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1).order_by('index')
        # 获取type种类首页分类商品的文字展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0).order_by('index')

        # 动态给type增加属性，分别保存首页分类商品的图片展示信息和文字展示信息
        type.image_banners = image_banners
        type.title_banners = title_banners


    # 组织模板上下文
    context = {'types': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners}

    # 使用模板
    # 1.加载模板文件,返回模板对象
    temp = loader.get_template('static_index.html')
    # 2.模板渲染
    static_index_html = temp.render(context)

    # 生成首页对应静态文件
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
