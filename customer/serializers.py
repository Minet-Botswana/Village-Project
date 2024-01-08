from rest_framework import serializers
from .models import KYCform

class KYCuploadForm(serializers.ModelSerializer):
    class Meta:
        model = KYCform
        fields = ['kyc_form']

    def create(self, validated_data):
        form_file = validated_data['kyc_form']
        filename = form_file.name
        form_file_url = KYCform.upload_form(form_file, filename)
        user = validated_data.get('user', None)
        return KYCform.objects.create(customer=user, kyc_form=form_file_url, **validated_data)

