from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from user import views
from user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView, LogoutView

urlpatterns = [
    # url(r'^register/$',views.register,name='register'),
    # url(r'^register_handle/$',views.register_handle,name='register_handle'),
    url(r'^register/$',RegisterView.as_view(),name='register'),  # 用户注册
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),  # 用户信息激活
    url(r'^login/$', LoginView.as_view(), name='login'),  # 用户登陆
    # url(r'^index$',IndexView.as_view(),name='index')，
    # url(r'^$',login_required(UserInfoView.as_view()),name='user'),  # 用户信息
    # url(r'^order/$',login_required(UserOrderView.as_view()),name='order'),  # 订单页面
    # url(r'^adress/$',login_required(AdressView.as_view()),name='adress'),  # 收货地址
    url(r'^$',UserInfoView.as_view(),name='user'),  # 用户信息
    url(r'^order/(?P<page>\d+)$', UserOrderView.as_view(), name='order'),  # 订单页面
    url(r'^address/$',AddressView.as_view(),name='address'),
    url(r'^logout/$',LogoutView.as_view(),name='logout')
]
