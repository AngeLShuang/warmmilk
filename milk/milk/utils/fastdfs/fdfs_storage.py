from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FastDFSStorage(Storage):
    """
    自定义文件存储系统类
    """

    def __init__(self, client_path=None, base_url=None):
        self.client_path = client_path or settings.FDFS_CLIENT_CONF
        self.base_url = base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """
        用户打开文件，自定义文件存储系统类的目的为了实现存储到远程的FastDFS服务器，不需要打开文件，所以此方法重写后什么也不做
        """
        pass

    def _save(self, name, content):
        """
        文件存储时调用此方法，默认是向本地存储，在此方法中实现存储到远程的FastDFS服务器
        content:以rb模式打开的文件对象，将来通过content.read()就可以读取到文件的二进制数据
        """
        client = Fdfs_client(self.client_path)
        ret = client.upload_by_buffer(content.read())  # 通过文件二进制数据进行上传  upload_by_filename只能通过文件绝对路径进行上传
        if ret.get('Status') != 'Upload successed.':
            raise Exception('Upload file failed')
        return ret.get('Remote file_id')

    def exists(self, name):
        """
        上传文件时判断文件是否已存在
        """
        return False

    def url(self, name):
        """
        获取图片文件的绝对路径  name：file_id
        """
        return self.base_url + name
