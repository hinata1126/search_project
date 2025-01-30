import json
from decimal import Decimal

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from.models import Cart, Product, Category, Order, OrderItem, Review # Product モßデルをインポート
from .forms import ProductForm, SearchForm, ReviewForm # フォームのインポート
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse  # reverseをインポート
from decimal import Decimal




def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()  # 保存したProductインスタンスを取得
            # 生成したproductの詳細ページへリダイレクト
            return redirect(reverse('product_detail', args=[product.pk]))
    else:
        form = ProductForm()  # GETリクエストや、POSTが無効な場合、新しいフォームを表示

    return render(request, 'product_form.html', {'form': form})

# def product_create(request):
#     if request.method == 'POST':
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('product_list')
#         else:
#             form = ProductForm()
#         return render(request, 'product_form.html', {'form': form})
    
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()  # 商品に関連するレビューを取得

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'product_detail.html', context)
    
def product_update(request, pk): 
    product = get_object_or_404(Product, pk=pk) 
    if request.method == 'POST': 
        form = ProductForm(request.POST, instance=product) 
        if form.is_valid(): 
            form.save() 
            return redirect('product_detail', pk=product.pk) 
    else: 
        form = ProductForm(instance=product) 
    # product オブジェクトをテンプレートに渡す
    return render(request, 'product_form.html', {'form': form, 'product': product})

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})

def search_view(request):
    form = SearchForm(request.GET or None)
    results = Product.objects.all() # クエリセットの初期化
    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            results = results.filter(name__icontains=query)
    # カテゴリフィルタリング
    category_name = request.GET.get('category')
    if category_name:
        try:
            # カテゴリ名に基づいてカテゴリ ID を取得
            category = Category.objects.get(name=category_name)
            results = results.filter(category_id=category.id)
        except Category.DoesNotExist:
            results = results.none() # 存在しないカテゴリの場合、結果を空にする
            category = None
    # 価格のフィルタリング (最低価格・最高価格)
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        results = results.filter(price__gte=min_price)
    if max_price:
        results = results.filter(price__lte=max_price)
    
    # 並び替え処理
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_asc':
        results = results.order_by('price')
    elif sort_by == 'price_desc':
        results = results.order_by('-price')

    #商品数の取得
    total_results = results.count()
    
    # クエリセットをリストに変換せず、直接Paginatorに渡す
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html', {'form': form, 'page_obj': page_obj, 'total_results': total_results})

# カートに商品を追加するビュー
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    return redirect('cart_detail')

# カート詳細ビュー
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user)
    cart_total = 0  # 合計金額の初期化

    for item in cart_items:
        item.subtotal = item.product.price * item.quantity  # 小計を計算
        cart_total += item.subtotal  # 合計金額に加算

    return render(request, 'cart_detail.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


# カートアイテムの数量を更新するビュー
@login_required
def update_cart_quantity(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    quantity = int(request.POST.get('quantity', 1))  # デフォルトは1
    cart_item.quantity = quantity
    cart_item.save()
    return redirect('cart_detail')

# カートアイテムを削除するビュー（必要に応じて追加）
@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart_detail')

# カートをJSON形式でシリアライズするビュー（必要に応じて追加）
def serialize_cart(cart_items):
    return json.dumps([
        {
            'name': item.product.name,
            'price': float(item.product.price),
            'quantity': item.quantity
        } for item in cart_items
    ])

@login_required
def checkout(request):
    # 現在のユーザーのカートアイテムを取得
    cart_items = Cart.objects.filter(user=request.user)
    
    # カートが空の場合は、カートページにリダイレクト
    if not cart_items.exists():
        return redirect('cart_detail')
    
    # 合計金額の計算
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    # 注文の確認ページ
    if request.method == 'POST':

        # 注文を保存
        order = Order(user=request.user, total_price=total_price)
        order.save()

    # 注文アイテムを保存
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)

        # 注文確認のフォーム処理がある場合はここに追加
        # 例えば、注文者の名前や住所、支払い方法など
        # 注文が確定した場合、注文を保存し、カートをクリアする
        # 注文情報をモデルに保存するコードをここに記述
        
        # 例: 注文を保存し、カートをクリア
        # order = Order(user=request.user, total_price=total_price)
        # order.save()
        # for item in cart_items:
        #     OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
        
        # カートを空にする
        cart_items.delete()
        
        # 注文完了ページや他のページにリダイレクト
        return redirect('order_complete')  # 注文完了ページにリダイレクト
    
    # カートに入っているアイテムと合計金額を渡して確認ページを表示
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def order_complete(request):
    # 最後に作成した注文を取得（例）
    order = Order.objects.filter(user=request.user).latest('created_at')
    return render(request, 'order_complete.html', {'order': order})

#注文履歴
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)  # ログイン中のユーザーの注文を取得
    order_items = order.items.all()  # related_name 'items' を使って関連するOrderItemを取得
    return render(request, 'order_detail.html', {'order': order, 'order_items': order_items})