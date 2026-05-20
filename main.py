from business.recruit_business import RecruitBusiness
from pages.get_web import DriverManager
import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="招聘岗位智能筛选系统")
    parser.add_argument("--platform", choices=["boss", "zlzp", "all"], default="all",
                        help="指定爬取平台（boss/zlzp/all）")
    parser.add_argument("--job", type=str, default=None, help="指定目标岗位（覆盖.env中的TARGET_JOB_NAME）")
    parser.add_argument("--region", type=str, default=None, help="指定目标地区（覆盖.env中的TARGET_REGION）")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if args.job:
        os.environ['TARGET_JOB_NAME'] = args.job
    if args.region:
        os.environ['TARGET_REGION'] = args.region

    app = RecruitBusiness(headless=True)
    if args.platform in ["boss", "all"]:
        app.boss_ints()
    if args.platform in ["zlzp", "all"]:
        app.zlzp_ints()

    DriverManager.close_driver()
