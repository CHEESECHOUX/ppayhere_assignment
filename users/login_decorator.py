import jwt
from django.http import JsonResponse
from payhere.settings import ALGORITHM, SECRET_KEY
from users.models import User


def login_decorator(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization').split(' ')[1]
            payload = jwt.decode(
                access_token,
                SECRET_KEY,
                algorithms=ALGORITHM)
            request.user = User.objects.get(id=payload['id'])

            return func(self, request, *args, **kwargs)

        except User.DoesNotExist:
            return JsonResponse({'message': '사용자가 존재하지 않습니다'}, status=401)
        except jwt.InvalidSignatureError:
            return JsonResponse({'message': 'INVALID_SIGNATURE'}, status=401)
        except jwt.exceptions.DecodeError:
            return JsonResponse({'message': 'INVALID_PAYLOAD'}, status=401)
    return wrapper
