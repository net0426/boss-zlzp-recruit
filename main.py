from business.recruit_business import RecruitBusiness
from pages.get_web import DriverManager
from pages.start_copaw import stop_ai
import os
import sys
import argparse
import atexit
from pages.email_page import send_email

def parse_args():
    parser = argparse.ArgumentParser(description="招聘岗位智能筛选系统")
    parser.add_argument("--platform", choices=["boss", "zlzp", "all"], default="all",
                        help="指定爬取平台（boss/zlzp/all）")
    parser.add_argument("--job", type=str, default=None, help="指定目标岗位（覆盖.env中的TARGET_JOB_NAME）")
    parser.add_argument("--region", type=str, default=None, help="指定目标地区（覆盖.env中的TARGET_REGION）")
    return parser.parse_args()


def cleanup():
    """程序退出时的最终清理"""
    try:
        stop_ai()
    except:
        pass
    try:
        DriverManager.close_driver()
    except:
        pass

atexit.register(cleanup)


if __name__ == '__main__':
    args = parse_args()

    if args.job:
        os.environ['TARGET_JOB_NAME'] = args.job
    if args.region:
        os.environ['TARGET_REGION'] = args.region

    try:
        app = RecruitBusiness(headless=True)
        if args.platform in ["boss", "all"]:
            if app.boss_ints(): send_email('BOSS运行错误','')
            else: send_email('BOSS运行成功','')
        if args.platform in ["zlzp", "all"]:
            if app.zlzp_ints(): send_email('智联招聘运行错误','')
            else: send_email('智联招聘运行成功', '')
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序执行出错: {e}")
    finally:
        cleanup()
        print("程序已退出")
        sys.exit(0)
