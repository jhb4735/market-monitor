"""
2026년 일일 시장 지표 자동 모니터링 및 메일 발송 프로그램 (에러 수정 버전)
Daily Market Monitoring & Email Report System - FIXED

에러 수정:
- NoneType 오류 수정 (signal이 None인 경우 처리)
- 네트워크 오류 처리
- 데이터 누락 시 처리
"""

import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import traceback

# ============ 설정 섹션 (여기만 수정하면 됨) ============

GMAIL_USER = "jhb4735@gmail.com"  # 본인 Gmail 주소 입력
GMAIL_PASSWORD = "zzsa ejlr xnbp wspc"  # Gmail 앱 비밀번호 입력 (계정 비번 X)
RECIPIENT_EMAIL = "jhb4735@gmail.com"  # 받을 이메일 주소

SYMBOLS = {
    'S&P500': '^GSPC',
    'NASDAQ100': '^NDX',
    'VIX': '^VIX',
    'Gold': 'GC=F',
    'Bitcoin': 'BTC-USD',
    'KOSPI': '^KS11',
    'USD/KRW': 'USDKRW=X',
}

MY_STOCKS = {
    'Google': 'GOOGL',
    'Micron': 'MU',
    'UnitedHealth': 'UNH',
}

MY_ETFS = {
    'TIGER SP500': 'TIGER000230.KS',
    'TIGER NASDAQ100': 'TIGER000270.KS',
    'KODEX Semiconductor': 'KODEX000720.KS',
}

# ========================================================

class MarketMonitor:
    def __init__(self):
        self.today = datetime.now()
        self.report = []
        
    def get_stock_data(self, symbol):
        """주식 데이터 조회 (에러 처리 강화)"""
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='5d')
            
            if len(hist) < 2:
                return None
            
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            change_percent = ((current_price - prev_close) / prev_close) * 100
            
            return {
                'current': round(current_price, 2),
                'change': round(change_percent, 2),
                'prev_close': round(prev_close, 2)
            }
        except Exception as e:
            print(f"⚠️ {symbol} 데이터 오류: {str(e)}")
            return None
    
    def interpret_signal(self, value, metric_type):
        """신호 해석 (None 체크 추가)"""
        if value is None:
            return "⚠️ 데이터 오류", "데이터를 수집할 수 없습니다"
        
        try:
            if metric_type == 'vix':
                if value < 12:
                    return "🟢 안전영역", "정상 범위"
                elif value < 20:
                    return "🟢 정상", "정상 변동성"
                elif value < 25:
                    return "🟡 주의", "약간의 불안감"
                elif value < 30:
                    return "🟠 경고", "불안감 고조"
                else:
                    return "🔴 심각", "공포 신호"
            
            elif metric_type == 'sp500_change':
                if -2 <= value < 0:
                    return "🟡 주의", "소폭 조정"
                elif -5 <= value < -2:
                    return "🟠 경고", "약세 신호"
                elif value < -5:
                    return "🔴 심각", "본격 약세"
                elif value >= 0:
                    return "🟢 강세", "상승 추세"
            
            elif metric_type == 'won_rate':
                if value > 1500:
                    return "🔴 심각", "고환율 (달러자산 매수 중단)"
                elif value > 1480:
                    return "🟡 주의", "높은 환율"
                elif 1400 <= value <= 1480:
                    return "🟢 정상", "정상 범위"
                elif value < 1400:
                    return "🟢 기회", "저환율 (달러 매수 기회)"
            
            elif metric_type == 'gold':
                if value > 5000:
                    return "🟠 고가", "상반기 목표가 달성"
                elif value > 4800:
                    return "🟢 매수기회", "목표가 근처"
                elif value > 4500:
                    return "🟢 정상", "적정 가격"
                else:
                    return "🔴 심각", "절매 신호"
            
            elif metric_type == 'bitcoin':
                if value > 150000:
                    return "🟠 고가", "목표가 달성"
                elif value > 120000:
                    return "🟡 주의", "고가 영역"
                elif value > 100000:
                    return "🟢 매수기회", "기술적 지지선"
                else:
                    return "🔴 심각", "강제청산 신호"
        
        except Exception as e:
            print(f"해석 오류: {str(e)}")
            return "⚠️ 분석 오류", "신호를 분석할 수 없습니다"
    
    def generate_report(self):
        """일일 리포트 생성 (에러 처리 강화)"""
        self.report = []
        self.report.append("=" * 60)
        self.report.append(f"📊 2026년 일일 시장 모니터링 리포트")
        self.report.append(f"📅 {self.today.strftime('%Y년 %m월 %d일 (%A)')} ")
        self.report.append("=" * 60)
        self.report.append("")
        
        try:
            # 1. 주요 지수
            self.report.append("🌍 【 주요 글로벌 지수 】")
            self.report.append("-" * 60)
            
            for name, symbol in list(SYMBOLS.items())[:4]:
                data = self.get_stock_data(symbol)
                if data:
                    change = data['change']
                    arrow = "📈" if change >= 0 else "📉"
                    
                    # NoneType 에러 방지
                    metric_key = name.lower().replace(' ', '_')
                    signal = self.interpret_signal(change, metric_key)
                    
                    self.report.append(f"{arrow} {name}: {data['current']}")
                    self.report.append(f"   변화: {change:+.2f}% {signal[0]}")
                    self.report.append(f"   해석: {signal[1]}")
                else:
                    self.report.append(f"⚠️ {name}: 데이터 오류")
                self.report.append("")
            
            # 2. VIX 상세 분석
            vix_data = self.get_stock_data('^VIX')
            if vix_data:
                self.report.append("🎯 【 VIX 공포지수 상세 분석 】")
                self.report.append("-" * 60)
                vix_val = vix_data['current']
                signal = self.interpret_signal(vix_val, 'vix')
                self.report.append(f"현재 VIX: {vix_val}")
                self.report.append(f"상태: {signal[0]}")
                self.report.append(f"대응: {signal[1]}")
                
                if vix_val > 20:
                    self.report.append("")
                    self.report.append("⚠️ 위험 신호 - 권장 대응:")
                    if vix_val > 30:
                        self.report.append("  1. 기술주 50% 이상 현금화")
                        self.report.append("  2. 현금 40% 이상 확보")
                        self.report.append("  3. 금 추가 매수")
                    elif vix_val > 25:
                        self.report.append("  1. 기술주 30% 현금화")
                        self.report.append("  2. 현금 15% 확보")
                self.report.append("")
            
            # 3. 한국 시장
            self.report.append("🇰🇷 【 한국 시장 】")
            self.report.append("-" * 60)
            kospi = self.get_stock_data('^KS11')
            won = self.get_stock_data('USDKRW=X')
            
            if kospi:
                arrow = "📈" if kospi['change'] >= 0 else "📉"
                self.report.append(f"{arrow} 코스피: {kospi['current']}")
                self.report.append(f"   변화: {kospi['change']:+.2f}%")
            else:
                self.report.append("⚠️ 코스피: 데이터 오류")
            self.report.append("")
            
            if won:
                signal = self.interpret_signal(won['current'], 'won_rate')
                arrow = "📈" if won['change'] >= 0 else "📉"
                self.report.append(f"{arrow} USD/KRW: {won['current']}")
                self.report.append(f"   변화: {won['change']:+.2f}%")
                self.report.append(f"   상태: {signal[0]}")
                self.report.append(f"   대응: {signal[1]}")
            else:
                self.report.append("⚠️ USD/KRW: 데이터 오류")
            self.report.append("")
            
            # 4. 원자재
            self.report.append("💰 【 원자재 & 암호화폐 】")
            self.report.append("-" * 60)
            
            gold = self.get_stock_data('GC=F')
            bitcoin = self.get_stock_data('BTC-USD')
            
            if gold:
                arrow = "📈" if gold['change'] >= 0 else "📉"
                signal = self.interpret_signal(gold['current'], 'gold')
                self.report.append(f"{arrow} 금 (Gold): ${gold['current']}")
                self.report.append(f"   변화: {gold['change']:+.2f}%")
                self.report.append(f"   상태: {signal[0]}")
            else:
                self.report.append("⚠️ 금: 데이터 오류")
            self.report.append("")
            
            if bitcoin:
                arrow = "📈" if bitcoin['change'] >= 0 else "📉"
                signal = self.interpret_signal(bitcoin['current'], 'bitcoin')
                btc_val = bitcoin['current']
                self.report.append(f"{arrow} 비트코인: ${btc_val:,.0f}")
                self.report.append(f"   변화: {bitcoin['change']:+.2f}%")
                self.report.append(f"   상태: {signal[0]}")
            else:
                self.report.append("⚠️ 비트코인: 데이터 오류")
            self.report.append("")
            
            # 5. 개별주식
            self.report.append("📈 【 보유 개별주식 】")
            self.report.append("-" * 60)
            
            for name, symbol in MY_STOCKS.items():
                data = self.get_stock_data(symbol)
                if data:
                    arrow = "📈" if data['change'] >= 0 else "📉"
                    self.report.append(f"{arrow} {name} ({symbol}): ${data['current']}")
                    self.report.append(f"   변화: {data['change']:+.2f}%")
                    if data['change'] < -15:
                        self.report.append(f"   ⚠️ 손절 검토 필요")
                    elif data['change'] > 20:
                        self.report.append(f"   🎯 수익 실현 검토")
                else:
                    self.report.append(f"⚠️ {name}: 데이터 오류")
                self.report.append("")
            
            # 6. 일일 액션 아이템
            self.report.append("✅ 【 오늘의 액션 아이템 】")
            self.report.append("-" * 60)
            
            actions = []
            sp500 = self.get_stock_data('^GSPC')
            vix = self.get_stock_data('^VIX')
            
            if vix and vix['current'] > 25:
                actions.append("1. 기술주 포지션 축소 (20~30%)")
            
            if sp500 and sp500['change'] < -5:
                actions.append("2. 현금 확보 (15% 이상)")
            
            gold = self.get_stock_data('GC=F')
            if gold and gold['current'] > 4800:
                actions.append("3. 금 월 100만원 이상 매수")
            
            if not actions:
                actions.append("현재 안정적 - 정기적 모니터링만 진행")
            
            for action in actions:
                self.report.append(f"  • {action}")
            
            self.report.append("")
            self.report.append("=" * 60)
            self.report.append("📌 주의: 이 리포트는 참고용입니다.")
            self.report.append("투자 결정 시 반드시 전문가 조언을 구하세요.")
            self.report.append("=" * 60)
        
        except Exception as e:
            self.report.append(f"\n⚠️ 리포트 생성 중 오류 발생: {str(e)}")
            self.report.append(traceback.format_exc())
        
        return "\n".join(self.report)
    
    def send_email(self, content):
        """이메일 발송"""
        try:
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = RECIPIENT_EMAIL
            msg['Subject'] = f"[시장 모니터링] {self.today.strftime('%Y년 %m월 %d일')} 일일 리포트"
            
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())
            server.quit()
            
            print(f"✅ 이메일 발송 성공: {RECIPIENT_EMAIL}")
            return True
        
        except Exception as e:
            print(f"❌ 이메일 발송 실패: {str(e)}")
            return False
    
    def run(self):
        """메인 실행 함수"""
        print("📊 시장 데이터 수집 중...")
        report = self.generate_report()
        
        print("\n" + report)
        print("\n📧 이메일 발송 중...")
        
        if self.send_email(report):
            print("✅ 완료!")
        else:
            print("❌ 이메일 발송 실패")


if __name__ == "__main__":
    monitor = MarketMonitor()
    monitor.run()
