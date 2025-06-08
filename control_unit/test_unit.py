import subprocess
import json

def run_curl(cmd: str):
    method = "UNKNOWN"
    url = "UNKNOWN"
    purpose = "UNKNOWN"
    for line in cmd.split('\n'):
        if "#" in line or line.strip().startswith("#"):
            purpose = line
        if "curl -X" in line or line.strip().startswith("curl -X"):
            parts = line.split()
            if "-X" in parts:
                method_index = parts.index("-X") + 1
                if method_index < len(parts):
                    method = parts[method_index].strip("'\"")
        if "http://" in line or "https://" in line:
            url = line.strip().strip("'\"").split("://")[1]
            url = "/" + "/".join(url.split("/")[1:])

    print(f"\n[test] {purpose}")
    print(f"[실행 url] {method} {url}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("[응답]:", result.stdout.strip())
        return result.stdout.strip()
    elif result.stderr:
        print("[에러]:", result.stderr.strip())
    return ""

curl_list_no_token = [
'''#회원가입 성공(권한 없음에서 추가확인하기 위함)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/SignUp' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "e_mail": "@23",
    "user_name": "NoPermission",
    "phone_num": "string",
    "user_info": "string",
    "create_on": "2025-06-06T11:25:35.982Z",
    "password": "123"
}' ''',
'''#회원가입 실패 (같은 이메일)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/SignUp' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "e_mail": "shinheewon@korea.ac.kr",
    "user_name": "string",
    "phone_num": "string",
    "user_info": "string",
    "create_on": "2025-06-06T11:25:35.982Z",
    "password": "123"
}' ''',
'''#회원가입 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/SignUp' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "e_mail": "@",
    "user_name": "string",
    "phone_num": "string",
    "user_info": "string",
    "create_on": "2025-06-06T11:25:35.982Z",
    "password": "123"
}' ''',
'''#잘못된 로그인\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/SignIn' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "e_mail": "@",
    "password": "123@"
}' ''',
'''#로그인 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/SignIn' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "e_mail": "@",
    "password": "123"
}' '''
]

user_one_token = ""

print("\n\n[로그인 기능 확인]\n\n")

for curl in curl_list_no_token:
    result = run_curl(curl)
    if result:
        try:
            token = json.loads(result).get("token")
            if token:
                user_one_token = token
        except json.JSONDecodeError:
            print("[경고] JSON 파싱 실패:", result)


a = [
'''#비밀번호 확인 실패\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/Reauthorization' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "password" : "12@3"
    }' ''',
'''#비밀번호 확인 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/Reauthorization' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "password" : "123"
    }' '''
]

b = []

for curl_cmd in a:
    auth_line = f"-H 'Authorization: Bearer {user_one_token}' \\"

    if "-d '" in curl_cmd:
        parts = curl_cmd.split("-d '", 1)
        before_d = parts[0].rstrip()
        after_d = "-d '" + parts[1]
        if not before_d.strip().endswith('\\'):
            before_d += " \\"
        modified_cmd = before_d + "\n" + auth_line + "\n" + after_d
    else:
        lines = curl_cmd.strip().split('\n')
        for i, line in enumerate(lines):
            if "-H 'accept: application/json'" in line:
                lines.insert(i + 1, auth_line)
                break
        modified_cmd = '\n'.join(lines)

    b.append(modified_cmd)

user_one_token = ""

for curl in b:
    result = run_curl(curl)
    if result:
        try:
            token = json.loads(result).get("token")
            if token:
                user_one_token = token
        except json.JSONDecodeError:
            print("[경고] JSON 파싱 실패:", result)

print("\n\n[로그인 기능 확인]\n\n")

curl_list_need_token = [
###User
'''#내 프로필 보기\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/Me' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#내 프로필 변경\n
    curl -X 'PUT' \\
    'http://127.0.0.1:8000/KU/User/Me' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "string",
  "user_name": "string",
  "phone_num": "string",
  "user_info": "string",
  "create_on": "2025-06-07T07:26:24.579Z",
  "password": "string"
}' ''',
'''#다른 유저 프로필 검색 실패(없는 유저)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/?user_id=222' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#다른 유저 검색 성공 \n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/?user_id=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
###Crew
'''#모임 생성 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "crew_name": "string",
    "description": "string"
    }' ''',
'''#내 프로필 보기 (crew변화 보기)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/Me' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#모임 생성 실패 (이미 있는 이름)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "crew_name": "string",
    "description": "string"
    }' ''',
'''#모임 정보 검색 실패 (없는 id)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Crew/22' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#모임 정보 검색 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Crew/1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#새로운 유저 등록 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/1/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#유저 정보 변경 확인\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/?user_id=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#모임 정보 검색 성공(새로운 유저 반영 확인)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Crew/1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#새로운 유저 등록 실패(이미 있는 유저)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/1/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#새로운 유저 등록 실패(없는 유저)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/1/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korr"
}' ''',
'''#유저 삭제 성공\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Crew/1/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#유저 삭제 실패(없는 유저)\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Crew/1/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
###Post
'''#새로운 게시물 작성\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Post/' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "title": "string",
  "content": "string",
  "when": "string",
  "where": "string"
}' ''',
'''#게시물 불러오기 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=2' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#게시물 페이징 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Post/List/?page_num=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#게시물 페이징 실패 (컨텐츠 없음)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=10' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''', 
'''#게시물 수정 성공\n
    curl -X 'PUT' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=2' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "title": "string",
  "content": "string",
  "when": "string",
  "where": "string"
}' ''',
'''#게시물 불러오기 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=2' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#게시물 수정 실패 (post없음)\n
    curl -X 'PUT' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=24' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "title": "string",
  "content": "string",
  "when": "string",
  "where": "string"
}' ''',
'''#게시물 삭제 성공\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=2' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#게시물 불러오기 실패 (post없음)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=2' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#게시물 삭제 실패 (post없음)\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=2' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#crew 유저 추가 완료 (권한 없음에서 추가확인 위함)
curl -X POST \\
  'http://127.0.0.1:8000/KU/Crew/1/Member' \\
  -H 'accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "e_mail": "@23"
  }' '''
    
]

curl_list_have_token = []

for curl_cmd in curl_list_need_token:
    auth_line = f"-H 'Authorization: Bearer {user_one_token}' \\"

    if "-d '" in curl_cmd:
        parts = curl_cmd.split("-d '", 1)
        before_d = parts[0].rstrip()
        after_d = "-d '" + parts[1]
        if not before_d.strip().endswith('\\'):
            before_d += " \\"
        modified_cmd = before_d + "\n" + auth_line + "\n" + after_d
    else:
        lines = curl_cmd.strip().split('\n')
        for i, line in enumerate(lines):
            if "-H 'accept: application/json'" in line:
                lines.insert(i + 1, auth_line)
                break
        modified_cmd = '\n'.join(lines)

    curl_list_have_token.append(modified_cmd)

print("\n\n[jwt필요 기능 확인]\n\n")

for curl in curl_list_have_token:
    result = run_curl(curl)
####################################################################

print("\n\n[권한 없음 확인 + no leader 권한 작동 확인]\n\n")

curl_list_no_token_for_permission_check = [
'''#로그인 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/SignIn' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "e_mail": "@23",
    "password": "123"
}' '''
]

user_one_token_for_permission_check = ""

for curl in curl_list_no_token_for_permission_check:
    result = run_curl(curl)
    if result:
        try:
            token = json.loads(result).get("token")
            if token:
                user_one_token_for_permission_check = token
        except json.JSONDecodeError:
            print("[경고] JSON 파싱 실패:", result)

aa = [
    '''#비밀번호 확인 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/User/Reauthorization' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "password" : "123"
    }' '''
]


bb = []

for curl_cmd in aa:
    auth_line = f"-H 'Authorization: Bearer {user_one_token_for_permission_check}' \\"

    if "-d '" in curl_cmd:
        parts = curl_cmd.split("-d '", 1)
        before_d = parts[0].rstrip()
        after_d = "-d '" + parts[1]
        if not before_d.strip().endswith('\\'):
            before_d += " \\"
        modified_cmd = before_d + "\n" + auth_line + "\n" + after_d
    else:
        lines = curl_cmd.strip().split('\n')
        for i, line in enumerate(lines):
            if "-H 'accept: application/json'" in line:
                lines.insert(i + 1, auth_line)
                break
        modified_cmd = '\n'.join(lines)

    bb.append(modified_cmd)


user_one_token_for_permission_check = ""

for curl in bb:
    result = run_curl(curl)
    if result:
        try:
            token = json.loads(result).get("token")
            if token:
                user_one_token_for_permission_check = token
        except json.JSONDecodeError:
            print("[경고] JSON 파싱 실패:", result)


curl_list_need_token_no_premission = [
'''#새로운 유저 등록 실패 (권한 없음)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/1/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#유저 삭제 실패 (권한 없음)\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Crew/1/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#게시물 수정 실패 (권한없음)\n
    curl -X 'PUT' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "title": "string",
  "content": "string",
  "when": "string",
  "where": "string"
}' ''',
'''#게시물 삭제 실패 (권한없음)\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#crew탈퇴 성공 \n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Crew/1/Me' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\ ''',
'''#user탈퇴 성공 \n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/User/Me' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\ ''',
'''#match 생성 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Match/Duel/' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "title": "string",
    "content": "string",
    "when": "string",
    "where": "string",
    "request_crew_id": 1,
    "opponent_crew_name": "string"
}' ''',
'''#match 수락 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Match/Accept/' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "match_id": 3,
  "accept_crew_id": 1
}' ''',
'''#match 삭제 성공\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Match/1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "match_id": 3,
  "accept_crew_id": 1
}' ''',

]

curl_list_have_token_no_premission = []

for curl_cmd in curl_list_need_token_no_premission:
    auth_line = f"-H 'Authorization: Bearer {user_one_token_for_permission_check}' \\"

    if "-d '" in curl_cmd:
        parts = curl_cmd.split("-d '", 1)
        before_d = parts[0].rstrip()
        after_d = "-d '" + parts[1]
        if not before_d.strip().endswith('\\'):
            before_d += " \\"
        modified_cmd = before_d + "\n" + auth_line + "\n" + after_d
    else:
        lines = curl_cmd.strip().split('\n')
        for i, line in enumerate(lines):
            if "-H 'accept: application/json'" in line:
                lines.insert(i + 1, auth_line)
                break
        modified_cmd = '\n'.join(lines)

    curl_list_have_token_no_premission.append(modified_cmd)

for curl in curl_list_have_token_no_premission:
    result = run_curl(curl)



"""


    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcl9uYW1lIjoiTm9QZXJtaXNzaW9uIiwiZXhwIjoxNzQ5MzI3MTI5fQ.nfGNhark2sFmTbKcZ5WKG3TlRAeDjRmHCmCS4stA2Bc' \

    


curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Crew/Member?crew_id=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcl9uYW1lIjoiTm9QZXJtaXNzaW9uIiwiZXhwIjoxNzQ5MzI3MTI5fQ.nfGNhark2sFmTbKcZ5WKG3TlRAeDjRmHCmCS4stA2Bc' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}'


curl -X POST \
  'http://127.0.0.1:8000/KU/Crew/Leader/Member' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MiwidXNlcl9uYW1lIjoic3RyaW5nIiwiZXhwIjoxNzQ5MzI3NzQ4fQ.UMeUYgK7zZtDa_xWuv3HCWhXsifT8GFpghKNHS9aR64' \
  -d '{
    "e_mail": "@23"
  }'

    curl -X 'POST' \
    'http://127.0.0.1:8000/KU/User/SignIn' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{
    "e_mail": "string",
    "password": "string"
}' '''






curl -X 'GET' \
    'http://127.0.0.1:8000/KU/User/MyProfile' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcl9uYW1lIjoic3RyaW5nIiwiZXhwIjoxNzQ5MzMwODcxfQ.zWbJ2Fj2Aeii1DDcAaPODxICIe4BmRKGgjI6DHC-9Bc' \
    -d '{
    "crew_name": "test",
    "description": "string"
    }'     
curl -X 'DELETE' \
    'http://127.0.0.1:8000/KU/Crew/Leader?crew_id=1' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcl9uYW1lIjoic3RyaW5nIiwiZXhwIjoxNzQ5MzMwODcxfQ.zWbJ2Fj2Aeii1DDcAaPODxICIe4BmRKGgjI6DHC-9Bc' \
    -d '{
    "crew_name": "test",
    "description": "string"
    }' 
curl -X 'GET' \
    'http://127.0.0.1:8000/KU/User/MyProfile' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcl9uYW1lIjoic3RyaW5nIiwiZXhwIjoxNzQ5MzMxMjc2fQ.ZG_W_hugZngSWwF2fdRRbnLfOtyhOGQaIcCXG8ZL8IY' \
    -d '{
    "crew_name": "test",
    "description": "string"
    }' 
    

curl -X 'DELETE' \
    'http://127.0.0.1:8000/KU/Match/1' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwidXNlcl9uYW1lIjoic3RyaW5nIiwicGFzc3dvcmRfdmVyaWZpZWQiOnRydWUsImV4cCI6MTc0OTM4ODYyN30.5spQ5jbv90M2sMnoMaKutPIZ32tbjRzGUygnmBnHshw' \
    -d '{
  "e_mail": "string",
  "password" : "string"
}'



"""