from urllib.parse import urlencode
import os, requests, re
from bs4 import BeautifulSoup as bs

class Utils:
    
    def get_company(self, comp_name):
        params = {'fullNameRu': comp_name, 'operator': 'AND'}
        firm = urlencode(params)
        lk = f"https://online.minjust.gov.kg/user/search?{firm}"
        return lk

    def find_hscodes(self, swords: list):
        base_path = os.path.dirname(__file__)  # Get the directory of ds.py
        file_path = os.path.join(base_path, "data/hscodes.txt")
        with open(file_path, 'r') as file:
            matched_lines = [line.strip() for line in file]
        
        check_dig = self.check_digit(swords[0])
        if len(swords) == 1 and check_dig:
            matched_lines = [line+'<br>' for line in matched_lines if line.lower().startswith(swords[0].lower())]
        else:
            k = 1
            for word in swords:
                if k == 1:
                    matched_lines = [line+'<br>' for line in matched_lines if word.lower() in line.lower()]
                else:
                    matched_lines = [line for line in matched_lines if word.lower() in line.lower()]
                k+=1
                if not matched_lines:
                    break
        return matched_lines
    
    def check_digit(self, n):
        return n.replace(" ", "").isdigit()
    
    def get_news(self, query):
        news_lines = [(title, link) for title, link in self.get_news_data()]
        return news_lines
    
    def get_news_data(self):
        """
        return: list: title, text, url_link
        """
        wsite = 'https://24.kg/'
        try:
            page = requests.get(wsite, timeout=5).text
        except Exception as e:
            raise TimeoutError(f'24.kg is not available at this moment', e)
        soup = bs(page, 'html.parser')
        news = soup.find_all('div', class_='title')
        sk_ptn = r'[Пп]огод[аы]|Курс доллара|Температурные'
        ptn = r'href="(.*)"'
        k = 1
        for i in news:
            if re.search(sk_ptn,i.text.strip()) or 'Афиша Бишкека' in i.text or 'Чудаки парковки' in i.text:
                continue
            else:
                try:
                    sch = re.search(ptn, str(i.a))
                    if sch:
                        link_1 = f'{wsite[:-1]}{sch[1][:-1]}'
                        title = i.text.strip()
                        # content = data_from_url(link_1)
                        yield (title, link_1)
                        k += 1
                except:
                    pass
                
# if __name__ == "__main__":
#     ut = Utils()
#     res= ut.get_news("query")
#     print(res)
    