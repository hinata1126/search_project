from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from django.conf import settings


class Category(models.Model): 
    name = models.CharField(max_length=255)

    def __str__(self):
         return self.name 

class Product(models.Model): 
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255) 
    description = models.TextField() 
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)  # 画像を追加

# 1 はカテゴリ ID
    def __str__(self): 
        return self.name
    
    def save(self, *args, **kwargs):
        # 画像が設定されている場合のみリサイズを行う
        if self.image:
            img = Image.open(self.image)
            img = img.convert('RGB')  # 画像をRGBに変換（PNGなどの場合）

            # 画像のサイズを設定
            img.thumbnail((200, 200))

            # バッファに画像を保存
            img_io = BytesIO()
            img.save(img_io, format='JPEG')
            img_io.seek(0)

            # メモリ上で保存された画像ファイルをInMemoryUploadedFileとして設定
            self.image = InMemoryUploadedFile(img_io, None, self.image.name, 'image/jpeg', sys.getsizeof(img_io), None)

        super().save(*args, **kwargs)
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta:
            unique_together = ['user', 'product']  # ユーザーと商品が重複しないようにする
    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

#レビューするために必要
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    rating = models.PositiveIntegerField(default=5)  # 1～5の評価値
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating})'