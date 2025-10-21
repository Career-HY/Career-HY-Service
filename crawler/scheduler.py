"""
크롤러 스케줄러

APScheduler를 사용하여 크롤러를 정기적으로 실행합니다.
기본 설정: 매일 오전 9시 실행
"""
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from main import main as run_crawler


def scheduled_crawl_job():
    """스케줄된 크롤링 작업"""
    print(f"\n{'='*60}")
    print(f"📅 정기 크롤링 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    try:
        success = run_crawler()

        if success:
            print(f"\n{'='*60}")
            print(f"✅ 정기 크롤링 성공 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print(f"⚠️  정기 크롤링 일부 실패 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ 정기 크롤링 오류 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   오류 내용: {e}")
        print(f"{'='*60}\n")


def main():
    """스케줄러 메인 함수"""

    # 환경변수에서 스케줄 설정 가져오기 (기본값: 매일 오전 9시)
    schedule_hour = int(os.getenv("CRAWL_SCHEDULE_HOUR", "9"))
    schedule_minute = int(os.getenv("CRAWL_SCHEDULE_MINUTE", "0"))

    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        Career-Hi RAG 크롤러 스케줄러                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 한국 시간대 설정
    kst = pytz.timezone('Asia/Seoul')
    current_time_kst = datetime.now(kst)

    print(f"⏰ 스케줄 설정: 매일 {schedule_hour:02d}:{schedule_minute:02d} 실행 (KST)")
    print(f"🕐 현재 시각: {current_time_kst.strftime('%Y-%m-%d %H:%M:%S')} (KST)\n")

    # 스케줄러 생성 (KST 타임존 사용)
    scheduler = BlockingScheduler(timezone=kst)

    # 크론 작업 등록
    job = scheduler.add_job(
        scheduled_crawl_job,
        CronTrigger(hour=schedule_hour, minute=schedule_minute, timezone=kst),
        id='daily_crawl',
        name='Daily Job Posting Crawl',
        replace_existing=True
    )

    # 즉시 실행 옵션 (환경변수로 제어)
    run_immediately = os.getenv("CRAWL_RUN_IMMEDIATELY", "false").lower() == "true"
    if run_immediately:
        print("🚀 즉시 실행 모드: 스케줄러 시작 직후 크롤링 실행\n")
        scheduled_crawl_job()

    print(f"✅ 스케줄러 시작됨!")
    print("Press Ctrl+C to exit\n")

    try:
        scheduler.start()
        # 스케줄러는 blocking이므로 이 아래 코드는 실행되지 않음
    except (KeyboardInterrupt, SystemExit):
        print("\n\n⏹️  스케줄러 종료")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
