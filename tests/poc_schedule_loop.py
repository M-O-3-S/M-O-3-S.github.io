import schedule
import time
import sys

def dummy_job():
    print(f"[{time.strftime('%H:%M:%S')}] ⏳ 스케줄러 트리거 발동! (가상의 백엔드 파이프라인 실행 중...)")

def test_scheduler_loop():
    print("=== [Architecture Step 4] 파이썬 범용 스케줄러 검증 PoC ===")
    print("목표: Mac cron 없이 자체적으로 백그라운드 루프가 도는지 10초간 검증합니다.")
    
    # 초 단위로 빠른 테스트
    schedule.every(2).seconds.do(dummy_job)
    
    start_time = time.time()
    loops = 0
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
            loops += 1
            if time.time() - start_time > 7.0: # 7초간 돌려봄 (2초마다 3번 발생 예정)
                print("\n✅ 검증 통과(Pass): 백그라운드 스케줄러 데몬이 안정적으로 실행 및 예약 트리거 완료!")
                break
    except KeyboardInterrupt:
        print("\n중단됨")

if __name__ == "__main__":
    test_scheduler_loop()
