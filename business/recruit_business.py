from pages.boss_page import Boss_Page
from pages.get_web import DriverManager
from pages.zlzp_page import Zlzp_Page
from pages.start_copaw import LocalAIHeadlessRunner, stop_ai
from config.config import BASE_CONFIG
class RecruitBusiness:
    def __init__(self, headless=False):
        if headless:
            self.driver = DriverManager.get_driver_head()
        else:
            self.driver = DriverManager.get_driver()
        self.boss = Boss_Page(self.driver)
        self.zlzp = Zlzp_Page(self.driver)
        LocalAIHeadlessRunner().start_ai()
        self.numm = self.start(BASE_CONFIG['Region'])
        pass

    def boss_ints(self):
        """BOSS直聘执行流程，包含登录检查"""
        if not self.boss.html_boss_search():
            return False
        if not len(self.numm) == '1':
            snis = []
            for i in range(len(self.numm)):
                self.boss.html_boss_job(self.numm[i])
                self.boss.html_boss_bottom()
                if self.boss.html_boss_jobs():
                    snis.append(f'{self.numm[i]}地区的职业过少')
                else:
                    snis.append(f'{self.numm[i]}地区投递完成')
            return snis
        else:
            self.boss.html_boss_job(self.numm[0])
            self.boss.html_boss_bottom()
            if self.boss.html_boss_jobs():
                return f'{self.numm[0]}岗位过少'
            else:
                return f'{self.numm[0]}地区投递完成'

    def zlzp_ints(self):
        """智联招聘执行流程，包含登录检查"""
        if not self.zlzp.html_zlzp_search():
            return False
        if not len(self.numm) == '1':
            snis = []
            for i in range(len(self.numm)):
                self.boss.html_zlzp_job_region(self.numm[i])
                self.boss.html_zlzp_bottom()
                if self.boss.html_boss_jobs():
                    snis.append(f'{self.numm[i]}地区的职业过少')
                else:
                    snis.append(f'{self.numm[i]}地区投递完成')
            return snis
        else:
            self.zlzp.html_zlzp_job_region(self.numm[0])
            self.zlzp.html_zlzp_bottom()
            if self.zlzp.html_zlzp_job():
                return f'{self.numm[0]}岗位过少'
            else:
                return f'{self.numm[0]}地区投递完成'

    def close(self):
        """显式关闭资源"""
        stop_ai()
        try:
            DriverManager.close_driver()
        except:
            pass

    def start(self,num):
        separators  = ['.','\\','-']
        parts = [num]  # 初始为单元素列表
        for sep in separators:
            # 对当前所有部分，按当前分隔符分割，并展开为新的列表
            parts = [sub for part in parts for sub in part.split(sep)]
        return parts

