import json
import bcrypt

from django.views import View
from django.http import JsonResponse
from users.models import User

from json.decoder import JSONDecodeError


class SignUpView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            phone = data['phone']
            password = data['password']

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'message': '이미 사용중인 휴대폰 번호 입니다'}, status=400)

            hashed_password = bcrypt.hashpw((password).encode(
                'utf-8'), bcrypt.gensalt()).decode('utf-8')

            User.objects.create(
                phone=phone,
                password=hashed_password,
            )
            return JsonResponse({'message': '회원가입 완료'}, status=201)
        except KeyError:
            return JsonResponse({'message': 'KEY_ERROR'}, status=400)
        except JSONDecodeError:
            return JsonResponse({'message': 'JSON_DECODE_ERROR'}, status=400)
