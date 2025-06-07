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


curl_list_need_token = [
###User
'''#로그인 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/Verify-password' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "password" : "12@3"
    }' ''',
'''#비밀번호 확인 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/Verify-password' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "password" : "123"
    }' ''',
'''#내 프로필 보기\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/MyProfile' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#내 프로필 변경\n
    curl -X 'PUT' \\
    'http://127.0.0.1:8000/KU/User/Profile' \\
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
    'http://127.0.0.1:8000/KU/User/Profile?user_id=222' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#다른 유저 검색 성공 \n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/Profile?user_id=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
###Crew
'''#모임 생성 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/NewCrew' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "crew_name": "string",
    "description": "string"
    }' ''',
'''#내 프로필 보기 (crew변화 보기)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/MyProfile' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#모임 생성 실패 (이미 있는 이름)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/NewCrew' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
    "crew_name": "string",
    "description": "string"
    }' ''',
'''#모임 정보 검색 실패 (없는 id)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Crew/Profile?crew_id=122' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#모임 정보 검색 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Crew/Profile?crew_id=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#새로운 유저 등록 성공\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#새로운 유저 등록 성공\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/User/Profile?user_id=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#모임 정보 검색 성공(새로운 유저 반영 확인)\n
    curl -X 'GET' \\
    'http://127.0.0.1:8000/KU/Crew/Profile?crew_id=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    ''',
'''#새로운 유저 등록 실패(이미 있는 유저)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#새로운 유저 등록 실패(없는 유저)\n
    curl -X 'POST' \\
    'http://127.0.0.1:8000/KU/Crew/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korr"
}' ''',
'''#유저 삭제 성공\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Crew/Member' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    -d '{
  "e_mail": "shinheewon@korea.ac.kr"
}' ''',
'''#유저 삭제 실패(없는 유저)\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Crew/Member' \\
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
'''#게시물 삭제 실패 (권한없음)\n
    curl -X 'DELETE' \\
    'http://127.0.0.1:8000/KU/Post/?post_num=1' \\
    -H 'accept: application/json' \\
    -H 'Content-Type: application/json' \\
    '''
    
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

