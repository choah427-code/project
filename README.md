# 🌃 서울 나이트 스팟 (Seoul Night Spot)

> 예쁜 곳보다 **지금 가기 좋은 곳**을 추천합니다.

서울시 야경명소 51개소의 혼잡도·운영시간·요금·주차 정보를 한눈에 확인하는 다크모드 지도 웹 서비스입니다.

## 🚀 실행 방법

### 로컬 실행
```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/seoul-nightspot.git
cd seoul-nightspot

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 앱 실행
streamlit run app.py
```

## 📁 폴더 구조

```
seoul-nightspot/
├── app.py                  # Streamlit 메인 앱
├── requirements.txt        # 패키지 목록
├── README.md
└── data/
    └── seoul_nightspot.csv # 서울시 야경명소 정보 (51개소)
```

## 🌐 Streamlit Cloud 배포

1. 이 저장소를 GitHub에 Push
2. [share.streamlit.io](https://share.streamlit.io) 접속 후 GitHub 로그인
3. **New app** → 저장소 선택 → `app.py` 선택 → **Deploy**

## 📊 데이터 출처

- 서울시 야경명소 정보 — [서울 열린데이터광장](https://data.seoul.go.kr)
- 혼잡도 데이터 — 서울시 실시간 인구데이터 API (현재 버전은 시뮬레이션)

## 🛠️ 주요 기능

| 기능 | 설명 |
|------|------|
| 🗺️ 다크 지도 | CartoDB 다크 타일 기반 야경 명소 시각화 |
| 🟢🟡🔴 혼잡도 | 여유/보통/붐빔 색상 마커 표시 |
| 🔍 필터 | 혼잡도·분류·요금·주차 조건 필터링 |
| 📋 목록 | 정렬 및 요약 카드 |
| 🔎 상세 정보 | 주소·운영시간·교통·주차 전체 정보 |

## 📌 향후 계획 (Phase 2~3)

- 서울시 실시간 인구 API 실 연동
- 대체 장소 자동 추천 알고리즘
- 날씨·미세먼지 데이터 연동
