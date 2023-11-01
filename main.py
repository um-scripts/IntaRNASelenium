import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re
import os
import requests
import numpy as np

if not os.path.exists('OUTPUT_CSV'):
    os.mkdir('OUTPUT_CSV')

if not os.path.exists('details.csv'):
    D = pd.DataFrame(columns=['Name', 'Result URL'])
else:
    D = pd.read_csv('details.csv')

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
input_file = open('MASTERsRNAseq.fa', 'r')

lines = input_file.readlines()
for i in range(0, len(lines), 2):
    ref_id = lines[i].strip('\n')[:-3]
    sequence = lines[i+1].strip('\n')
    print(f'{ref_id}')

    if ref_id in D['Name'].values:
        print('Already Done')
        continue
    elif len(sequence) >750:
        D= D.append({'Name':ref_id,'Result URL': np.nan}, ignore_index= True)
        D.to_csv('details.csv',index= False)
        print('sequence length greater than 750')
        continue

    browser.get("http://rna.informatik.uni-freiburg.de/IntaRNA/Input.jsp")
    ref = browser.find_element(By.ID, "querysequences")
    ref.send_keys(ref_id + '\n' + sequence)
    browser.execute_script("toggleNCBI();checkNCBI();")
    ref = browser.find_element(By.ID, "ncbiacc")
    ref.send_keys("NC_000962")
    browser.find_element(By.CLASS_NAME, "button_start").click()
    c_url = browser.current_url

    WebDriverWait(browser, 900).until(lambda d: re.match("^http://rna.informatik.uni-freiburg.de/IntaRNA/Result.jsp\\?"
                                                         "toolName=IntaRNA&jobID=[0-9]+$", d.current_url) is not None)

    links = browser.find_elements(By.TAG_NAME, 'a')
    fl = False
    for link in links:
        href = link.get_attribute('href')
        if not re.match("^http://rna.informatik.uni-freiburg.de/DownloadFile.jsp\\?jobID=[0-9]+"
                        "&toolName=IntaRNA&isTextFile=true&fileNameOrType=intarna_websrv_table_truncated.csv$", href):
            continue
        fl = True
        of = open(f'OUTPUT_CSV/{ref_id.split(":")[1]}.csv', 'wb')
        res = requests.get(href, timeout=100)
        of.write(res.content)
        res.close()
        of.close()
        break

    if fl:
        print(f'Success')
        D = D.append({'Name': ref_id, 'Result URL': browser.current_url}, ignore_index=True)
        D.to_csv('details.csv', index=False)
    else:
        print(f'Failure')