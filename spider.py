import re

import logging
from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Chrome

logging.basicConfig(level=logging.INFO)


class DDGspider(object):
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.page_load_strategy = 'eager'

        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('blink-settings=imagesEnabled=false')
        self.chrome_options.add_argument('--incognito')

        self.chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        self.base_url = "https://duckduckgo.com/?q={}&t=h_&atb=v371-2__&ia=web"
        self.title_class_name = "ikg2IXiCD14iVX7AdZo1"
        self.abstract_class_name = "OgdwYG6KE2qthn9XQWFC"
        self.doc_content_class_name = "nrn-react-div"
        self.url_calss_name = "LnpumSThxEWMIsDdAT17 CXMyPcQ6nDv47DKFeywM"

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

        driver.close()
        return {"status": status, "html": page}

    # status: 成功 200，其它 0
    def htmlToSearchResult(self, query, reuslt_num):
        html_info = self.getHtml(query)
        search_result = {"status" : 0, "docs" : [{}]}

        if html_info["status"] != 200:
            return search_result

        page = html_info["html"]
        try:
            docs_div = page.find_all(class_ = self.doc_content_class_name)
        except:
            logging.error("Failed to find class name.")
            return search_result

        doc_info = self._getText(docs_div, reuslt_num)
        if len(doc_info) > 0:
            search_result["docs"] = doc_info
            search_result["status"] = 200

        return search_result

    def _cleanText(self, text):

        return re.sub(r'(\n){4,}', '\n\n\n', text.strip()).\
            replace(' {3,}', ' ').replace('\t', '').replace(
            '\n+(\s*\n)*', '\n')

    # doc = {"order": 1, "title" : "", "abstract" : "", "url" : []}
    def _getText(self, docs_div, result_number):
        doc_info = []
        if len(docs_div) > 0:
            docs_div = docs_div[:result_number]
            order = 1
            for item in docs_div:
                doc = {}
                item = str(item)
                item = BeautifulSoup(item, 'html.parser')
                abstract_div = item.find(class_=self.abstract_class_name)
                title_div = item.find(class_=self.title_class_name)
                url_div = item.find(class_=self.url_calss_name)
                if not abstract_div or not title_div or not url_div:
                    continue

                doc["oredr"] = order
                title = ";".join([span.get_text() for span in title_div.find_all('span')])
                doc["title"] = self._cleanText(title)
                abstract = ";".join([span.get_text() for span in abstract_div.find_all('span')])
                doc["abstract"] = self._cleanText(abstract)
                doc["url"] = [link.get("href", "") for link in url_div.find_all('a')]

                order += 1

                doc_info.append(doc)

        return doc_info


if __name__ == "__main__":
    spider = DDGspider()
    search_result = spider.htmlToSearchResult("介绍一下狂飙", 3)
    print(search_result)