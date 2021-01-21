from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from .views import ObtainTokenPairWithColorView, CustomUserCreate, CheckUsernameIsExists, ListProducts, PostEvalute, getProductById, PostBill, ProductsView, Bill,UpdateBill, BillDetail,itemsOrderStar, itemsOrderPrice, itemsOrderTime
urlpatterns = [
    path('user/create/', CustomUserCreate.as_view(), name="create_user"),
    path('checkUserIsExists/', CheckUsernameIsExists.as_view(), name='check_username'),
    #path('token/obtain/', jwt_views.TokenObtainPairView.as_view(), name='token_create'),  # override sjwt stock token
    path('login/', ObtainTokenPairWithColorView.as_view(), name='token_create'),  
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    # path('hello/', HelloWorldView.as_view(), name='hello_world'),
    path('list_product/', ListProducts),
    path('post_evalute/', PostEvalute),
    path('product/<id>', getProductById),
    path('postBill/', PostBill),
    path('add_product/', ProductsView.as_view(), name='post_product'),
    path('list_bill/', Bill),
    path('updateBill/', UpdateBill),
    path('billDetail/', BillDetail),
    path('itemsOrderStar/', itemsOrderStar),
    path('itemsOrderPrice/', itemsOrderPrice),
    path('itemsOrderTime/', itemsOrderTime)

]