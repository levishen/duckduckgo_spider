import logging
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Chrome

logging.basicConfig(level=logging.INFO)


class BDspider(object):
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.page_load_strategy = 'eager'

        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('blink-settings=imagesEnabled=false')
        self.chrome_options.add_argument('--incognito')

        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        self.base_url = "https://www.baidu.com/s?wd={}&rsv_spt=1&rsv_iqid=0xc2ecfb71000003cf&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=cn&tn=baiduhome_pg&rsv_enter=1&rsv_dl=tb&oq=%25E8%258B%258D%25E5%2585%25B0%25E8%25AF%2580&rsv_btype=t&inputT=2404&rsv_t=74f44Vc2Qm1DSaT%2BFo9Z3KHk%2FN9CLUs4bjLt5WN%2Ffhd5dGNvTKflCFxN1OhGfsp3e5nk&rsv_sug3=23&rsv_sug1=20&rsv_sug7=101&rsv_pq=b91a5d6b0000139d&rsv_sug2=0&rsv_sug4=2999"
        self.title_class_name = "c-title t t tts-title"
        self.abstract_class_name = "c-gap-top-small"
        self.doc_content_class_name = "c-container"
        self.url_calss_name = "c-title t t tts-title"

    def getHtml(self, query):
        driver = Chrome(options=self.chrome_options)
        # 超时5s 视为失败.
        driver.set_page_load_timeout(5)

        status = 0
        url = self.base_url.format(query)
        try:
            driver.get(url)
        except TimeoutException:
            logging.error("{}: Timeout occurred.".format(query))
        except WebDriverException:
            logging.error("{}: Failed to get html.".format(query))

        page = ""
        try:
            page = BeautifulSoup(driver.page_source, 'html.parser')
            status = 200
        except Exception:
            logging.error("{}: Html format is invalid.".format(query))

        driver.quit()
        return {"status": status, "html": page}

    # status: 成功 200，其它 0
    def htmlToSearchResult(self, query, reuslt_num):
        html_info = self.getHtml(query)
        search_result = {"status" : 0, "docs" : [{}]}

        if html_info["status"] != 200:
            return search_result

        page = html_info["html"]
        try:
            docs_div = page.find('div', {'id': 'content_left'}).\
                find_all(class_ = self.doc_content_class_name)
        except Exception as e:
            logging.error("Failed to find class name.", e)
            return search_result

        doc_info = self._getDocInfo(docs_div, reuslt_num)
        if len(doc_info) > 0:
            search_result["docs"] = doc_info
            search_result["status"] = 200

        return search_result

    # doc = {"order": 1, "title" : "", "abstract" : "", "url" : []}
    def _getDocInfo(self, docs_div, result_number):
        doc_info = []
        if len(docs_div) > 0:
            docs_div = docs_div[:result_number]
            order = 1
            for item in docs_div:
                doc = {}
                item = str(item)
                item = BeautifulSoup(item, 'html.parser')
                abstract_div = item.find(class_=self.abstract_class_name)
                if not abstract_div:
                    continue

                doc["oredr"] = order
                doc["title"] = ";".join([span.get_text() for span in item.find_all('a')])
                doc["abstract"] = ";".join([span.get_text() for span in abstract_div.find_all('span')])
                doc["url"] = [link.get("href", "") for link in item.find_all('a')][:1]

                order += 1

                doc_info.append(doc)

        return doc_info


if __name__ == "__main__":
    spider = BDspider()
    search_result = spider.htmlToSearchResult("苍兰诀", 3)
    print(search_result)
