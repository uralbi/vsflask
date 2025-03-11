from urllib.parse import urlencode
import os

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