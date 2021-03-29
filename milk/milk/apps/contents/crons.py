from collections import OrderedDict
from django.conf import settings
from django.template import loader
import os
import time
from milk.apps.goods.utils import get_categories
from .models import ContentCategory


def generate_static_index_html():
    """
    生成静态的主页html文件
    """
    categories = get_categories()
    # 广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')
    # 渲染模板
    context = {
        'categories': categories,
        'contents': contents
    }
    # 加载模板文件
    template = loader.get_template('index.html')
    # 渲染模板
    html_text = template.render(context)
    # print(html_text)
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    # encoding ： 用于解决在定时器执行时中文字符编码的问题
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
