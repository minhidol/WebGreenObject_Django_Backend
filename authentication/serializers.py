from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser, Products

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super(MyTokenObtainPairSerializer, cls).get_token(user)
        # Add custom claims
        token['name'] = user.name
        token['address'] = user.address
        token['phone'] = user.phone
        token['bill'] = user.bill
        return token

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'name', 'address', 'phone', 'bill')
        extra_kwargs = {'password':{'write_only':True}}
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  # as long as the fields are the same, we can just use thi
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('id',
                  'name',
                  'img',
                  'price',
                  'description',
                  'category',
                  'category_concrete',
                  'date',
                  'count',
                  'count_client',
                  'count_star',
                  'count_star_people',
                  )

