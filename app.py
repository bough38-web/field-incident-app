import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import re
import io

st.set_page_config(page_title="사건사고 통합 관리 시스템", page_icon="🏢", layout="wide")

# ==========================================
# 1. 상태 관리 및 비밀번호 설정
# ==========================================
if "app_passwords" not in st.session_state:
    st.session_state.app_passwords = {
        "user_pw": "1234",
        "hq_pw": "admin1234!!",
        "branch_pws": {
            "중앙": "wnddkd1234",
            "강북": "rkdqnr1234",
            "서대문": "tjeoans1234",
            "고양": "rhdid1234",
            "의정부": "dmlwjdqn1234",
            "남양주": "skadiddwn1234",
            "강릉": "rkdfmd1234",
            "원주": "dnjswn1234"
        }
    }

if "incidents_db" not in st.session_state:
    st.session_state.incidents_db = [
        {
            "id": "INC-001", "branch": "강북", "incident_type": "고객사고(도난)", "status": "접수", 
            "created_by": "SG 정석민 / 101호", "service_no": "봉봉스테이션 노원점 (63256647)", "reported_time": "04:23", 
            "reported_at": "2026-03-05 06:15:00", "media_files": [],
            "description_full": "[도난사고 - GiGAeyes Guard]\n[피해내용]\n- 1만원권 : 1,100,000원\n- 1천원권 : 709,000원\n- 피해 금액 : 1,809,000원\n[조치내용]\n- 관제 진행 상황 고객 및 관제센터 보고\n- 고객 동의 하에 경찰 영상 촬영 진행\n- 방범장비 이상 없음 확인\n[조치예정]\n- 영상 백업 요청\n- USB 미소지로 인한 재방문 예정\n\n[발생경위]\n04:23 자석감지기 최초 신호 발생\n04:26 관제센터 착신, 영상관제 결과 도난 정황 확인\n04:31 경찰관과 동시 현장 도착, 도난 발생 확인\n06:29 관제센터 최종 보고 후 상황 종료"
        },
        {
            "id": "INC-002", "branch": "서대문", "incident_type": "차량사고", "status": "해결완료", 
            "created_by": "김무열", "service_no": "경기안양 사9975 (출동 203호)", "reported_time": "26년02월26일 18시 35분경", 
            "reported_at": "2026-03-04 10:20:00", "media_files": [],
            "description_full": "[차량사고]\n- 형태: 가해 / 보험: 접수 완료\n- 상대차량 피해: 앞범퍼 깨짐\n- 회사차량 피해: 출동오토바이 좌측 바디커버 및 이너커버 까짐\n[조치내용]\n- 사진촬영 및 보험사 대물 접수\n- 관제보고 및 oss등록\n\n[발생경위]\n효성-NH5C11 출동 처리 후 키렌탈 a/s 방문 이동을 위해 진입금지 도로로 주행중 좌회전중인 차량과 부딪힘 사고"
        },
        {
            "id": "INC-003", "branch": "고양", "incident_type": "고객사고(침수)", "status": "해결완료", 
            "created_by": "301호 장동원", "service_no": "(주)다성아이앤에스 (63527874)", "reported_time": "26.01.18 11:38", 
            "reported_at": "2026-02-28 14:15:00", "media_files": [],
            "description_full": "[침수사고 - ktt oct가드 (nvr)]\n- 보험: 일반형A\n- 신호내역: 11:38 침입(4번) 자석 신호 발생\n- 피해: 바닥에 있던 박스 자제 젖음\n- 장비손실: 없음\n[조치내용]\n- 고객 대면 후 보고 완료\n- 영상 촬영완료, 관제보고, 텔레캅장비 손실없음 확인\n\n[발생경위]\n11:38 출동지령으로 출동\n12:02 도착 후 경계 해제 후 출입\n12:03 현장 누수 확인 및 긴급통보\n12:05 계량기 물 잠금 및 박스 안전한 곳 이동"
        },
        {
            "id": "INC-004", "branch": "의정부", "incident_type": "고객사고(화재)", "status": "진행중", 
            "created_by": "포천 505호 양용주", "service_no": "제이라인디자인산업 (61680495)", "reported_time": "2026년 02월 27일 04시 12분", 
            "reported_at": "2026-03-05 05:20:00", "media_files": [],
            "description_full": "[고객사고(화재)]\n- 지령일시: 26.02.27 04:12\n- 도착시간: 04:30\n- 소요시간: 18분\n- 인명피해: 없음\n- 대물피해: 사업장 건물 전소 및 화재진압 중\n[조치내용]\n- 화재 진행확인 및 소방차, 경찰차 출동 후 화재진압 중\n- 도로 통제 및 사업장 화재로 내부 진입불가 관제 보고\n- 고객 소방관, 경찰 상담중 간략 대면상담 후 철수\n\n[고객연락처] 010-2100-4813\n[발생경위]\n긴급 2순위 고객통화 완료. 화재사진 첨부 대기중."
        },
        {
            "id": "INC-005", "branch": "중앙", "incident_type": "안전사고(단독)", "status": "접수", 
            "created_by": "송민규 (안전요원)", "service_no": "종합상황실 내부", "reported_time": "2026년 03월 05일 08:30분경", 
            "reported_at": "2026-03-05 08:45:00", "media_files": [],
            "description_full": "[안전사고]\n- 부상내용: 좌측 발목 염좌 및 찰과상\n- 병원방문: 예정/진행중\n[조치내용]\n- 응급 키트로 지혈 조치 완료 후 대기\n- 근처 정형외과 엑스레이 검사 이동 예정\n\n[발생경위]\n순찰 업무 중 계단 논슬립 마감 패드 탈락으로 인해 미끄러지면서 발목을 접지름. 상황실 내 구급상자로 1차 조치함."
        }
    ]

# 페이지 라우팅 제어 ('landing', 'user', 'admin')
if "current_page" not in st.session_state:
    st.session_state.current_page = "landing"
if "auth_status" not in st.session_state:
    st.session_state.auth_status = False
if "admin_role" not in st.session_state:
    st.session_state.admin_role = None

def go_home():
    st.session_state.current_page = "landing"
    st.session_state.auth_status = False
    st.session_state.admin_role = None

# ==========================================
# 2. 컴포넌트 함수 정의
# ==========================================

def landing_page():
    # 모바일 최적화를 위한 커스텀 CSS 강제 주입
    st.markdown("""
        <style>
        /* 기본적으로 Streamlit 앱 요소 여백 최소화 */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        /* 랜딩 박스들 반응형 CSS */
        .landing-box {
            padding: 1.5rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 1rem;
        }
        .user-box {
            background-color: #F3F4F6;
            border-top: 5px solid #3B82F6;
        }
        .admin-box {
            background-color: #1F2937;
            border-top: 5px solid #10B981;
            color: white;
        }
        .admin-box p {
            color: #D1D5DB;
        }
        /* 모바일 사이즈에서 h1 타이틀 크기 조정 */
        @media (max-width: 640px) {
            h1 {
                font-size: 1.5rem !important;
            }
            .landing-box {
                padding: 1rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🏢 사건·사고 통합 관제 플랫폼</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>[지사/현장] 사건 등록 및 [본부/지사] 통계 모니터링을 위한 통합 포털입니다.</p>", unsafe_allow_html=True)
    st.write("")
    
    # 랜딩 박스들을 가로로 배치 (모바일에서는 Streamlit이 자동으로 세로 스태킹함)
    col1, col2 = st.columns(2)
    
    # 지사(사용자/현장) 로그인 박스
    with col1:
        st.markdown("""
        <div class='landing-box user-box'>
            <h2>📝 사건등록 (지사/현장)</h2>
            <p>현장 담당자, 출동 요원 전용 등록 페이지</p>
        </div>
        """, unsafe_allow_html=True)
        user_pw_input = st.text_input("접속 비밀번호 입력", type="password", key="pw_user", placeholder="지사용 웹페이지 암호 (1234)")
        if st.button("사건등록 접속하기", use_container_width=True, type="primary"):
            if user_pw_input == st.session_state.app_passwords["user_pw"]:
                st.session_state.auth_status = True
                st.session_state.current_page = "user"
                st.rerun()
            else:
                st.error("비밀번호가 일치하지 않습니다.", icon="🚨")
                
    # 관리자 (본부/지사) 로그인 박스
    with col2:
        st.markdown("""
        <div class='landing-box admin-box'>
            <h2 style='color: white;'>📊 대시보드 (모니터링)</h2>
            <p>사건 조회, 엑셀 다운로드 및 상태 관리</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        admin_role_select = st.selectbox("조회 권한(소속) 선택", ["본부 (전체 권한)", "중앙", "강북", "서대문", "고양", "의정부", "남양주", "강릉", "원주"])
        admin_pw_input = st.text_input("관리용 비밀번호 입력", type="password", key="pw_admin", placeholder="지사 담당자용 비밀번호 입력")
        
        if st.button("모니터링 대시보드 접속", use_container_width=True, type="secondary"):
            if admin_role_select == "본부 (전체 권한)":
                if admin_pw_input == st.session_state.app_passwords["hq_pw"]:
                    st.session_state.auth_status = True
                    st.session_state.admin_role = "본부"
                    st.session_state.current_page = "admin"
                    st.rerun()
                else:
                    st.error("본부 관리자 비밀번호가 일치하지 않습니다.", icon="🚨")
            else:
                expected_pw = st.session_state.app_passwords["branch_pws"].get(admin_role_select)
                if expected_pw and admin_pw_input == expected_pw:
                    st.session_state.auth_status = True
                    st.session_state.admin_role = admin_role_select
                    st.session_state.current_page = "admin"
                    st.rerun()
                else:
                    st.error(f"[{admin_role_select}지사] 관리자 비밀번호가 일치하지 않습니다.", icon="🚨")

def user_registration_page():
    col_nav1, col_nav2 = st.columns([8, 2])
    with col_nav1:
        st.header("📝 새로운 사건/사고 등록하기 (현장용)")
    with col_nav2:
        if st.button("🚪 메인으로 로그아웃", use_container_width=True):
            go_home()
            st.rerun()
            
    st.markdown("현장 담당자나 고객이 새로운 이슈를 시스템에 접수하는 화면입니다.")
    
    with st.form("incident_register_form", clear_on_submit=True):
        st.markdown("---")
        st.subheader("2. 미디어 첨부 (사진 및 동영상)")
        uploaded_media = st.file_uploader("사고 현장 사진 및 영상 (JPG, PNG, MP4, MOV)", type=['jpg', 'jpeg', 'png', 'mp4', 'mov'], accept_multiple_files=True)
        
        # --- 효율성 강화: 업로드 프리뷰 시각화 ---
        if uploaded_media:
            st.markdown("**📸 업로드 대기중인 미디어 미리보기**")
            preview_cols = st.columns(4)
            for i, f in enumerate(uploaded_media):
                with preview_cols[i % 4]:
                    if f.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                        st.image(f, use_container_width=True)
                    else:
                        st.info(f"🎥 {f.name}")
        # ----------------------------------------
        
        st.subheader("3. 기본 정보 입력")
        col1, col2 = st.columns(2)
        with col1:
            branch = st.selectbox("지사명*", ["중앙", "강북", "서대문", "고양", "의정부", "남양주", "강릉", "원주"])
            created_by = st.text_input("근무자/구역정보*", placeholder="예: 301호 장동원")
            incident_type = st.selectbox("사고유형*", ["차량사고", "고객사고(도난)", "고객사고(화재)", "고객사고(침수)", "고객사고(기타)", "안전사고(단독)"])
        with col2:
            service_no = st.text_input("고객정보(상호 및 서비스번호)*", placeholder="예: (주)다성아이앤에스 (63527874)")
            
            # --- 직관성 강화: 날짜 및 시간 선택 캘린더 도입 ---
            st.markdown("<p style='font-size: 14px; margin-bottom: 0px;'>사고발생(신호) 일시*</p>", unsafe_allow_html=True)
            col_dt1, col_dt2 = st.columns(2)
            with col_dt1:
                rep_date = st.date_input("사고일자", value=datetime.today().date(), label_visibility="collapsed")
            with col_dt2:
                rep_time = st.time_input("사고시간", value=datetime.now().time(), label_visibility="collapsed")
            reported_time = f"{rep_date.strftime('%y.%m.%d')} {rep_time.strftime('%H:%M')}"
            # ------------------------------------------------
            address = st.text_input("구역 / 발생 장소", placeholder="예: 301호")
            
        if incident_type == "차량사고":
            with st.expander("🚗 차량사고 추가 정보 입력창 (접기/펴기)", expanded=True):
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    vehicle_fault = st.radio("사고형태*", ["가해", "피해", "쌍방", "단독(알수없음)"], horizontal=True)
                    insurance_status = st.radio("보험 접수 유무*", ["접수 완료", "미접수", "현장 합의"], horizontal=True)
                with col_v2:
                    damage_my = st.text_input("회사차량 피해내용 (대인/대물)", placeholder="예: 대인:무, 대물:좌측 바디커버 까짐")
                    damage_other = st.text_input("상대차량 피해내용 (대인/대물)", placeholder="예: 대인:무, 대물:앞범퍼 깨짐")
                action_taken = st.text_area("조치내용*", placeholder="- 사진촬영 및 보험사 접수\n- 관제보고", height=100)
                
        elif incident_type == "고객사고(침수)":
            with st.expander("💧 고객사고(침수) 추가 정보 입력창 (접기/펴기)", expanded=True):
                col_w1, col_w2 = st.columns(2)
                with col_w1:
                    service_product = st.text_input("서비스상품", placeholder="예: ktt oct가드 (nvr)")
                    insurance_type = st.text_input("보험 구분", placeholder="예: 일반형A")
                with col_w2:
                    signal_details = st.text_input("신호내역 상세", placeholder="예: 11:38 침입(4번) 자석 신호 발생, 12:02 현장 도착")
                    equipment_loss = st.radio("텔레캅장비 손실유무", ["없음", "있음"], horizontal=True)
                    
                property_damage = st.text_input("피해내역", placeholder="예: 바닥에 있던 박스 자재 젖음")
                action_taken = st.text_area("점검 및 조치결과*", placeholder="- 고객 대면 후 보고 완료\n- 영상 촬영완료", height=100)

        elif incident_type == "고객사고(도난)":
            with st.expander("🕵️ 고객사고(도난) 추가 정보 입력창 (접기/펴기)", expanded=True):
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    service_product = st.text_input("가입상품", placeholder="예: GiGAeyes Guard")
                    stolen_amount = st.text_area("피해내용 (금액/물품)", placeholder="예: 1만원권 110만, 1천원권 70.9만. 총 1,809,000원", height=100)
                with col_t2:
                    action_taken = st.text_area("조치내용*", placeholder="- 경찰 영상 촬영 진행\n- 방범장비 이상 없음 확인", height=100)
                    future_action = st.text_area("조치예정", placeholder="- 영상 백업 요청\n- USB 지참 후 재방문 예정", height=100)

        elif incident_type.startswith("고객사고"):
            with st.expander(f"🔥 {incident_type} 추가 정보 입력창 (접기/펴기)", expanded=True):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    arrival_time = st.text_input("현장 도착시간", placeholder="예: 26년 02월 27일 04시 30분경")
                    casualties = st.radio("인명피해 유무", ["없음", "있음"], horizontal=True)
                    customer_contact = st.text_input("고객 연락처", placeholder="예: 010-2100-4813")
                with col_c2:
                    duration_time = st.text_input("현장 도착 소요시간", placeholder="예: 18분")
                    property_damage = st.text_input("재산(대물) 피해내용 유무", placeholder="예: 유 (사업장 건물 전소 등)")
                action_taken = st.text_area("조치내용*", placeholder="- 소방차, 경찰차 출동 후 현재 화재진압 중\n- 고객 소방관, 경찰이랑 상담중", height=150)
                
        elif incident_type == "안전사고(단독)":
            with st.expander("🤕 안전사고 추가 정보 입력창 (접기/펴기)", expanded=True):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    injury_details = st.text_input("부상 부위/내용", placeholder="예: 오른쪽 무릎 뒤틀림")
                with col_s2:
                    hospital_visit = st.radio("병원 후송/검사 여부", ["예정/진행중", "미방문", "완료"], horizontal=True)
                action_taken = st.text_area("조치내용*", placeholder="- 관제보고, 거점장 보고\n- 병원이동 후 엑스레이 촬영", height=100)
            
        st.markdown("---")
        st.subheader("4. 상세 내용 (발생경위)")
        description = st.text_area("발생경위*", placeholder="시간대별 현장 상황을 적어주세요\n...", height=150)
        
        submit_btn = st.form_submit_button("사건 접수하기 (데이터 전송)", use_container_width=True)
        
        if submit_btn:
            if not created_by or not branch or not description or not reported_time:
                st.error("지사명, 근무자, 사고발생 일시, 사고경위는 필수 입력값입니다.", icon="🚨")
            else:
                final_description = description
                if incident_type == "차량사고":
                    final_description = f"[차량사고]\n- 형태: {vehicle_fault} / 보험: {insurance_status}\n- 상대차량 피해: {damage_other}\n- 회사차량 피해: {damage_my}\n[조치내용]\n{action_taken}\n\n[발생경위]\n{description}"
                elif incident_type == "고객사고(침수)":
                    final_description = f"[침수사고 - {service_product}]\n- 보험: {insurance_type}\n- 신호내역: {signal_details}\n- 피해: {property_damage}\n- 장비손실: {equipment_loss}\n[조치내용]\n{action_taken}\n\n[발생경위]\n{description}"
                elif incident_type == "고객사고(도난)":
                    final_description = f"[도난사고 - {service_product}]\n[피해내용]\n{stolen_amount}\n[조치내용]\n{action_taken}\n[조치예정]\n{future_action}\n\n[발생경위]\n{description}"
                elif incident_type.startswith("고객사고"):
                    final_description = f"[{incident_type}]\n- 지령일시: {reported_time}\n- 도착시간: {arrival_time}\n- 소요시간: {duration_time}\n- 인명피해: {casualties}\n- 대물피해: {property_damage}\n[조치내용]\n{action_taken}\n\n[고객연락처] {customer_contact}\n[발생경위]\n{description}"
                elif incident_type == "안전사고(단독)":
                    final_description = f"[안전사고]\n- 부상내용: {injury_details}\n- 병원방문: {hospital_visit}\n[조치내용]\n{action_taken}\n\n[발생경위]\n{description}"
                
                # 파일 자동 폴더 저장 로직 (업로드데이터/본부또는지사/날짜_상호명)
                saved_files = []
                if uploaded_media:
                    base_dir = "업로드데이터"
                    date_str = datetime.now().strftime("%Y%m%d")
                    # 서비스번호(상호)에서 폴더명 생성 제약 문자 제거 및 공백을 언더스코어로 변환
                    safe_service_no = re.sub(r'[\\\\/*?:"<>|]', "", service_no).replace(" ", "_")
                    if not safe_service_no: safe_service_no = "기타상호"
                    # 예: 업로드데이터/고양/20260305_다성아이앤에스_63527874
                    save_dir = os.path.join(base_dir, branch, f"{date_str}_{safe_service_no}")
                    
                    os.makedirs(save_dir, exist_ok=True)
                    
                    for file in uploaded_media:
                        file_path = os.path.join(save_dir, file.name)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())
                        saved_files.append(file_path)

                # DB 저장 로직 수행
                new_id = f"INC-00{len(st.session_state.incidents_db) + 1}"
                new_incident = {
                    "id": new_id,
                    "branch": branch,
                    "incident_type": incident_type,
                    "status": "접수", 
                    "created_by": created_by,
                    "service_no": service_no,
                    "reported_time": reported_time,
                    "description_full": final_description, 
                    "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "media_files": saved_files
                }
                st.session_state.incidents_db.append(new_incident)
                
                st.success(f"성공적으로 접수되었습니다! (발급번호: {new_id})", icon="✅")
                if uploaded_media:
                    st.info(f"첨부된 미디어 {len(uploaded_media)}장이 로컬 폴더에 안전하게 자동 저장되었습니다: `{save_dir}`")

def admin_dashboard_page():
    # 상단 네비게이션
    current_role = st.session_state.admin_role
    
    col_nav1, col_nav2 = st.columns([8, 2])
    with col_nav1:
        if current_role == "본부":
            st.header("📊 관제 본부(전체) 모니터링 대시보드")
            st.success("🌐 **본부 모드:** 모든 지사의 사건을 열람 및 관리할 수 있습니다.")
        else:
            st.header(f"📊 {current_role}지사 전용 대시보드")
            st.warning(f"🔒 **{current_role}지사 제한 모드:** 소속 지사의 사건만 열람할 수 있습니다.")
            
    with col_nav2:
        if st.button("🚪 메인으로 로그아웃", use_container_width=True):
            go_home()
            st.rerun()
            
    # ------ 보안 설정 영역 ------
    with st.expander("🔑 비밀번호 계정 설정 및 초기화 모듈", expanded=False):
        if current_role == "본부":
            st.info("💡 **[본부 관리자 전용]** 모든 지사 관리자 및 사용자 비밀번호를 관리하고 분실 시 강제 초기화해줄 수 있습니다.")
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown("**본부 암호 변경**")
                new_hq_pw = st.text_input("새 본부 비밀번호", type="password", key="new_hq_pw")
                if st.button("본부 암호 업데이트"):
                    st.session_state.app_passwords["hq_pw"] = new_hq_pw
                    st.success("✅ 본부 비밀번호 변경 완료")
            with sc2:
                st.markdown("**지사 관리자 암호 초기화**")
                target_branch = st.selectbox("지사 선택", ["중앙", "강북", "서대문", "고양", "의정부", "남양주", "강릉", "원주"], key="target_b")
                new_branch_pw = st.text_input("새 지사 비밀번호", type="password", key="new_branch_pw")
                if st.button("해당 지사 설정 리셋"):
                    st.session_state.app_passwords["branch_pws"][target_branch] = new_branch_pw
                    st.success(f"✅ [{target_branch}] 관리자 계정 초기화 완료")
            with sc3:
                st.markdown("**사건등록(현장) 공통 암호 초기화**")
                new_user_pw = st.text_input("새 사용자 비밀번호", type="password", key="new_user_pw")
                if st.button("현장 암호 임의 설정"):
                    st.session_state.app_passwords["user_pw"] = new_user_pw
                    st.success("✅ 사용자 암호 초기화 완료! (직원에게 전달 요망)")
        else:
            st.info(f"💡 **[{current_role}지사 관리자 전용]** 본지 관리자 본인의 암호를 변경하거나, 소속 현장 사용자의 접속 암호를 초기화할 수 있습니다.")
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown("**지사 관리자 본인 암호 변경**")
                my_new_pw = st.text_input("지사 새 비밀번호", type="password", key="my_new_pw")
                if st.button("내 관리자 암호 업데이트"):
                    st.session_state.app_passwords["branch_pws"][current_role] = my_new_pw
                    st.success("✅ 내 지사 암호 변경 완료")
            with sc2:
                st.markdown("**사건등록(현장) 공통 암호 초기화**")
                new_user_pw_br = st.text_input("새 사용자 비밀번호", type="password", key="new_user_pw_br")
                if st.button("현장 암호 임의 설정"):
                    st.session_state.app_passwords["user_pw"] = new_user_pw_br
                    st.success("✅ 사용자 암호 초기화 완료! (직원에게 전달 요망)")
    # ----------------------------
            
    df = pd.DataFrame(st.session_state.incidents_db)
    
    # 본부 권한이 아닌 경우, 해당 지사 데이터만 필터링
    if current_role != "본부":
        df = df[df['branch'] == current_role]
    
    # 데이터가 비어있을 경우 에러 방지
    if df.empty:
        st.info("조건에 맞는 사건이 존재하지 않습니다.")
        return

    # KPIs
    st.markdown("---")
    colA, colB, colC = st.columns(3)
    with colA:
        st.metric(label="총 접수 건수", value=f"{len(df)}건")
    with colB:
        completed = len(df[df['status'] == '해결완료'])
        st.metric(label="조치 완료 건수", value=f"{completed}건")
    with colC:
        pending = len(df[df['status'].isin(['접수', '진행중'])])
        st.metric(label="현재 대응중/대기", value=f"{pending}건", delta_color="inverse")

    st.divider()

    # 차트영역
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("📍 지사별 보안 이벤트 현황")
        branch_counts = df['branch'].value_counts().reset_index()
        branch_counts.columns = ['지점', '건수']
        fig_branch = px.bar(branch_counts, x='지점', y='건수', color='지점', text='건수', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_branch.update_traces(textposition='outside')
        fig_branch.update_layout(showlegend=False, height=350, plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_branch, use_container_width=True)

    with col_c2:
        st.subheader("📈 사고 유형별 밀집도")
        type_counts = df['incident_type'].value_counts().reset_index()
        type_counts.columns = ['사고유형', '비율']
        fig_status = px.pie(type_counts, names='사고유형', values='비율', hole=0.5, color_discrete_sequence=px.colors.qualitative.Set3)
        fig_status.update_layout(height=350)
        st.plotly_chart(fig_status, use_container_width=True)

    st.divider()

    # 데이터 테이블 및 엑셀 다운로드 헤더
    col_tbl1, col_tbl2 = st.columns([8, 2])
    with col_tbl1:
        st.subheader("📋 실시간 사건 관제 모니터링 채널")

    # 필터 옵션
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        if current_role == "본부":
            branch_filter = st.multiselect("지사 필터링:", options=df["branch"].unique(), default=df["branch"].unique())
        else:
            # 지사 관리자는 필터링 변경 불가
            branch_filter = current_role
            st.multiselect("지사 필터링:", options=[current_role], default=[current_role], disabled=True)
            
    with col_f2:
        status_filter = st.multiselect("상태 필터링:", options=df["status"].unique(), default=df["status"].unique())
    with col_f3:
        type_filter = st.multiselect("사고유형 필터링:", options=df["incident_type"].unique(), default=df["incident_type"].unique())
        
    if current_role == "본부":
        filtered_df = df[(df["branch"].isin(branch_filter)) & (df["status"].isin(status_filter)) & (df["incident_type"].isin(type_filter))]
    else:
        filtered_df = df[(df["branch"] == branch_filter) & (df["status"].isin(status_filter)) & (df["incident_type"].isin(type_filter))]
    
    # 엑셀 다운로드 (우측 버튼)
    with col_tbl2:
        if not filtered_df.empty:
            buffer = io.BytesIO()
            # 누락된 컬럼에 대비해 기본값 채우기
            for col in ['id', 'reported_at', 'branch', 'incident_type', 'status', 'created_by', 'service_no', 'reported_time', 'description_full']:
                if col not in filtered_df.columns:
                    filtered_df[col] = "기록없음"
                    
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                export_df = filtered_df[['id', 'reported_at', 'branch', 'incident_type', 'status', 'created_by', 'service_no', 'reported_time', 'description_full']].copy()
                export_df.columns = ['접수번호', '전산 기록일', '지사명', '사고유형', '처리상태', '근무자/현장', '식별차량/고객번호', '실제 발생시간', '상세보고내역']
                export_df['현장사진'] = ""  # 사진이 들어갈 빈 공간
                export_df.to_excel(writer, index=False, sheet_name='사건접수내역')
                
                workbook = writer.book
                worksheet = writer.sheets['사건접수내역']
                
                # 엑셀 보기 좋게 너비 조정
                worksheet.column_dimensions['I'].width = 50  # 상세내역
                worksheet.column_dimensions['J'].width = 30  # 현장사진
                
                from openpyxl.drawing.image import Image as OpenpyxlImage
                from PIL import Image
                
                # 데이터 행별로 높이 조절 및 사진 삽입
                for r_idx, (_, row_data) in enumerate(filtered_df.iterrows(), start=2):
                    worksheet.row_dimensions[r_idx].height = 100  # 사진용 셀 높이 확보
                    
                    media_list = row_data.get('media_files', [])
                    if isinstance(media_list, list) and media_list:
                        for fpath in media_list:
                            ext = os.path.splitext(fpath)[1].lower()
                            if ext in ['.jpg', '.jpeg', '.png'] and os.path.exists(fpath):
                                try:
                                    # 사진 크기를 엑셀 셀 크기에 축소 및 최적화하여 삽입
                                    img = OpenpyxlImage(fpath)
                                    img.width = 180
                                    img.height = 130
                                    cell_ref = f"J{r_idx}"
                                    worksheet.add_image(img, cell_ref)
                                    break # 칸 크기를 위해 대표 사진 1장만 넣음
                                except Exception:
                                    pass
            
            st.write("") # 마진
            st.write("")
            st.download_button(
                label="📥 엑셀(Excel) 전송/다운",
                data=buffer.getvalue(),
                file_name=f"사건사고리포트_{current_role}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )

    display_df = filtered_df[['id', 'reported_at', 'branch', 'incident_type', 'status', 'created_by', 'service_no']].copy()
    display_df.columns = ['접수번호', '전산 접수일시', '지사명', '사고유형', '처리상태', '근무자/현장', '고객정보/차량번호']
    
    # === 동적 연동 핵심: 데이터 상태 직접 수정 (st.data_editor) ===
    st.markdown("**💡 팁:** 아래 표에서 `처리상태` 항목을 클릭하여 바로 상태를 **업데이트** 할 수 있습니다. (접수 → 진행중 → 해결완료)")
    edited_df = st.data_editor(
        display_df.iloc[::-1], 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "접수번호": st.column_config.TextColumn(disabled=True),
            "전산 접수일시": st.column_config.TextColumn(disabled=True),
            "지사명": st.column_config.TextColumn(disabled=True),
            "사고유형": st.column_config.TextColumn(disabled=True),
            "처리상태": st.column_config.SelectboxColumn("처리상태 (클릭하여 변경)", options=["접수", "진행중", "해결완료"], required=True),
            "근무자/현장": st.column_config.TextColumn(disabled=True),
            "고객정보/차량번호": st.column_config.TextColumn(disabled=True),
        },
        key="admin_data_editor"
    )
    
    # 상태 변경점 감지 및 DB(session_state) 업데이트 로직
    # st.data_editor 가 반환한 데이터프레임과 원본 DB를 비교하여 상태를 반영함
    # (주의: iloc[::-1] 로 역순 표시되었던 것을 감안해야 하므로 ID를 기준으로 매핑)
    if st.session_state.get('admin_data_editor') is not None:
        changed_rows = st.session_state.admin_data_editor.get("edited_rows", {})
        if changed_rows:
            for row_idx, changes in changed_rows.items():
                if "처리상태" in changes:
                    new_status = changes["처리상태"]
                    # edited_df에서 변경된 행의 접수번호(ID) 추출
                    target_id = edited_df.iloc[row_idx]['접수번호']
                    
                    # session_state DB 원본 업데이트
                    for item in st.session_state.incidents_db:
                        if item['id'] == target_id:
                            item['status'] = new_status
                            break
            # DB가 업데이트 되었으므로 UI를 리프레시하여 새 상태의 KPI/차트를 그림
            st.rerun()
    
    st.markdown("---")
    st.subheader("🔍 현장 정밀 보고 원문 (데이터 및 미디어 열람)")
    
    if not filtered_df.empty:
        selected_id = st.selectbox("상세 보고서를 열람할 접수번호(ID)를 선택하세요", options=filtered_df['id'].iloc[::-1].tolist())
        selected_row = filtered_df[filtered_df['id'] == selected_id].iloc[0]
        
        with st.container(border=True):
            st.markdown(f"### 🚨 [{selected_row['branch']}] {selected_row['incident_type']} (ID: {selected_row['id']})")
            
            # --- 효율성 강화: 원클릭 빠른 상태 변경 버튼 ---
            st.write("")
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                st.markdown("**⚡ 빠른 조치 상태 업데이트:**")
            with btn_col2:
                if st.button("🚀 '진행중' 처리", key="s_prog", use_container_width=True):
                    for item in st.session_state.incidents_db:
                        if item['id'] == selected_id:
                            item['status'] = "진행중"
                    st.rerun()
            with btn_col3:
                if st.button("✅ '해결완료' 종결", key="s_done", type="primary", use_container_width=True):
                    for item in st.session_state.incidents_db:
                        if item['id'] == selected_id:
                            item['status'] = "해결완료"
                    st.rerun()
            st.divider()
            
            st.markdown(f"**담당 현장 요원:** {selected_row['created_by']} &nbsp;&nbsp;|&nbsp;&nbsp; **현재 상태:** `{selected_row['status']}`")
            st.markdown(f"**식별 정보:** {selected_row['service_no']} &nbsp;&nbsp;|&nbsp;&nbsp; **사고/신호 일시:** {selected_row['reported_time']}")
            st.divider()
            
            detail_text = selected_row.get('description_full', '상세 내용이 접수되지 않았습니다.')
            st.text(detail_text) 
            
            # 미디어 출력 (사진, 동영상 작게 4개 칼럼으로 정렬)
            media_list = selected_row.get('media_files', [])
            if isinstance(media_list, list) and media_list:
                st.markdown("#### 📸 현장 첨부 미디어")
                img_cols = st.columns(4)
                col_idx = 0
                for fpath in media_list:
                    if os.path.exists(fpath):
                        ext = os.path.splitext(fpath)[1].lower()
                        with img_cols[col_idx % 4]:
                            if ext in ['.jpg', '.jpeg', '.png']:
                                st.image(fpath, use_container_width=True, caption=os.path.basename(fpath))
                            elif ext in ['.mp4', '.mov']:
                                st.video(fpath) # st.video는 width가 container_width에 맞춰짐
                        col_idx += 1
                    else:
                        st.warning(f"경로를 찾을 수 없음: {fpath}")
    else:
        st.info("조건에 맞는 사건이 없습니다.")


# ==========================================
# 3. 메인 라우터 실행
# ==========================================
if st.session_state.current_page == "landing":
    landing_page()
elif st.session_state.current_page == "user" and st.session_state.auth_status:
    user_registration_page()
elif st.session_state.current_page == "admin" and st.session_state.auth_status:
    admin_dashboard_page()
else:
    # 비정상 접근 시 랜딩으로
    go_home()
    st.rerun()
