from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

    def create(self, validated_data):
        profile_pic_file = validated_data['profile_pic']
        filename = profile_pic_file.name
        pro_pic_url = Customer.upload_image(profile_pic_file, filename)
        user = validated_data.get('user', None)
        return Customer.objects.create(user=user, profile_pic=pro_pic_url, **validated_data)
