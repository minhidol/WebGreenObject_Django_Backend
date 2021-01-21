from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework import status, permissions, authentication, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser, Products
from .serializers import MyTokenObtainPairSerializer, CustomUserSerializer, ProductSerializer
from django.http.response import JsonResponse
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.decorators import api_view
from passlib.hash import django_pbkdf2_sha256 as handler
import random
import pymongo
import urllib.parse
from datetime import datetime
import json
from bson.json_util import loads, dumps
from bson import json_util, ObjectId



username ='minh'
password = 'Khjgt@10'
username = urllib.parse.quote_plus('minh')
password = urllib.parse.quote_plus('Khjgt@10')
myclient = pymongo.MongoClient('mongodb+srv://%s:%s@cluster0.01uom.mongodb.net/<dbname>?retryWrites=true&w=majority' %(username, password))
mydb = myclient['Project_GreenObject']

mycol = mydb['authentication_products']
my_client = mydb['authentication_customuser']
myBill = mydb['bill']






class ObtainTokenPairWithColorView(TokenObtainPairView):
    #permission_classes = (permissions.AllowAny,)
    serializer_class = MyTokenObtainPairSerializer
    authentication_classes = ()
    

class CustomUserCreate(APIView):
    permission_classes = (permissions.AllowAny,)

    # Đăng ký

    def post(self, request, format='json'):
        now = datetime.now()
        serializer = JSONParser().parse(request)
        serializer['password'] = handler.using(rounds=18000).hash(serializer['password'])
        latest = 0
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        temp = my_client.find().sort("_id", -1).limit(1)
        for i in temp:
            latest = i['id']
        serializer['id']=latest+1
        serializer['is_superuser'] = False
        serializer['is_staff'] = False
        serializer['is_active'] = True
        serializer['date_joined'] = dt_string
        serializer['bill'] = []
        x = my_client.insert_one(serializer)
        if x:
            return JsonResponse({"result":"success"}, status=status.HTTP_201_CREATED)
        return JsonResponse({"result":"failure"}, status=status.HTTP_400_BAD_REQUEST)

class CheckUsernameIsExists(APIView):
    permission_classes = (permissions.AllowAny,)

    # Kiểm tra tên đăng nhập tồn tại
    def post(self, request, format='json'):
        a = CustomUser.objects.filter(username=request.data['username'])
        serializer = CustomUserSerializer(a, many=True)
        username_serializer = CustomUserSerializer(data=request.data)
        temp= ''
        dem=0
        for i in range(len(serializer.data)):
            if(request.data['username'] == serializer.data[i]['username']):
                dem = dem + 1
        if(dem == 1):
            temp = 'Yes'
        else:
            temp = 'No'
        return Response({"check":temp}, status=status.HTTP_202_ACCEPTED)


@api_view(['GET', 'POST'])
# Lấy danh sách tất cả các product
def ListProducts(request):
    if request.method == 'GET':
        products = mycol.find()
        products_client = []
        for x in products:
            x.pop('_id')
            products_client.append(x)
        return JsonResponse(products_client, safe=False)
    return Response({"message": "Hello, world!"})


@api_view(['PUT'])
#Post bình luận sản phẩm
def PostEvalute(request):
    if request.method == 'PUT':
        toturial_data = JSONParser().parse(request)
        temp = int(toturial_data['id'])
        mycol.update_one({'id':temp}, {'$push':{'evalute_comment':toturial_data},})
        query={'id':temp}
        count_star = mycol.find(query)[0]['count_star']
        count_people = mycol.find(query)[0]['count_star_people']
        mycol.update_one({'id':temp}, {'$set':{'count_star':count_star+toturial_data['star']}})
        if(toturial_data['star'] != 0):
            mycol.update_one({'id':temp}, {'$set':{'count_star_people':count_people+1}})
        return JsonResponse({"message":"success!"}, safe=False)

@api_view(['GET'])
#
def getProductById(request, id):
    if request.method == 'GET':
        product = Product.objects.get(id=id)
        product_serializer = ProductSerializer(product)
        return JsonResponse(product_serializer.data, safe=False)
       

@api_view(['PUT'])
#Post đơn hàng
def PostBill(request):
    if request.method == 'PUT':
        bill_data = JSONParser().parse(request)

        for i in range(len(bill_data['info_details'])):
            count = bill_data['info_details'][i]['count']
            _count = mycol.find({'id':int(bill_data['info_details'][i]['id'])})[0]['count']
            mycol.update_one({'id':bill_data['info_details'][i]['id']}, {'$set':{'count':_count-count}})
        
        my_client.update_one({'id':int(bill_data['id_user'])}, {'$push':{'bill':bill_data}})
        myBill.insert_one(bill_data)


        return JsonResponse({'message':'success!'}, safe=False)

class ProductsView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        products_serializer = ProductSerializer(data=request.data)
        if products_serializer.is_valid():
            products_serializer.save()
        x = mycol.find().sort("_id", -1).limit(1)
        latest = 0
        for i in x:
            latest = i['id']
        k = mycol.update_one({'id':latest}, {'$set':{'evalute_comment':[]}})
    
        
        return Response({"check":"success"}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def Bill(request):
    if request.method == 'GET':
        list_bill = []
        for x in myBill.find():
            list_bill.append(x)
        a = json.loads(json_util.dumps(list_bill))
        return JsonResponse(a, safe=False)
        
@api_view(['PUT'])
def UpdateBill(request):
    if request.method == 'PUT': 
        status = JSONParser().parse(request)
        if status['status'] == "Xác nhận đơn hàng":
            k = myBill.update_one({"_id":ObjectId(status['_id']['$oid'])}, {'$set':{'status':"Đã xác nhận, đang giao"}})
        elif status['status'] == "Đã nhận hàng":
            k = myBill.update_one({"_id":ObjectId(status['_id']['$oid'])}, {'$set':{'status':"Đã nhận hàng"}})
        elif status['status'] == "Hủy đơn hàng":
            myBill.delete_one({"_id":ObjectId(status['_id']['$oid'])})

        return JsonResponse({"Result":"success"}, safe=False)
        
@api_view(['POST'])
def BillDetail(request):
    if request.method == 'POST':
        status = JSONParser().parse(request)
        x = myBill.find_one({"_id":ObjectId(status['_id']['$oid'])})
        detail = json.loads(json_util.dumps(x))
        return JsonResponse(detail, safe=False)
            
# phan xu li thuat toan

#phan cua Thuan

# phan xu li thuat toan

def Max(a, b):
    if a > b:
        return a
    else:
        return b
#-----------------------------
def Min(a, b):
    if a < b:
        return a
    else:
        return b
#-----------------------------
def ConverPrice(str):
    str_conver = str.replace(" đ", '')
    str_conver = str_conver.replace('.','')
    return int(str_conver)
#-----------------------------
def MedianOfTree(arr, first, last, flag):
    mid = (first + last) // 2
    
    #convert data
    if(flag):
        value_first = arr[first]["count_star_people"] / arr[first]["count_star"] if arr[first]["count_star_people"] > 0 else 0
        value_last = arr[last]["count_star_people"] / arr[last]["count_star"] if arr[last]["count_star_people"] > 0 else 0
        value_mid = arr[mid]["count_star_people"] / arr[mid]["count_star"] if arr[mid]["count_star_people"] > 0 else 0
    else:
        value_first = ConverPrice(arr[first]["price"])
        value_last = ConverPrice(arr[last]["price"])
        value_mid = ConverPrice(arr[mid]["price"])
        
    valueMedian = value_first + value_mid + value_last - Max(Max(value_first, value_mid), value_last) - Min(Min(value_first, value_mid), value_last)
    
    if (value_first == valueMedian):
        arr[mid], arr[first] = arr[first], arr[mid]
    else:
        if (value_last == valueMedian):
            arr[mid], arr[last] = arr[last], arr[mid]
    return
#-----------------------------
def PartitionArr(arr, first, last, flag):
    
    #convert data
    if(flag):
        value_first = arr[first]["count_star_people"] / arr[first]["count_star"] if arr[first]["count_star_people"] > 0 else 0
        value_last = arr[last]["count_star_people"] / arr[last]["count_star"] if arr[last]["count_star_people"] > 0 else 0
    else:
        value_first = ConverPrice(arr[first]["price"])
        value_last = ConverPrice(arr[last]["price"])
    
    pivot = value_first
    lastS1 = first
    firstUnknown = first + 1
    
    while (firstUnknown <= last):
        
        #convert data
        if(flag):
            value_firstUnknown = arr[firstUnknown]["count_star_people"] / arr[firstUnknown]["count_star"] if arr[firstUnknown]["count_star_people"] > 0 else 0
        else:
            value_firstUnknown = ConverPrice(arr[firstUnknown]["price"])
            
        if (value_firstUnknown < pivot):
            arr[firstUnknown], arr[lastS1+1] = arr[lastS1+1], arr[firstUnknown]
            lastS1 += 1
            
        firstUnknown += 1
        
    arr[first], arr[lastS1] = arr[lastS1], arr[first]
    
    return lastS1
#-----------------------------
def QuickSort(arr, first, last, flag):
    if (first < last):
        MedianOfTree(arr, first, last, flag)
        i = PartitionArr(arr, first, last, flag)
        QuickSort(arr, first, i, flag)
        QuickSort(arr, i + 1, last, flag)
    return
#-----------------------------

@api_view(['GET'])
def itemsOrderPrice(request):
    if request.method == 'GET':
        products = list(mycol.find())
        QuickSort(products, 0, len(products)-1, False)
        detail = json.loads(json_util.dumps(products))
        return JsonResponse(detail, safe=False)

@api_view(['GET'])
def itemsOrderStar(request):
    if request.method == 'GET':
        products = list(mycol.find())
        QuickSort(products, 0, len(products) -1, True)
        detail = json.loads(json_util.dumps(products))
        return JsonResponse(detail, safe=False)

@api_view(['GET'])
def itemsOrderTime(request):
    if request.method == 'GET':
        products = mycol.find_one()
        detail = json.loads(json_util.dumps(products))
        _products = []
        _products.append(detail)
        return JsonResponse(_products, safe=False)
        

