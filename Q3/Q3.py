from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, ElementNotInteractableException
import time
import os
import requests

print('='*30)
print('pixabay 사이트에서 이미지를 검색하여 수집하는 크롤러 입니다.')
print('='*30)

keyword = input('1. 크롤링할 이미지의 키워드는 무엇입니까? ')
count = int(input('2. 크롤링 할 건수는 몇 건입니까? '))
save_folder = input('3. 파일이 저장될 경로를 입력하세요 (예: .//imgs/ 또는 c:/temp/): ')
page_number = 1
# 크롬 드라이버 설정 및 크롤링 시작
try:  
    driver = webdriver.Chrome()
    driver.get('https://pixabay.com/ko/')

    time.sleep(0.5)
    # input_box를 기다렸다가 상호작용
    input_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input'))
    )
    input_box.send_keys(keyword)
    time.sleep(0.5)
    
    input_box.send_keys(Keys.RETURN)
    time.sleep(1.5)

    # 저장 폴더가 없으면 생성
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    imgs = set()
    scroll_pause_time = 1.5

    last_scroll_position = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")

    while len(imgs) < count:
        # 스크롤을 조금씩 내린다.
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(scroll_pause_time)  # 페이지가 로드될 시간을 주기 위해 잠시 대기

        # 이미지 요소들을 다시 찾는다.
        new_imgs = driver.find_elements(By.CSS_SELECTOR, 'img')
        for img in new_imgs:
            try:
                img_url = img.get_attribute('src')
                # print(img_url)
                imgs.add(img_url)
            except StaleElementReferenceException as e:
                print(e)
                continue

        # 현재 스크롤 위치를 측정
        current_scroll_position = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")
        # print("현재 스크롤 위치:", current_scroll_position, last_scroll_position)

        if current_scroll_position == last_scroll_position:
            try:
                page_number += 1
                next_page_url = f'https://pixabay.com/ko/images/search/{keyword}/?pagi={page_number}'
                driver.get(next_page_url)
                time.sleep(1.5)
                last_scroll_position = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")
            except Exception as e:
                print(f'다음 버튼 클릭 중 오류 발생: {e}')
                break

        last_scroll_position = current_scroll_position

    # 이미지 다운로드
    for i, img_url in enumerate(list(imgs)[:count]):
        try:
            img_data = requests.get(img_url).content
            file_name = os.path.join(save_folder, f'img_{i + 1}.jpg')
            with open(file_name, 'wb') as file:
                file.write(img_data)
            print(f'{i + 1}/{count} 이미지 다운로드 완료: {file_name}')
        except Exception as e:
            print(f'이미지 다운로드 중 오류 발생: {e}')

except Exception as e:
    print(f'크롤링 중 오류 발생: {e}')

finally:
    driver.quit()
    print('크롤링 완료. 브라우저를 종료합니다.')
