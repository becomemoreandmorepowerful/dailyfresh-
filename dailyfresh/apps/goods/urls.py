from django.conf.urls import url
from goods import views
from goods.views import IndexView

from goods.views import DetailView,ListView

urlpatterns = [
    # url(r'^index/$',views.index,name='index'),
    url(r'^$',IndexView.as_view(),name='index'),
    url(r'^index/$', IndexView.as_view(), name='index'),
    url(r'^goods/(?P<goods_id>\d+)', DetailView.as_view(), name='detail'),
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$',ListView.as_view(),name='list'),
    # url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list'),
]
