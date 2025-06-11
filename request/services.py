import requests
import json
import time
from urllib.parse import urlencode
from django.utils import timezone
from .models import APIRequest, RequestHistory


class RequestExecutionService:
    """سرویس اجرای درخواست‌های HTTP"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def execute_request(self, api_request: APIRequest, user=None):
        """اجرای یک درخواست API و ذخیره تاریخچه"""
        start_time = time.time()
        
        # ایجاد تاریخچه
        history = RequestHistory(
            request=api_request,
            user=user or api_request.user,
            method=api_request.method,
            url=api_request.get_full_url(),
            headers=api_request.headers or {},
            body=self._prepare_body(api_request)
        )
        
        try:
            # آماده‌سازی درخواست
            request_data = self._prepare_request_data(api_request)
            
            # اجرای درخواست
            response = self.session.request(**request_data)
            
            # محاسبه زمان پاسخ
            response_time = time.time() - start_time
            
            # ذخیره اطلاعات پاسخ
            history.status_code = response.status_code
            history.response_headers = dict(response.headers)
            history.response_body = response.text
            history.response_time = response_time
            history.response_size = len(response.content)
            history.status = 'success'
            
        except requests.exceptions.Timeout:
            history.status = 'timeout'
            history.error_message = 'درخواست منقضی شد'
            
        except requests.exceptions.RequestException as e:
            history.status = 'error'
            history.error_message = str(e)
            
        except Exception as e:
            history.status = 'error'
            history.error_message = f'خطای غیرمنتظره: {str(e)}'
        
        # ذخیره تاریخچه
        history.save()
        return history
    
    def execute_quick_request(self, request_data: dict, user):
        """اجرای درخواست سریع بدون ذخیره در مدل APIRequest"""
        start_time = time.time()
        
        # ایجاد تاریخچه
        history = RequestHistory(
            user=user,
            method=request_data['method'],
            url=self._build_url_with_params(request_data['url'], request_data.get('params', {})),
            headers=request_data.get('headers', {}),
            body=self._prepare_body_from_dict(request_data)
        )
        
        try:
            # آماده‌سازی درخواست
            prepared_data = self._prepare_request_data_from_dict(request_data)
            
            # اجرای درخواست
            response = self.session.request(**prepared_data)
            
            # محاسبه زمان پاسخ
            response_time = time.time() - start_time
            
            # ذخیره اطلاعات پاسخ
            history.status_code = response.status_code
            history.response_headers = dict(response.headers)
            history.response_body = response.text
            history.response_time = response_time
            history.response_size = len(response.content)
            history.status = 'success'
            
        except requests.exceptions.Timeout:
            history.status = 'timeout'
            history.error_message = 'درخواست منقضی شد'
            
        except requests.exceptions.RequestException as e:
            history.status = 'error'
            history.error_message = str(e)
            
        except Exception as e:
            history.status = 'error'
            history.error_message = f'خطای غیرمنتظره: {str(e)}'
        
        # ذخیره تاریخچه
        history.save()
        return history
    
    def _prepare_request_data(self, api_request: APIRequest):
        """آماده‌سازی داده‌های درخواست از مدل APIRequest"""
        data = {
            'method': api_request.method,
            'url': api_request.get_full_url(),
            'headers': api_request.headers or {},
            'timeout': api_request.timeout,
            'allow_redirects': api_request.follow_redirects,
        }
        
        # اضافه کردن body
        body = self._prepare_body(api_request)
        if body:
            if api_request.body_type == 'form-data':
                data['data'] = api_request.body_form_data
            elif api_request.body_type == 'x-www-form-urlencoded':
                data['data'] = api_request.body_urlencoded
            else:
                data['data'] = body
        
        return data
    
    def _prepare_request_data_from_dict(self, request_data: dict):
        """آماده‌سازی داده‌های درخواست از dict"""
        data = {
            'method': request_data['method'],
            'url': self._build_url_with_params(request_data['url'], request_data.get('params', {})),
            'headers': request_data.get('headers', {}),
            'timeout': request_data.get('timeout', 30),
            'allow_redirects': request_data.get('follow_redirects', True),
        }
        
        # اضافه کردن body
        body = self._prepare_body_from_dict(request_data)
        if body:
            body_type = request_data.get('body_type', 'none')
            if body_type == 'form-data':
                data['data'] = request_data.get('body_form_data', {})
            elif body_type == 'x-www-form-urlencoded':
                data['data'] = request_data.get('body_urlencoded', {})
            else:
                data['data'] = body
        
        return data
    
    def _prepare_body(self, api_request: APIRequest):
        """آماده‌سازی body درخواست"""
        if api_request.body_type == 'none':
            return ''
        elif api_request.body_type == 'raw':
            return api_request.body_raw
        elif api_request.body_type == 'form-data':
            return urlencode(api_request.body_form_data or {})
        elif api_request.body_type == 'x-www-form-urlencoded':
            return urlencode(api_request.body_urlencoded or {})
        return ''
    
    def _prepare_body_from_dict(self, request_data: dict):
        """آماده‌سازی body از dict"""
        body_type = request_data.get('body_type', 'none')
        
        if body_type == 'none':
            return ''
        elif body_type == 'raw':
            return request_data.get('body_raw', '')
        elif body_type == 'form-data':
            return urlencode(request_data.get('body_form_data', {}))
        elif body_type == 'x-www-form-urlencoded':
            return urlencode(request_data.get('body_urlencoded', {}))
        return ''
    
    def _build_url_with_params(self, url: str, params: dict):
        """ساخت URL با پارامترها"""
        if not params:
            return url
        
        params_str = '&'.join([f"{k}={v}" for k, v in params.items() if v])
        if not params_str:
            return url
            
        separator = '&' if '?' in url else '?'
        return f"{url}{separator}{params_str}"


# تابع کمکی برای استفاده آسان
def execute_api_request(api_request: APIRequest, user=None):
    """اجرای درخواست API"""
    service = RequestExecutionService()
    return service.execute_request(api_request, user)


def execute_quick_request(request_data: dict, user):
    """اجرای درخواست سریع"""
    service = RequestExecutionService()
    return service.execute_quick_request(request_data, user) 