from selenium import webdriver
import urllib
import pickle
import time
import os
import requests, json
import threading
import pickle
import time, datetime

def get_img_Lovelyz(pageStart = 1, pageEnd = 3):
    # img folder 있는지 확인
    list_save_contents = []
    total_update_content = 0

    bIsImgFolder = os.path.exists("img")
    bIsList = os.path.exists("img/list.txt")

    if bIsImgFolder == False:
        os.makedirs("img")

    if bIsList == False:
        with open("img/list.txt", "wt") as f:
            f.write("")
    else:
        with open("img/list.txt", "rt") as f:
            while True:
                content = f.readline()
                if not content:
                    break
                list_save_contents.append(content[:-1])

    print(list_save_contents)

    driver = webdriver.Chrome()
    driver.get("http://theqoo.net")

    # login
    url_login = "http://theqoo.net/index.php?mid=index&act=dispMemberLoginForm"
    driver.get(url_login)
    driver.find_element_by_css_selector("#uid").send_keys("wjy5446")
    with open("pw.p", "rb") as f:
        pw = pickle.load(f)
    driver.find_element_by_css_selector("#upw").send_keys(pw)
    driver.find_element_by_css_selector(".submit.btn").click()

    for num_page in range(pageStart, pageEnd, 1):
        url_lovelyz = "http://theqoo.net/index.php?mid=kdol&category=244170055&page="
        url = url_lovelyz + str(num_page)
        driver.get(url)

        # get list of contents including image
        contents_img = {}

        contents = driver.find_elements_by_css_selector("table > tbody > tr:not(.notice):not(.notice_expand)")

        print(len(contents))

        for content in contents:
            try:
                content.find_element_by_css_selector("td.title > img")
                bIsImg = True
            except:
                bIsImg = False

            if bIsImg == True:
                link_content_img = content.find_element_by_css_selector("td.title > a:nth-child(2)").get_attribute("href")
                contents_img[link_content_img.split("=")[-1]] = link_content_img

        print("link : ", len(contents_img))

        # download image in list
        for name_content, link_content_img in contents_img.items():

            # save_content에 해당 자료가 있는 지 확인
            if name_content in list_save_contents:
                print("skip")
                continue
            else:
                with open("img/list.txt", "a") as f:
                    f.write(name_content+"\n")
                    total_update_content += 1
                    print("write")

            th_down = threading.Thread(target=download_image, args = (name_content, link_content_img))
            th_down.start()

    if total_update_content != 0:
        now_time = datetime.datetime.now()
        msg = "[{}. {} .{} - {} :{}]새로운 러블리즈 게시물 총 {}개가 추가되었습니다.^^".format(now_time.year, now_time.month, now_time.day, now_time.hour, now_time.minute, total_update_content)
        send_slack(msg)

    driver.close()


def download_image(name_content, link_content_img):
    driver = webdriver.Chrome()
    driver.get(link_content_img)

    time.sleep(1)

    article = driver.find_element_by_css_selector("#content article")
    imgs = article.find_elements_by_css_selector("img")

    print("img :", len(imgs))

    link_content_img.split("=")[-1]
    num_img = 0

    for img in imgs:
        link_img = img.get_attribute("src")
        extension = link_img.split(".")[-1]
        filename = "img/{}-{}.{}".format(name_content, num_img, extension)
        urllib.request.urlretrieve(link_img, filename)
        num_img += 1

    print("end crawler")
    driver.close()

def send_slack(msg):
    webhook_url = "https://hooks.slack.com/services/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"

    payload = {
        "channel" : "#general",
        "icon_emoji" : ":star-struck:",
        "text" : msg,
        "username" : "Lovelyz_bot"
    }

    response = requests.post(
        webhook_url,
        data = json.dumps(payload),
    )

    print(response)

get_img_Lovelyz(1, 5)
