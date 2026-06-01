import os
import requests
import xml.etree.ElementTree as ET

# 1. 환경변수에서 정보 불러오기 (보안을 위해 코드에 직접 입력하지 않음)
API_KEY = os.environ.get("API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def fetch_volunteer_data(keyword):
    """API를 호출하여 청소년 가능 봉사활동 상위 데이터를 가져옵니다."""
    url = "https://apis.data.go.kr/1741000/volunteerPartcptnService/getVltrPartcptnItem"
    params = {
        'serviceKey': API_KEY,
        'numOfRows': '20',
        'pageNo': '1',
        'keyword': keyword
    }
    try:
        response = requests.get(url, params=params)
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        data = []
        for item in items:
            yngbgs = item.find('yngbgsPosblAt')
            # 청소년 참여 가능한 활동(Y)만 수집
            if yngbgs is not None and yngbgs.text == 'Y':
                data.append({
                    "title": item.find('progrmSj').text,
                    "region": item.find('nanmmbyNm').text,
                    "date": f"{item.find('progrmBgnde').text} ~ {item.find('progrmEndde').text}",
                    "url": f"https://www.1365.go.kr/vols/1572247904127/partcptn/timeCptn.do?type=show&progrmRegistNo={item.find('progrmRegistNo').text}"
                })
        return data
    except Exception as e:
        print(f"[{keyword}] API 호출 오류: {e}")
        return []

def send_telegram_message(text):
    """텔레그램 봇을 통해 메시지를 전송합니다."""
    # 환경변수가 제대로 설정되지 않았을 경우를 대비한 안전장치
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("텔레그램 토큰이나 CHAT ID가 환경변수에 설정되지 않았습니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("텔레그램 알림 전송 성공!")
    else:
        print(f"전송 실패: {response.text}")

if __name__ == "__main__":
    regions = ["순천", "광양", "진주"]
    all_results = []
    
    for r in regions:
        all_results.extend(fetch_volunteer_data(r))

    if all_results:
        msg = "🔔 <b>오늘의 1365 청소년 자원봉사 알림</b>\n\n"
        
        for item in all_results[:5]: # 최대 5개만 전송
            msg += f"📍 <b>[{item['region']}]</b> {item['title']}\n"
            msg += f"📅 기간: {item['date']}\n"
            msg += f"🔗 <a href='{item['url']}'>상세보기</a>\n\n"
        
        if len(all_results) > 5:
            msg += f"<i>...외 {len(all_results)-5}건의 봉사가 더 있습니다.</i>"
            
        send_telegram_message(msg)
    else:
        print("조건에 맞는 새로운 봉사활동이 없습니다.")
