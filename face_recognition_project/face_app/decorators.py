from functools import wraps
from .utils import error_response
from datetime import datetime,timedelta
import jwt
from django.conf import settings
def custom_auth_required(roles=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return error_response(message='未提供认证凭据。', code=403)

            try:
                token_type, token = auth_header.split(' ', 1)
            except ValueError:
                return error_response(message='Authorization 请求头格式无效。必须是 Bearer <token>。', code=403)

            if token_type.lower() != 'bearer':
                return error_response(message='不支持的认证类型。必须是 Bearer。', code=403)

            user = verify_token(token)
            if user is None:
                return error_response(message='无效的 token 或用户未找到。', code=403)

            request.user = user
            if request.user.get('user_type') not in roles:
                return error_response(message='您没有权限访问此资源。', code=403)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# 验证token
def verify_token(token):
    try:
        return jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=['HS256'],
        )  
    except Exception as e:
        return None

# 生成token
def generate_token(user_id, user_type):
    current_utc_time = datetime.utcnow()
    payload = {
        'user_id': user_id,        
        'user_type': user_type,   
        'exp': current_utc_time + timedelta(hours=1), 
        'iat': current_utc_time   
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token.decode('utf-8') if isinstance(token, bytes) else token

# 请求中解析token
def get_token_from_request(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    
    if not auth_header:
        return None  

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
        
    token = verify_token(parts[1])
    
    return token

def get_token_data(token):
    token = get_token_from_request(token)
    user_id = token.get('user_id')
    user_type = token.get('user_type')
    return user_id, user_type