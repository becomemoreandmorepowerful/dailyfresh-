# from django.conf import settings
# from django.core.files.storage import Storage
# from fdfs_client.client import Fdfs_client
#
#
# class FDFSStorage(Storage):
#     '''fdfs文件存储类'''
#
#     def __init__(self,client_conf=None,base_url=None):
#         '''初始化'''
#         # 如果没有指定client.conf的路径
#         if client_conf is None:
#             client_conf = settings.FDFS_CLIENT_CONF
#         self.client_conf = client_conf
#         # 如果没有指定Url，就使用settings里面的配置
#         if base_url is None:
#             base_url = settings.FDFS_URL
#         self.base_url = base_url
#
#
#     def open(self, name, mode='rb'):
#         '''打开文件时使用'''
#         pass
#
#     def _save(self, name, content):
#         '''保存文件时使用'''
#         # name是选择上传文件的名字 content包含上传文件的内容的File对象
#         # 创建一个Fdfs_client对象 并指定client.conf的路径
#         client = Fdfs_client(self.client_conf)
#         # 上传文件到fast dfs系统 括号里面是上传的文件的内容
#         res = client.upload_by_buffer(content.read())
#         # dict
#         # {
#         #     'Group name': group_name,
#         #     'Remote file_id': remote_file_id,
#         #     'Status': 'Upload successed.',
#         #     'Local file name': '',
#         #     'Uploaded size': upload_size,
#         #     'Storage IP': storage_ip
#         # }
#
#         if res.get('Status') != 'Upload successed':
#             # 上传失败
#             raise Exception('上传文件失败')
#         filename = res.get('Remote file_id')
#         return filename
#
#     def exists(self, name):
#         '''判断文件名是否可用'''
#         # False表示文件名可用
#         return False
#
#     def url(self, name):
#         '''返回访问url的路径'''
#         return self.base_url + name


from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
    '''fast dfs文件存储类'''
    def __init__(self, client_conf=None, base_url=None):
        '''初始化'''
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url

    def _open(self, name, mode='rb'):
        '''打开文件时使用'''
        pass

    def _save(self, name, content):
        '''保存文件时使用'''
        # name:你选择上传文件的名字 test.jpg
        # content:包含你上传文件内容的File对象

        # 创建一个Fdfs_client对象
        client = Fdfs_client(self.client_conf)

        # 上传文件到fast dfs系统中
        res = client.upload_by_buffer(content.read())

        # dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': '',
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res.get('Status') != 'Upload successed.':
            # 上传失败
            raise Exception('上传文件到fast dfs失败')

        # 获取返回的文件ID
        filename = res.get('Remote file_id')

        return filename

    # 1.jpg
    def exists(self, name):
        '''Django判断文件名是否可用'''
        return False

    def url(self, name):
        '''返回访问文件的url路径'''
        return self.base_url+name



