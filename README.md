# ppayhere_assignment

- 과제 수행 기간 : 2023.04.20 ~ 202304.24
- 사용 언어 및 프레임워크 : Python, Django/DRF
- Database : MySQL : 5.7
<br/>

# 🛠 ERD
<img width="1033" alt="스크린샷 2023-04-24 오후 8 48 42" src="https://user-images.githubusercontent.com/89918678/233992769-e6b0f1a3-5729-43f7-a0ba-5d5ccf9932b4.png">

- 서비스 확장 시 다양해질 카테고리와 상품을 고려해 카테고리 테이블과 상품 테이블은 1:N 비식별 관계로 설계했습니다.
- 음료 사이즈는 small, large 총 두 가지이므로 ENUM 데이터 타입을 사용했습니다.
<br/>

# 📡 API
### [API Documentation](https://documenter.getpostman.com/view/20782433/2s93Y5QLSk)

|기능|EndPoint|메소드|
|:---|:---|:---:|
|회원가입|/users/signup|POST|
|로그인|/users/login|POST|
|로그아웃|/users/logout|POST|
|상품 생성|/products/create|POST|
|상품 리스트 가져오기|/products/list|GET|
|해당 상품 정보 가져오기|/products/detail/{product_id}|GET|
|상품 단어, 초성 검색|/products/search|GET|
|상품 부분 수정|/products/update/{product_id}|PATCH|
|상품 삭제|/products/delete/{product_id}|DELETE|
<br/>

# 🙋🏻‍♀️ 구현
1. 사장님은 휴대폰 번호와 비밀번호를 입력을 통해 회원가입<br/>
(정규표현식을 통해 유효성 검사)
- 휴대폰 번호 : {3개의숫자}-{3~4개의숫자}-{4개의숫자} ex) 010-1234-5678
- 비밀번호 : 숫자, 대문자 알파벳, 소문자 알파벳 최소 한 개 이상씩 포함, 문자열 최소 8자리 이상 ex)Jisoo1234
2. bcrypt를 사용해 사장님의 비밀번호를 암호화
3. PyJWT를 사용해 access_token으로 인증 제어
4. 로그인 데코레이터를 사용해 로그인하지 않은 사장님의 상품 관련 API에 대한 접근 제한 처리
<br/>

# 💡 고민했던 점
---
### 1. 초성 검색 기능<br/>
__[구현 요구 사항]__<br/>
- user는 상품 이름에 대해 like 검색과 초성 검색 기능을 지원해야합니다.<br/>
ex) 슈크림 라떼 -> 검색 가능한 키워드 : 슈크림, 크림, 라떼, ㅅㅋㄹ, ㅋㄹ, ㄹㄸ<br/>

__[구현한 방법]__<br/>
- user가 상품 이름 등록시, 초성값도 함께 DB에 저장되도록 구현
- 초성을 추출하는 함수(get_chosung)를 만들고 icontains 쿼리 연산자를 활용해, user가 입력한 keyword 문자열이(대소문자 구분 없이) 포함 되어있는지 확인

---
### 2. 상품 등록 기능<br/>
__[구현 요구 사항]__<br/>
- user는 상품을 등록할 수 있습니다.

__[구현한 방법]__<br/>
- user가 상품을 create할 때 user_id, category_id가 상품 정보와 함께 DB에 저장되도록 구현<br/>
- get_or_create() 메서드를 사용해 category_name이 DB에 존재할 경우 category_id를 get해서 DB에 저장, 존재하지 않을 경우 create해서 DB에 저장하도록 구현
