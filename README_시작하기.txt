D& 인테리어 사이트 V15 (관리자 모드 + 마케팅 연동 틀 포함)

■ 지금 상태
- 사이트는 그대로 올려서 쓸 수 있습니다. (폴더째 Vercel에 업로드)
- /admin 주소는 아직 로그인이 안 됩니다. 아래 "승인 후 연결"을 하면 켜집니다.

■ 승인 후 연결 (한 번만, 약 20분)
1. GitHub에 새 저장소(repository)를 만들고 이 폴더 전체를 올립니다.
2. Vercel에서 그 저장소를 Import 해서 배포합니다. (Build Command 비움, Output Directory 비움)
3. GitHub > Settings > Developer settings > OAuth Apps > New OAuth App
   - Homepage URL: https://사이트주소
   - Authorization callback URL: https://사이트주소/api/callback
   발급된 Client ID, Client Secret 을 복사합니다.
4. Vercel > Project > Settings > Environment Variables 에 추가
   GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, SITE_ORIGIN(=https://사이트주소) → Redeploy
5. admin/config.yml 맨 위 repo(저장소 이름), base_url, site_url(사이트 주소) 3곳을 실제 값으로 수정해 저장소에 올립니다.
6. https://사이트주소/admin 접속 → GitHub로 로그인
   (저장소에 Collaborator로 초대된 사람만 수정할 수 있습니다. 형님 계정을 초대하세요.)

■ 관리자에서 수정하는 방법
- 왼쪽 메뉴에서 ① 기본 정보 ② 페이지별 문구·사진 ③ 시공 사례·디자인 제안 사진 을 고르고,
  문구를 고치거나 사진 칸에서 사진을 올린 뒤 [발행하기]를 누르면 끝.
- 발행 후 약 1~2분 뒤 사이트에 반영됩니다. (자동으로 페이지를 다시 만들고 배포)
- 시공 사례 추가/삭제, 디자인 제안 추가/삭제(상세 페이지 자동 생성), 연락처, 공정표, FAQ, 업체 정보까지 전부 수정됩니다.
- 사진은 가로 1600px 이상, 용량 500KB~1MB 이하 JPG/WebP를 권장합니다.

■ 폴더 설명 (건드릴 필요 없음)
- content/ : 모든 문구 데이터 (관리자가 여기를 수정)
- gen.py : 데이터를 보고 페이지를 만드는 프로그램 (저장 시 GitHub이 자동 실행)
- admin/ : 관리자 화면 설정
- api/ : 로그인 처리
- assets/ : 디자인 파일과 사진

■ 직접 수정하고 싶을 때 (관리자 없이)
- content/*.json 을 고친 뒤 `python3 gen.py` 실행하면 HTML이 다시 만들어집니다.
- 연습용: 컴퓨터에서 `npx decap-server` 실행 + admin/config.yml 의 local_backend 주석 해제 → 로그인 없이 /admin 체험


■ 값을 넣으면 화면에 나타나는 항목 (비어 있으면 사이트에 표시되지 않음)
- 시공 전/후 슬라이더 : 시공 사례 > 시공 전/후 사진 쌍
- 고객 후기 : 홈 후기 항목 (실제 후기와 사용 동의가 있을 때만 입력, 이름은 가려서 표기)
- 외부 후기 링크 버튼 : 기본 정보 > 외부 후기 링크 (네이버 플레이스·블로그·구글 리뷰 주소)
- 자재 갤러리 : 홈 자재 항목
- 규모별(평형) 필터 : 사례마다 규모 태그를 넣으면 나타남
- 영상 / 블로그 글 링크 : 사례별 항목
- 유튜브 / 핀터레스트 링크 : 기본 정보 (푸터에 표시)

■ 마케팅 연동 (도메인 연결 후)
1. 기본 정보 > 공개 홈페이지 주소(site_url)에 https://도메인 입력 (canonical, sitemap, robots 자동 생성)
2. 메타 이벤트 관리자에서 픽셀을 만들고, 숫자 ID를 기본 정보 > 메타 픽셀 ID에 입력
   - 모든 페이지 방문(PageView), 견적 폼 제출(Lead), 전화·문자 클릭(Contact)이 자동 기록됩니다.
3. 메타 비즈니스 관리자 > 도메인 인증에서 받은 코드를 기본 정보 > 메타 도메인 인증 코드에 입력
4. 방문자 데이터를 수집하므로 개인정보처리방침 페이지를 사이트에 두는 것을 권장합니다.

■ 사진 안내
- 홈/포트폴리오는 assets/images/case1.jpg ~ case3.jpg (신주옥미 의정부점)가 있으면 자동 표시, 없으면 숨김 처리됩니다.
- 사진은 WebP 변환 후 넣는 것을 권장합니다. (용량·속도)
