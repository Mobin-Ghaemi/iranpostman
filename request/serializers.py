from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Environment, Collection, APIRequest, RequestHistory, SavedResponse


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class EnvironmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Environment
        fields = ['id', 'name', 'variables', 'user', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CollectionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    requests_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'user', 'requests_count', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def get_requests_count(self, obj):
        return obj.apirequest_set.count()


class APIRequestSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    full_url = serializers.CharField(source='get_full_url', read_only=True)
    
    class Meta:
        model = APIRequest
        fields = [
            'id', 'name', 'method', 'url', 'full_url', 'description',
            'headers', 'params', 'auth_type', 'auth_data',
            'body_type', 'body_raw', 'body_raw_type', 'body_form_data', 'body_urlencoded',
            'timeout', 'follow_redirects',
            'user', 'collection', 'collection_name', 'environment', 'environment_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_collection(self, value):
        """بررسی اینکه collection متعلق به کاربر فعلی باشد"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("شما نمی‌توانید در کالکشن دیگران درخواست ایجاد کنید.")
        return value

    def validate_environment(self, value):
        """بررسی اینکه environment متعلق به کاربر فعلی باشد"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("شما نمی‌توانید از محیط دیگران استفاده کنید.")
        return value


class RequestHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    request_name = serializers.CharField(source='request.name', read_only=True)
    response_json = serializers.SerializerMethodField()
    is_success = serializers.BooleanField(source='is_success', read_only=True)
    
    class Meta:
        model = RequestHistory
        fields = [
            'id', 'request', 'request_name', 'user', 'method', 'url',
            'headers', 'body', 'status_code', 'response_headers', 'response_body',
            'response_json', 'response_time', 'response_size', 'status', 'error_message',
            'is_success', 'executed_at'
        ]
        read_only_fields = ['user', 'executed_at']

    def get_response_json(self, obj):
        return obj.get_response_json()


class SavedResponseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    history_details = RequestHistorySerializer(source='history', read_only=True)
    
    class Meta:
        model = SavedResponse
        fields = ['id', 'name', 'history', 'history_details', 'user', 'notes', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_history(self, value):
        """بررسی اینکه history متعلق به کاربر فعلی باشد"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("شما نمی‌توانید تاریخچه دیگران را ذخیره کنید.")
        return value


class ExecuteRequestSerializer(serializers.Serializer):
    """Serializer برای اجرای درخواست"""
    request_id = serializers.IntegerField()
    
    def validate_request_id(self, value):
        """بررسی وجود درخواست و دسترسی کاربر"""
        try:
            request_obj = APIRequest.objects.get(id=value, user=self.context['request'].user)
            return value
        except APIRequest.DoesNotExist:
            raise serializers.ValidationError("درخواست مورد نظر یافت نشد یا به شما تعلق ندارد.")


class QuickRequestSerializer(serializers.Serializer):
    """Serializer برای درخواست سریع بدون ذخیره"""
    method = serializers.ChoiceField(choices=APIRequest.METHOD_CHOICES, default='GET')
    url = serializers.URLField()
    headers = serializers.JSONField(default=dict, required=False)
    params = serializers.JSONField(default=dict, required=False)
    body_type = serializers.ChoiceField(choices=APIRequest.BODY_TYPE_CHOICES, default='none', required=False)
    body_raw = serializers.CharField(default='', required=False, allow_blank=True)
    body_form_data = serializers.JSONField(default=dict, required=False)
    body_urlencoded = serializers.JSONField(default=dict, required=False)
    timeout = serializers.IntegerField(default=30, required=False)
    follow_redirects = serializers.BooleanField(default=True, required=False) 