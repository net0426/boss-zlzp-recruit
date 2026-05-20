from pages.boss_page import Boss_Page
from pages.get_web import DriverManager
from pages.zlzp_page import Zlzp_Page
from pages.start_copaw import LocalAIHeadlessRunner, stop_ai

class RecruitBusiness:
    def __init__(self, headless=False):
        """
        初始化招聘业务类
        
        Args:
            headless: 是否使用无头模式运行浏览器
                     - True:  无头模式，不显示浏览器窗口（适用于 main.py）
                     - False: 有头模式，显示浏览器窗口（适用于 GUI 启动）
        """
        if headless:
            self.driver = DriverManager.get_driver_head()
        else:
            self.driver = DriverManager.get_driver()
        
        self.boss = Boss_Page(self.driver)
        self.zlzp = Zlzp_Page(self.driver)
        LocalAIHeadlessRunner().start_ai()

    def boss_ints(self):
        """BOSS直聘执行流程，包含登录检查"""
        if not self.boss.html_boss_search():
            # 未登录，跳过后续流程
            return
        
        self.boss.html_boss_bottom()
        self.boss.html_boss_jobs()

    def zlzp_ints(self):
        """智联招聘执行流程，包含登录检查"""
        if not self.zlzp.html_zlzp_search():
            # 未登录，跳过后续流程
            return
        
        self.zlzp.html_zlzp_bottom()
        self.zlzp.html_zlzp_job()

    def __del__(self):
        stop_ai()