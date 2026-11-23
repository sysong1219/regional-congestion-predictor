import streamlit as st

st.set_page_config(page_title="전국 시간별 예상 혼잡도 가이드", page_icon="🗺️")

st.title("🗺️ 전국 시간별 예상 혼잡도 가이드")
st.write("지역, 시간, 요일 유형(평일/휴일/연휴)을 선택하면 예상 혼잡도와 시간대별 추이를 안내해 드립니다.")
st.divider()

# 혼잡도 점수 계산 함수
def calculate_congestion(region, hour, day_type):
    # 1. 시간대별 기본 점수 (평일 / 휴일 / 연휴 구분)
    if day_type == "평일":
        if 0 <= hour <= 5:
            base_score = 15
        elif 6 <= hour <= 9:
            base_score = 65
        elif 10 <= hour <= 11:
            base_score = 50
        elif 12 <= hour <= 13:
            base_score = 75
        elif 14 <= hour <= 17:
            base_score = 60
        elif 18 <= hour <= 20:
            base_score = 80
        else:
            base_score = 40

    elif day_type == "휴일":
        if 0 <= hour <= 5:
            base_score = 15
        elif 6 <= hour <= 9:
            base_score = 25
        elif 10 <= hour <= 11:
            base_score = 50
        elif 12 <= hour <= 13:
            base_score = 65
        elif 14 <= hour <= 17:
            base_score = 80
        elif 18 <= hour <= 20:
            base_score = 75
        else:
            base_score = 50

    else:  # "연휴"
        if 0 <= hour <= 5:
            base_score = 25   # 심야 귀성·귀경 차량 이동 반영
        elif 6 <= hour <= 9:
            base_score = 45   # 이른 아침 출발 인파
        elif 10 <= hour <= 11:
            base_score = 70
        elif 12 <= hour <= 13:
            base_score = 80
        elif 14 <= hour <= 17:
            base_score = 85   # 연휴 낮 시간대 이동 및 관광 피크
        elif 18 <= hour <= 20:
            base_score = 80
        else:
            base_score = 60

    # 2. 지역 및 요일별 특성 가중치 적용
    region_weight = 0
    if day_type == "연휴":
        if region == "서울":
            region_weight = -10  # 연휴 기간 서울 인구 유출(도심 한산) 반영
        elif region in ["강원", "제주"]:
            region_weight = 20   # 연휴 기간 대표 관광지 극심한 혼잡
        elif region in ["충청", "전라", "경상"]:
            region_weight = 15   # 귀성·귀경 인파 집중
        else:  # 경기 및 광역시
            region_weight = 5
    else:
        if region == "서울":
            region_weight = 15 if day_type == "평일" else 10
        elif region == "경기":
            region_weight = 12 if day_type == "평일" else 8
        elif region in ["인천", "부산", "대구", "대전", "광주", "울산"]:
            region_weight = 6 if day_type == "평일" else 8
        elif region in ["강원", "제주"]:
            if day_type == "휴일" and 11 <= hour <= 19:
                region_weight = 15
            elif day_type == "평일":
                region_weight = -10
        else:  # 충청, 전라, 경상
            region_weight = 0 if day_type == "평일" else 5

    # 3. 심야 시간대(00시~05시) 감점 기준
    if 0 <= hour <= 5:
        region_weight -= 10  # 대중교통 종료 및 취침 시간대 반영

    return max(5, min(100, base_score + region_weight))

def get_status(score):
    if score >= 75:
        return "혼잡"
    elif score >= 45:
        return "보통"
    else:
        return "원활"

# 지역 목록
regions = ["서울", "경기", "인천", "부산", "대구", "대전", "광주", "울산", "강원", "충청", "전라", "경상", "제주"]

col1, col2, col3 = st.columns(3)
with col1:
    region = st.selectbox("📍 지역 선택", regions)
with col2:
    hour = st.selectbox("⏰ 시간 선택", list(range(24)), format_func=lambda x: f"{x:02d}시", index=14)
with col3:
    day_type = st.radio("📅 평일 / 휴일 / 연휴", ["평일", "휴일", "연휴"])

st.write("")

if st.button("예상 혼잡도 조회하기", type="primary", use_container_width=True):
    current_score = calculate_congestion(region, hour, day_type)
    current_status = get_status(current_score)

    st.divider()

    # 1. 현재 '혼잡'인 경우 -> 몇 시간 더 혼잡이 지속될지 계산
    if current_status == "혼잡":
        duration = 0
        for i in range(1, 13):
            next_hour = (hour + i) % 24
            next_score = calculate_congestion(region, next_hour, day_type)
            if get_status(next_score) == "혼잡":
                duration += 1
            else:
                break

        if duration > 0:
            trend_msg = f"앞으로 **{duration}시간** 더 혼잡할 예정입니다."
        else:
            trend_msg = "다음 시간부터는 혼잡이 완화될 예정입니다."

        st.error(f"""
        ### {region}의 {hour}시 예상 상황은 **'{current_status}'**입니다.
        - **예상 혼잡도 점수:** {current_score}점입니다.
        - **예상 추이:** {trend_msg}
        """)

    # 2. 현재 '원활' 또는 '보통'인 경우 -> 몇 시간 후에 혼잡해질지 계산
    else:
        hours_until_congestion = None
        for i in range(1, 24):
            next_hour = (hour + i) % 24
            next_score = calculate_congestion(region, next_hour, day_type)
            if get_status(next_score) == "혼잡":
                hours_until_congestion = i
                break

        if hours_until_congestion is not None:
            trend_msg = f"**{hours_until_congestion}시간 후**에 혼잡해질 예정입니다."
        else:
            trend_msg = "당분간 혼잡해질 예정이 없습니다."

        result_text = f"""
        ### {region}의 {hour}시 예상 상황은 **'{current_status}'**입니다.
        - **예상 혼잡도 점수:** {current_score}점입니다.
        - **예상 추이:** {trend_msg}
        """

        if current_status == "보통":
            st.warning(result_text)
        else:
            st.success(result_text)
