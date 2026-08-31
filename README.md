# 포모도로 + 할일 트래커

집중 시간과 할 일을 함께 관리하는 앱입니다. 두 가지 버전으로 제공됩니다.

- `index.html` — 정적 HTML 버전 (설치 없이 브라우저에서 바로 실행)
- `app.py` — Streamlit 버전 (Streamlit Community Cloud 등에 배포 가능)

## 기능

- **포모도로 타이머**: 집중(25분) / 짧은 휴식(5분) / 긴 휴식(15분) 모드 전환
- **할 일 목록**: 할 일 추가, 완료 처리, 삭제
- **집중 대상 지정**: 할 일을 집중 대상으로 지정하면, 완료된 뽀모도로가 해당 항목에 기록됩니다
- **통계**: 오늘 완료한 뽀모도로 수, 이번 주 완료 수, 연속 달성일(스트릭)

## 실행 방법

### HTML 버전

`index.html` 파일을 웹 브라우저로 열면 바로 사용할 수 있습니다. 진행 상황은 브라우저의 `localStorage`에 저장됩니다.

### Streamlit 버전

```bash
pip install -r requirements.txt
streamlit run app.py
```

진행 상황은 브라우저 세션 동안만 유지됩니다(서버 재시작 시 초기화).

## 기술 스택

- HTML 버전: 순수 HTML / CSS / JavaScript (외부 라이브러리 없음)
- Streamlit 버전: Python, [Streamlit](https://streamlit.io), [streamlit-autorefresh](https://pypi.org/project/streamlit-autorefresh/)
