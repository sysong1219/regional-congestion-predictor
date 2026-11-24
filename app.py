import streamlit as st

st.title("청소년 개인 카페인 복용량 추천")

# 체중 입력
weight = st.number_input(
    "체중 입력 (kg)",
    min_value=30.0,
    max_value=130.0,
    value=50.0,
    step=1.0
)

# 음료 리스트
drinks = [
    ("커피", 150),
    ("핫식스", 100),
    ("스누피", 240)
]

# 분석 버튼
if st.button("분석하기 →"):

    # 카페인 계산
    amount = weight * 2.5

    st.subheader("분석 결과")
    st.write(f"계산 기준값은 {amount:.1f}mg입니다.")

    # 선택문
    if amount < 100:
        st.warning("카페인 복용을 추천하지 않습니다.")

    # 음료 결과 리스트
    results = []

    # 반복문
    for name, caffeine in drinks:

        if caffeine > amount:
            result = "기준 초과"
        else:
            result = "기준 이하"

        results.append({
            "음료": name,
            "카페인 함량": f"{caffeine}mg",
            "판정": result
        })

    # 표 출력
    st.subheader("카페인 음료 비교")
    st.table(results)

    st.caption("※ 학습용 계산 결과이며 실제 섭취 권장량이 아닙니다.")

       
