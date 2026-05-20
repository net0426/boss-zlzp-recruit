from config.config import BOSS_CONFIG, BASE_CONFIG
from pages.base_page import BasePage
from utils.log_utils import logger
from pypinyin import lazy_pinyin
import time


class Boss_Page(BasePage):
    url = BOSS_CONFIG['url']
    # 搜索框
    searchInput = '.ipt-search'
    jobName = BASE_CONFIG['jobName']
    # 地理位置
    region_s = '.city-label active'
    region = BASE_CONFIG['Region']
    # 所有城市简写
    char_list = '.city-char-list'
    # 所有城市简写详细
    char_list_li = 'xpath:.//li'
    # 详细城市box
    region_box = '.city-list-select'
    # 工作经验学历
    filteri = '.condition-filter-select'
    filters = [
        # 工作经验
        (2, BOSS_CONFIG['work']),
        # 学历
        (3, BOSS_CONFIG['deg']),
    ]
    # 下滑次数
    scrollDownCount = 1
    # 岗位卡片
    job_cards = '.job-card-wrap'
    job_card = ''
    # 岗位数据
    datum = []
    # 最多多少条岗位
    max_job = BOSS_CONFIG['max_job']
    nao_job = 0
    # 岗位名称
    boss_name = '.boss-name'
    # 全部详情
    user_name = '.job-detail-box'
    body_ele = '.job-detail-body'
    header_ele = '.job-detail-header'
    # 获取岗位名称
    job_name = '.job-name'
    # 正则清洗
    email_Ext = 'boss|来自BOSS直聘'
    # 立即沟通
    makefile = '.op-btn op-btn-chat'
    # 输入框
    chat_input = '.chat-input'
    # 发送
    send = '.btn-v2 btn-sure-v2 btn-send'

    # 登录状态检查
    login_success = '.nav-figure'

    def __init__(self, driver):
        super().__init__(driver)
        self.winmax()

    # ==============逻辑核心================
    def html_boss_search(self):
        """BOSS直聘搜索流程，包含登录状态检查"""
        self.get(self.url)
        self.wait_get_tab_name("BOSS直聘")

        # 检查登录状态
        if not self.wait_ele(self.login_success, timeout=3):
            logger.warning('BOSS直聘：未登录状态，跳过BOSS直聘流程')
            return False

        logger.info('BOSS直聘：已登录')

        # 已登录，继续搜索流程
        self.input_and_enter(self.searchInput, f'{self.jobName}\n')
        self.switch_to_latest_tab()
        logger.info(f'搜索进入{self.jobName}页面')
        # 修改地址 获取地点首拼音
        result = lazy_pinyin(self.region[0])[0].upper()[:1:]
        time.sleep(3)
        # 点击地址
        self.ele_click(self.region_s)
        time.sleep(1)
        # 获取所有简写标签
        results = self.wait_eles_text(self.wait_ele(self.char_list), self.char_list_li)
        target_index = None
        for idx, text in enumerate(results):
            if result in text:
                target_index = idx + 1
                break
        # 点击首字母拼音对应按钮
        self.wait_ele_click(self.wait_ele(self.char_list), f'xpath:.//li[{target_index}]')
        # 点击地点
        self.wait_ele_click(self.wait_ele(self.region_box), self.region)
        # 修改学历工作经验
        filteri = self.wait_eles(self.filteri)
        for selector, value in self.filters:
            if value:
                self.hover_web_element(filteri[selector])
                time.sleep(1)
                self.wait_ele_click(filteri[selector], value)
                time.sleep(1)
        time.sleep(2)

        logger.info('BOSS直聘：搜索条件设置完成')
        return True

    def html_boss_bottom(self):
        for _ in range(self.scrollDownCount):
            self.tobottom(1)
            self.html_boss_wu()

    def html_boss_wu(self):
        self.job_card = ''
        self.job_card = self.wait_eles(self.job_cards)
        logger.info(f'找到 {len(self.job_card)} 个职位卡片')
        time.sleep(2)

    # 获取到一定数量的岗位
    def html_boss_jobs(self):
        index = 0
        while self.nao_job < self.max_job:
            if len(self.job_card) - 3 <= index:
                self.html_boss_bottom()
            try:
                boss_name = self.wait_ele_text(self.job_card[index], self.boss_name) if self.wait_ele_element(self.job_card[index], self.boss_name) else '未知公司'
                self.wait_ele_click(self.job_card[index])
                detail_container = self.wait_ele(self.user_name)
                if detail_container:
                    header_ele = self.wait_ele_element(detail_container, self.header_ele)
                    body_ele = self.wait_ele_element(self.wait_ele_element(detail_container, self.body_ele), 'tag:p')
                    try:
                        box_ele = self.wait_ele_element(detail_container, '.job-label-list', 2)
                        box_ele = "、".join(self.wait_ele_text(box_ele).split('\n'))
                    except:
                        box_ele = None
                    if body_ele and header_ele:
                        name = self.html_boss_job_name(header_ele, self.job_name)
                        full_content = self.get_clean_text(body_ele, self.email_Ext)
                        logger.info("=" * 60)
                        logger.info(f'点击{boss_name}公司岗位')
                        logger.info("岗位详情：")
                        clean_job = {
                            "岗位名称": name,
                            "职位标签": box_ele,
                            "岗位职责": full_content
                        }
                        logger.info(clean_job)
                        if self.immediate(clean_job, self.jobName):
                            self.nao_job += 1
                            logger.info(f'第{self.nao_job}符合内容,立刻联系')
                            self.wait_ele_click(detail_container, self.makefile)
                            time.sleep(1)
                            self.switch_to_latest_tab()
                            self.input_and_enter(self.chat_input, self.AI_sayhi(clean_job, self.jobName))
                            logger.info(self.AI_sayhi(clean_job, self.jobName))
                            time.sleep(2)
                            self.ele_click(self.send)
                            time.sleep(0.5)
                            self.close_back()
                            time.sleep(2)
                            self.switch_to_latest_tab()
                            self.html_boss_wu()
                        else:
                            logger.info('不符合')
                        index += 1
                        logger.info("=" * 60)
                    else:
                        logger.info(f'{boss_name}：未找到职位详情头部/主体')
                else:
                    logger.info(f'{boss_name}：未找到职位详情容器')
            except Exception as e:
                logger.error(f'处理第 {index} 个职位卡片时出错：{str(e)}')
                continue
        logger.info(f"最终联系到 {self.nao_job} 条有效职位")


