# pages/base_page.py
from config.config import AI_CONFIG
from pages.AI_page import AiPage
import requests
import time
import re


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10

    # 跳转页面
    def get(self, url):
        self.driver.get(url)
        self.driver.wait.load_start()

    def current_url(self):
        return self.driver.url

    # 定位获取元素
    def wait_ele(self, locator: str, timeout=None):
        timeout = timeout or self.timeout
        return self.driver.ele(locator, timeout=timeout)

    # 定位获取多个元素
    def wait_eles(self, locator: str, timeout=None):
        timeout = timeout or self.timeout
        return self.driver.eles(locator, timeout=timeout)

    # 获取iframe内容
    def wait_ele_iframe(self, locator: str, timeout=None):
        try:
            timeout = timeout or self.timeout
            return self.driver.iframe(locator, timeout=timeout)
        except Exception as e:
            return False

    def wait_get_tab_name(self, locator: str):
        target_tab = self.driver.get_tab(title=locator)
        if target_tab:
            self.driver.activate_tab(target_tab)
            print(f"已激活标题为 '{target_tab.title}' 的标签页。")
        else:
            print(f"未找到标题包含 {target_tab.title} 的标签页。")

    # 点击
    def ele_click(self, locator: str):
        self.wait_ele(locator).click()

    # 点击已经获取的元素
    def wait_ele_click(self, web_element, locator: str = None):
        if locator:
            web_element.ele(locator).click()
        else:
            web_element.click()
        time.sleep(0.5)

    # 输入内容
    def input_and_enter(self, locator: str, text: str):
        ele = self.wait_ele(locator)
        ele.clear()
        time.sleep(0.1)
        ele.input(text)

    # 切换到最新打开的标签页
    def switch_to_latest_tab(self):
        self.driver = self.driver.browser.latest_tab
        time.sleep(0.5)

    # 关闭当前标签页
    def close_current_tab(self):
        self.driver.close()
        time.sleep(0.5)

    # 返回上一页
    def close_back(self):
        self.driver.back()
        time.sleep(0.5)

    # 页面滑动到底部
    def tobottom(self, tim: int = 0.4):
        self.driver.scroll.to_bottom()
        time.sleep(tim)

    # 页面滑动
    def paage_scroll(self, tosse):
        if tosse > 0:
            self.driver.scroll.up(tosse)
        else:
            self.driver.scroll.down(tosse)

    # 页面放最大
    def winmax(self):
        self.driver.set.window.max()

    # 删除style元素
    def delete_style(self, locator: str, style):
        target_ele = self.driver.ele(locator)
        if target_ele:
            self.driver.run_js(f"arguments[0].style.{style};", target_ele)
        else:
            print('删除失败')

    # 悬停
    def hover_ele(self, locator: str):
        ele = self.driver.ele(locator, timeout=15)
        if ele:
            ele.hover()
        else:
            print("未找到元素")

    def hover_web_element(self, web_element):
        if web_element:
            web_element.hover()
        else:
            print("未找到元素")

    # 获取元素内的元素文本
    def wait_ele_text(self, web_element, locator: str = ''):
        if locator == '':
            return web_element.text
        else:
            return web_element.ele(locator).text

    # 获取元素内的所有该元素文本
    def wait_eles_text(self, web_element, locator: str = ''):
        if locator == '':
            return web_element.text
        else:
            elements = web_element.eles(locator)
            texts = []
            for i, ele in enumerate(elements):
                text = ele.text
                texts.append(text)
            return texts

    # 获取元素内的url
    def wait_ele_href(self, web_element, locator: str = '', attri: str = 'href'):
        try:
            if locator == '':
                return web_element.attr(attri)
            else:
                return web_element.ele(locator).attr(attri)
        except Exception as e:
            print('获取元素错误')
            return False

    # 获取元素内元素
    def wait_ele_element(self, web_element, locator: str, timeout=15):
        return web_element.ele(locator, timeout=timeout)

    # =============清洗工具================
    def get_clean_text(self, element, email_Ext):
        if not element:
            return ""
        raw_text = self.wait_ele_text(element)
        raw_text = re.sub(email_Ext, '', raw_text)
        return raw_text.strip()

    def html_boss_job_name(self, web_element, JobName):
        return self.wait_ele_text(web_element, JobName)

    # 极简清洗函数
    def clean_one_job(self, name, raw_job, email_Ext):
        label = []
        for item in raw_job[:-3]:
            item = str(item).strip()
            if len(item) > 20 or item in ["职位描述", ""]:
                continue
            label.append(item)
        label = list(set(label))
        statement = ""
        if len(raw_job) >= 3:
            content = raw_job[-3].strip()
            content = re.sub(email_Ext, " ", content).strip()
            statement = content
        return {
            "岗位名称": name,
            "职位标签": "、".join(label),
            "岗位职责": statement
        }

    # =============AI调用================
    def to_ai_text(self, datum, jobName):
        text = f"【岗位{jobName}】\n岗位名称：{datum.get('岗位名称', '未知')}\n核心信息：{datum.get('职位标签', '无')} | {datum.get('岗位职责', '无')[:200]}\n\n"
        return text

    def boss_AI_text(self, text, id=0, temperature=0.1):
        im = AiPage.text_open(AI_CONFIG['UserQuery'][id])
        params = {
            "model": "qwen",
            "messages": [
                {"role": "system", "content": im},
                {"role": "user", "content": text}
            ],
            "temperature": temperature,
            "max_tokens": 6800,
            "stream": False
        }
        try:
            r = requests.post(AI_CONFIG['ApiPath'], json=params)
            r.raise_for_status()
            res = r.json()
            return res["choices"][0]["message"]["content"]
        except Exception as e:
            print("❌ 请求失败：", e)
            print("返回内容：", r.text if 'r' in locals() else '')
            return False

    # ai判断岗位符合与否逻辑
    def immediate(self, clean_job, jobName):
        service = ''
        for _ in range(3):
            try:
                service = self.AI_Service(clean_job, jobName).strip().upper()
                print(service)
                if service in ("TRUE", "FALSE"):
                    break
                print("返回值格式错误，重试中...")
            except Exception as e:
                print(f"AI调用异常：{e}，重试中...")
                time.sleep(1)
        return service == 'TRUE'

    # 调用ai分析
    def AI_Service(self, datum, jobName):
        return self.boss_AI_text(self.to_ai_text(datum, jobName))

    def AI_sayhi(self, datum, jobName):
        return self.boss_AI_text(self.to_ai_text(datum, jobName), id=1)
