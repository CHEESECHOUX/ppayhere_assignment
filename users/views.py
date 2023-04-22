import json
import bcrypt
import jwt

from datetime import datetime, timedelta

from django.views import View
from django.http import JsonResponse
from json.decoder import JSONDecodeError
from django.conf import settings

from users.validation import phone_validate, password_validate
from users.models import User
from users.login_decorator import login_decorator
from django.contrib.auth import logout


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone']
            password = data['password']

            phone_validate(phone)
            password_validate(password)

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'message': '이미 사용중인 휴대폰 번호 입니다'}, status=400)

            hashed_password = bcrypt.hashpw(
                (password).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            User.objects.create(
                phone=phone,
                password=hashed_password,
            )

            return JsonResponse({'meta': {'code': 201, 'message': '회원가입 완료'}, 'data': data})

        except KeyError:
            return JsonResponse({'meta': {'code': 400, 'message': 'KEY_ERROR'}})
        except JSONDecodeError:
            return JsonResponse({'meta': {'code': 400, 'message': 'JSON_DECODE_ERROR'}})


class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            user = User.objects.get(phone=data['phone'])

            hashed_password = user.password.encode('utf-8')
            access_token = jwt.encode(
                {'id': user.id, 'exp': datetime.utcnow() + timedelta(weeks=1)},
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM
            )

            if not bcrypt.checkpw(data['password'].encode('utf-8'), hashed_password):
                return JsonResponse({'meta': {'code': 401, 'message': '비밀번호를 다시 입력해주세요'}})

            return JsonResponse({'meta': {'code': 200, 'message': '로그인 성공', 'token': access_token}, 'data': data})

        except User.DoesNotExist:
            return JsonResponse({'meta': {'code': 404, 'message': '사용자가 존재하지 않습니다'}})
        except KeyError:
            return JsonResponse({'meta': {'code': 400, 'message': 'KEY_ERROR'}})


class LogoutView(View):
    @login_decorator
    def post(self, request):
        logout(request)
        return JsonResponse({'meta': {'code': 200, 'message': '로그아웃 되었습니다'}})
