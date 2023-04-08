import argparse
import clueai
from datetime import datetime
from spider import DDGspider

class WebChatYuan():
    def __init__(self):
        self.key = "zOproTToQyVMNoj3aI4pO100001111"
        self.chat = clueai.Client(self.key, check_api_key=True)
        self.spider = DDGspider()
        self.default_prompt = """
        网络结果：{}
        当前日期：{}
        Instructions：使用提供的网络搜索结果，撰写对给定query的全面回复。\
        确保在参考文献后使用[[数字]（URL）]表示法引用结果。\
        如果提供的搜索结果涉及具有相同名称的多个主题，请为每个主题编写单独的答案。
        query：{}
        """

    def formatWebResults(self, results):
        if not results:
            return ""
        if len(results) == 0:
            return "No results found.\n"
        counter = 1
        return "".join(
            [f"[{counter + i}] \"{result['abstract']}\"\nURL: {result['url']}\n\n" for i, result in enumerate(results)])

    def getPrediction(self, query):
        web_results = self.spider.htmlToSearchResult(query, 3)
        web_content = ""
        if web_results["status"] == 200:
            web_content = self.formatWebResults(web_results["docs"])

        prompt = self.default_prompt.format(web_content, str(datetime.now().date()), query)

        prediction = self.chat.generate(model_name="ChatYuan-large", prompt=prompt)

        text = ""
        if len(prediction.generations) >= 1:
            text = prediction.generations[0].text

        return text


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', help='query')
    args = parser.parse_args()
    chat = WebChatYuan()
    print(chat.getPrediction(args.query))