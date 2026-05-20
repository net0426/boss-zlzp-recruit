from pages.login_manager import BrowserManager

class DriverManager:

    @staticmethod
    def get_driver(name=''):
        """有头模式启动（原 get_driver 行为）"""
        driver = BrowserManager().get_driver(headless=False)
        if name:
            driver.get(name)
        return driver

    @staticmethod
    def get_driver_head(name=''):
        """无头模式启动（原 get_driver_head 行为）"""
        driver = BrowserManager().get_driver(headless=True)
        if name:
            driver.get(name)
        return driver

    @classmethod
    def close_driver(cls):
        """彻底关闭浏览器（供退出时调用）"""
        BrowserManager().quit_driver()