from django.contrib import admin
from . import models


class GoodsCategoryAdmin(admin.ModelAdmin):
    """商品类别模型站点管理类"""

    def save_model(self, request, obj, form, change):
        """
        当点击admin中的保存按钮会调用此方法
        @param request:保存时本次请求对象
        @param obj:本次要保存的模型对象
        @param form:表单
        @param change:
        """
        obj.save()
        # 重新生成新的列表静态页面
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()

    def delete_model(self, request, obj):
        """当点击admin中的删除按钮会调用此方法"""
        obj.delete()
        from celery_tasks.html.tasks import generate_static_list_search_html
        generate_static_list_search_html.delay()


class SKUAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)


class SKUImageAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)
        # 设置SKU默认图⽚
        sku = obj.sku
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
        sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)


admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage, SKUImageAdmin)
