from config.config import ZLZP_CONFIG, BASE_CONFIG
from pages.base_page import BasePage
from utils.log_utils import logger
import time


class Zlzp_Page(BasePage):
    url = ZLZP_CONFIG['url']
    cur_url = 'https://i.zhaopin.com/'
    # 搜索框
    searchInput = '.search-wrapper__input'
    ifsearchInput = '.a-input__native'
    jobName = BASE_CONFIG['jobName']
    # 判断地理位置
    region_s = '.content-s__item__text'
    region = BASE_CONFIG['Region']
    filteri = '.query-select-comp__content__text'
    filters = [
        # 工作经验
        (2, ZLZP_CONFIG['work']),
        # 学历
        (1, ZLZP_CONFIG['deg']),
    ]
    max_job = ZLZP_CONFIG['max_job']
    nao_job = 0
    # 标签
    job_cards = '.joblist-box__iteminfo'
    job_card = ''
    # 岗位名
    title = '.summary-planes__title'
    # 岗位标签
    skills = '.describtion-card__skills-item'
    # 岗位职责
    content = '.describtion-card__detail-content'
    # 立刻投递
    makefile = '.a-button a--bordered a--filled'
    # 下一页
    next = '.btn soupager__btn'
    # 登录判定
    loginsw = '.home-header__c-no-login'
    # 判断人机
    rnj = '.checkbox checkbox-verify'
    rnji = '#verifyCheckbox'

    def __init__(self, driver):
        super().__init__(driver)
        self.winmax()

    # ==============逻辑核心================

    def html_zlzp_search(self):
        """智联招聘搜索流程，包含登录状态检查"""
        self.get(self.url)

        # 检查登录状态
        if self.wait_ele(self.loginsw, timeout=3):
            logger.warning('智联招聘：未登录状态，跳过智联招聘流程')
            return False
        else:
            logger.info('智联招聘：已登录')

        # 已登录，继续搜索流程
        self.html_zlzp_sear()
        return True

    def html_zlzp_sear(self):
        self.switch_to_latest_tab()
        if self.wait_ele(self.ifsearchInput, timeout=5):
            self.input_and_enter(self.ifsearchInput, f'{self.jobName}\n')
        else:
            self.input_and_enter(self.searchInput, f'{self.jobName}\n')
        self.switch_to_latest_tab()
        logger.info(f'搜索进入{self.jobName}页面')
        time.sleep(2)
        # 查看地址信息
        if self.region != self.wait_ele_text(self.wait_ele(self.region_s)) and self.region:
            self.ele_click(self.region_s)
            time.sleep(1)
            self.ele_click(self.region)
        # 修改学历工作经验
        filteri = self.wait_eles(self.filteri)
        for selector, value in self.filters:
            if value:
                self.hover_web_element(filteri[selector])
                time.sleep(1)
                logger.info(value)
                self.ele_click(value)
                time.sleep(1)
        time.sleep(1)

    # 点击下一页
    def html_zlzp_next(self):
        self.switch_to_latest_tab()
        self.tobottom()
        self.paage_scroll(200)
        tim = self.wait_ele_href(self.wait_ele(self.next))
        if tim:
            self.get(tim)
        self.switch_to_latest_tab()
        time.sleep(3)

    # 找到标签
    def html_zlzp_bottom(self):
        self.switch_to_latest_tab()
        self.job_card = ''
        self.job_card = self.wait_eles(self.job_cards)
        logger.info(f'找到 {len(self.job_card)} 个职位卡片')
        time.sleep(2)
        if not len(self.job_card):
            return True

    # 数据获取数据处理
    def html_zlzp_job(self):
        index = 0
        while self.nao_job < self.max_job:
            if len(self.job_card) <= index:
                self.html_zlzp_next()
                if self.html_zlzp_bottom():
                    break
                else:
                    index = 0
            try:
                self.switch_to_latest_tab()
                logger.info(f'开始第{index + 1}卡片')
                self.job_card[index].scroll.to_see()
                self.wait_ele_click(self.job_card[index])
                time.sleep(0.5)
                self.switch_to_latest_tab()
                if self.wait_ele(self.rnj):
                    self.wait_ele_click(self.rnj)
                elif self.wait_ele(self.rnji):
                    self.wait_ele_click(self.rnji)
                self.html_zlzp_view()
                index += 1
            except Exception as e:
                logger.error(f"第 {index + 1} 个职位点击失败：{str(e)}")

    # 获取岗位内容
    def html_zlzp_view(self):
        try:
            time.sleep(1)
            self.switch_to_latest_tab()
            iframe = self.wait_ele_iframe('XPATH://*[@id="tcaptcha_iframe_eo"]')
            if iframe:
                self.wait_ele_click(iframe, self.rnj)
                self.wait_ele_click(iframe, self.rnji)

            self.switch_to_latest_tab()
            title = self.wait_ele_text(self.wait_ele(self.title))
            skills = self.wait_eles(self.skills)
            skill = []
            for index, tim in enumerate(skills):
                skill.append(self.wait_ele_text(tim))
            content = self.wait_ele_text(self.wait_ele(self.content))
            content = content.replace('\n', '').replace('"', '')
            clean_job = {
                "岗位名称": title,
                "职位标签": "、".join(skill),
                "岗位职责": content
            }
            if self.immediate(clean_job, self.jobName):
                self.nao_job += 1
                logger.info(f'第{self.nao_job}符合内容,立刻联系')
                self.ele_click(self.makefile)
                time.sleep(1)
                self.switch_to_latest_tab()
                time.sleep(1)
                self.close_current_tab()
            else:
                logger.info('不符合')
            self.switch_to_latest_tab()
            time.sleep(1)
            self.close_current_tab()
        except Exception as e:
            logger.error(f'获取岗位内容错误:{e}')