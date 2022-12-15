from rest_framework import serializers
from .models import Contact
from django.core.mail import EmailMessage
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_406_NOT_ACCEPTABLE


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','password']
    
    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        a = User.objects.filter(username = username)
        b = User.objects.filter(email = email)
        if a:
            raise ValidationError("User already exist with given Username",HTTP_406_NOT_ACCEPTABLE)
        if b:
            raise ValidationError("User already exist with given email",HTTP_406_NOT_ACCEPTABLE)
        return attrs

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
    def create(self, validated_data):
        contact = Contact.objects.create(**validated_data)

        from_email = validated_data.pop('email')
        ceo = User.objects.filter(is_superuser=True)
        to_email = []
        for x in ceo:
            to_email.append(x.email)

        subject = validated_data.pop('subject')
        body = validated_data.pop('message')
        email = EmailMessage(
            subject = subject,
            body = body,
            from_email = from_email,
            to = to_email
        )
        email.send()
        return contact

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','password']