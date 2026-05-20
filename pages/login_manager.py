
import time
import random
from DrissionPage import ChromiumPage, ChromiumOptions

class BrowserManager:
    _instance = None
    _driver = None
    _boss_page = None      # ✅ 恢复这两个属性
    _zlzp_page = None      # ✅ 恢复这两个属性
    _current_headless = None   # 记录当前浏览器的头模式
    HEADLESS = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_driver(self, headless=None):
        if headless is None:
            headless = self.HEADLESS

        # 已存在且模式相同 -> 直接返回
        if self._driver is not None and self._current_headless == headless:
            return self._driver

        # 模式不同 -> 关闭现有浏览器，重新创建
        if self._driver is not None:
            self.quit_driver()

        if headless:
            self._driver = self._create_headless_driver()
        else:
            self._driver = self._create_driver()
        self._current_headless = headless
        return self._driver

    def _create_driver(self):
        return ChromiumPage()

    def _create_headless_driver(self):
        co = ChromiumOptions()
        co.headless()
        co.set_argument('--headless=new')
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--window-size=1920,1080')
        co.set_argument('--lang=zh-CN,zh;q=0.9,en;q=0.8')
        co.set_argument('--user-agent=Mozilla/5.0 ...')  # 你的原有 UA
        co.set_argument('--disable-gpu')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-dev-shm-usage')
        co.set_local_port(9222)
        return ChromiumPage(addr_or_opts=co)

    def quit_driver(self):
        if self._driver is not None:
            try:
                self._driver.quit()   # 彻底关闭浏览器进程
            except:
                pass
            self._driver = None
            self._current_headless = None

    def get_boss_page(self):
        """获取 BOSS 直聘页面实例（单例）"""
        if self._boss_page is None:
            # from verification import BossPage   # 避免循环导入，放在方法内
            self._boss_page = BossPage(self)
        return self._boss_page

    def get_zlzp_page(self):
        """获取智联招聘页面实例（单例）"""
        if self._zlzp_page is None:
            # from verification import ZlzpPage
            self._zlzp_page = ZlzpPage(self)
        return self._zlzp_page


class BossPage:
    """BOSS直聘页面操作类"""
    boss_url = 'https://www.zhipin.com/guangzhou/?ka=header-home'
    # 登录检查
    search = '.ipt-search'
    # 获取二维码
    get_ewm = '.btn-sign-switch ewm-switch'
    # 二维码
    ewm = '.qr-img-box'
    # 刷新
    refresh = '.btn btn-primary'
    # 登录成功
    ris = '.nav-figure'
    # 登录
    login = '.btn btn-outline header-login-btn'
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.driver = None
        self.tab = None

    def _get_or_create_tab(self):
        browser = self.browser_manager.get_driver()
        if self.tab is None:
            self.tab = browser.new_tab()
            self.driver = self.tab
            self._maximize_window(browser)
            print("BOSS直聘创建新标签页")
        try:
            _ = self.tab.title
        except:
            self.tab = browser.new_tab()
            self.driver = self.tab
            self._maximize_window(browser)
            print("BOSS直聘已关闭")
        return self.driver

    def _maximize_window(self, browser):
        """窗口最大化"""
        try:
            browser.set.window.max()
        except:
            pass

    def get_qrcode(self):
        driver = self._get_or_create_tab()

        try:
            # 确保在主页
            if self.boss_url not in driver.url:
                driver.get(self.boss_url)
                time.sleep(2)
        except:
            driver.get(self.boss_url)

        try:
            if driver.ele(self.search):
                # 1. 优先判断是否已经登录成功 (通过头像判断)
                if driver.ele(self.ris, timeout=2):
                    return '登录成功'
                # 2. 检查是否有登录按钮
                login_btn = driver.ele(self.login, timeout=2)
                if login_btn:
                    login_btn.click()
                    time.sleep(1)
                    ewm_switch = driver.ele(self.get_ewm, timeout=2)
                    if ewm_switch:
                        ewm_switch.click()
                        time.sleep(0.8)
                    qr_img = driver.ele(self.ewm, timeout=3)
                    if qr_img:
                        qr_img.get_screenshot(path='img/', name='boss_image.png')
                        return 'img/boss_image.png'
                    return '未找到二维码元素'
            else:
                return '页面加载异常'
        except Exception as e:
            return '获取二维码失败'

    def refresh_qrcode(self):
        """刷新二维码（不新建标签页，直接在当前页刷新）"""
        if self.driver is None:
            # 如果 driver 丢失，重新获取标签页
            self._get_or_create_tab()
        try:
            # 先尝试点击刷新按钮（如果有）
            refresh_btn = self.driver.ele(self.refresh, timeout=2)
            if refresh_btn:
                refresh_btn.click()
                time.sleep(random.uniform(0.5, 1))
            refis = self.driver.ele(self.ris,timeout=2)
            if refis:
                return '登录成功'
            # 重新截图
            qr_img = self.driver.ele(self.ewm, timeout=5)
            if qr_img:
                qr_img.get_screenshot(path='img/', name='boss_image.png')
                print('BOSS直聘二维码刷新成功')
                return 'img/boss_image.png'
            else:
                return '未找到二维码元素'
        except Exception as e:
            print(f"刷新出错: {e}")
            return '失败'


class ZlzpPage:
    """智联招聘页面操作类"""
    zlzp_url = 'https://www.zhaopin.com/'
    # 检查点
    checkpoint = '.search-wrapper__input'
    # 二维码按钮
    get_ewm = '.zppp-panel-normal-bar__img'
    # 二维码
    ewm = '.zppp-panel-scan-qrcode'
    # 刷新
    refresh = 'tag:img@alt=qrcode'
    # 登录成功  备选c-login__top__name c-login__top__photo basic-info__content
    riss = '.page-header__user'
    ris = '.c-login__top__photo'
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager
        self.driver = None
        self.tab = None

    def _get_or_create_tab(self):
        browser = self.browser_manager.get_driver()
        if self.tab is None:
            self.tab = browser.new_tab()
            self.driver = self.tab
            self._maximize_window(browser)
            print("智联招聘创建新标签页")
        try:
            _ = self.tab.title
        except:
            self.tab = browser.new_tab()
            self.driver = self.tab
            self._maximize_window(browser)
            print("智联招聘已关闭")
        return self.driver

    def _maximize_window(self, browser):
        """窗口最大化"""
        try:
            browser.set.window.max()
        except:
            pass

    def get_qrcode(self):
        driver = self._get_or_create_tab()

        try:
            current_url = driver.url
            if current_url != self.zlzp_url:
                driver.get(self.zlzp_url)
                time.sleep(random.uniform(2, 3))
        except:
            driver.get(self.zlzp_url)
            time.sleep(random.uniform(2, 3))

        try:
            if driver.ele(self.checkpoint):
                if driver.ele(self.ris, timeout=2):
                    return '登录成功'
                login_icon = driver.ele(self.get_ewm, timeout=2)
                if login_icon:
                    login_icon.click()
                    time.sleep(1)
                qr_img = driver.ele(self.ewm, timeout=3)
                if qr_img:
                    qr_img.get_screenshot(path='img/', name='zlzp_image.png')
                    return 'img/zlzp_image.png'
                return '未找到二维码元素'
            else:
                return '页面加载异常'
        except Exception as e:
            return '获取二维码失败'

    def refresh_qrcode(self):
        """刷新二维码（复用当前标签页）"""
        if self.driver is None:
            self._get_or_create_tab()
        # 确保当前激活的标签页是智联招聘的页面
        browser = self.driver.browser
        target_tab = None
        for tab in browser.get_tabs():
            if '智联招聘' in tab.title or 'zhaopin' in tab.url:
                target_tab = tab
                break
        if target_tab:
            browser.activate_tab(target_tab)
            self.driver = target_tab
            self.tab = target_tab
            time.sleep(1)
        else:
            print("未找到智联招聘标签页，重新打开")
            self._get_or_create_tab()

        try:
            if self.driver.ele(self.ris, timeout=2) or self.driver.ele(self.riss, timeout=2):
                return '登录成功'
            # 先尝试点击刷新二维码的图片（如果有）
            qr_img_elem = self.driver.ele(self.refresh, timeout=1)
            if qr_img_elem:
                qr_img_elem.click()
                time.sleep(random.uniform(0.7, 1.5))
            # 重新截图
            qr_img = self.driver.ele(self.ewm, timeout=5)
            if qr_img:
                qr_img.get_screenshot(path='img/', name='zlzp_image.png')
                print('智联招聘二维码刷新成功')
                return 'img/zlzp_image.png'
            else:
                return '未找到二维码元素'
        except Exception as e:
            print(f"刷新出错: {e}")
            return '失败'


class BrowserCloser:
    """浏览器关闭器，负责关闭整个浏览器实例并清理资源"""

    def __init__(self):
        self.browser_manager = BrowserManager()

    def close_browser(self):
        """彻底关闭浏览器（会终止浏览器进程）"""
        self.browser_manager.quit_driver()
        print("浏览器已关闭")
