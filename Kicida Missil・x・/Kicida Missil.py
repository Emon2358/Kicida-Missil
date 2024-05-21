from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import speech_recognition as sr
import time
import requests
from io import BytesIO
from pydub import AudioSegment
from selenium.webdriver.chrome.options import Options
def print_ascii_art():
    art = """
    ██╗  ██╗██╗ ██████╗ ██╗ ██████╗  █████╗     ███╗   ███╗██╗███████╗███████╗██╗  ██╗     
    ██║ ██╔╝██║██╔════╝ ██║ ██   ██╗██╔══██╗    ████╗ ████║██║██╔════╝██╔════╝██║  ██║     
    █████╔╝ ██║██║      ██║ ██   ██╔███████║    ██╔████╔██║██║███████╗███████║██║  ██║     
    ██╔═██╗ ██║██║      ██║ ██   ██╗██╔══██║    ██║╚██╔╝██║██║╚════██║╚════██║██║  ██║     
    ██║  ██╗██║╚██████╗ ██║ ██████╔║██║  ██║    ██║ ╚═╝ ██║██║███████║███████║██║  ███████╗
    ╚═╝  ╚═╝╚═╝╚═════╝  ╚═╝  ╚═╝╚═╝╚═╝   ╚═╝    ╚═╝╚═╝╚══════╝╚══════╝╚═╝ ╚══════╝╚═╝   ╚═╝
    """
    print(art)
print_ascii_art()
def recognize(audio_data):
    r = sr.Recognizer()
    with BytesIO(audio_data) as audio_file:
        audio = AudioSegment.from_file(audio_file, format="mp3")
    with sr.AudioFile(audio.export(format="wav")) as source:
        audio = r.record(source)
    return r.recognize_google(audio)

def solve_captcha(driver):
    try:
        # reCAPTCHAのiframeに切り替える
        print("reCAPTCHAのiframeに切り替え中...")
        captcha_frame = WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@title='reCAPTCHA']"))
        )
        print("reCAPTCHAのiframeに切り替えました")

        # reCAPTCHAのチェックボックスがクリック可能になるのを待ってクリックする
        print("reCAPTCHAのチェックボックスを待機中...")
        recaptcha_checkbox = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))
        )
        recaptcha_checkbox.click()
        time.sleep(1)
        print("reCAPTCHAのチェックボックスをクリックしました")

        # 音声チャレンジのiframeに切り替える
        print("音声チャレンジのiframeに切り替え中...")
        driver.switch_to.default_content()
        audio_challenge_frame = WebDriverWait(driver, 20).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[starts-with(@src, 'https://www.google.com/recaptcha/api2/bframe?')]"))
        )
        print("音声チャレンジのiframeに切り替えました")

        # 音声チャレンジのボタンをクリックする
        print("音声チャレンジボタンを待機中...")
        audio_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "recaptcha-audio-button"))
        )
        print("音声チャレンジボタンを見つけました、クリックしています...")
        audio_button.click()
        time.sleep(1)
        print("音声チャレンジボタンをクリックしました")

        # 音声ファイルのURLを取得してダウンロードする
        print("音声ファイルのURLを取得中...")
        audio_src = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "audio-source"))
        ).get_attribute("src")
        print(f"音声ファイルのURL: {audio_src}")

        audio_data = requests.get(audio_src).content
        answer = recognize(audio_data)

        # テキスト入力欄に解答を入力して検証する
        print("解答を入力して検証中...")
        audio_response_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "audio-response"))
        )
        audio_response_field.send_keys(answer)
        
        input("回答を入力し、Enterキーを押してください...")
        
        verify_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "recaptcha-verify-button"))
        )
        verify_button.click()
        time.sleep(1)

        # reCAPTCHAが正常に解決されるまで待機する
        driver.switch_to.default_content()
        while True:
            driver.switch_to.frame(captcha_frame)
            if driver.find_element(By.ID, "recaptcha-anchor").get_attribute("aria-checked") == "true":
                break
            driver.switch_to.default_content()
            time.sleep(1)

        print("reCAPTCHAが正常に解決されました")
        return answer
    except Exception as e:
        print(f"CAPTCHAの解決中にエラーが発生しました: {e}")
        return None

def manually_solve_captcha(driver):
    input("キャプチャを手動で解決し、Enterを押して続行してください...")



options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")  # ヘッドレスモードを使用する場合はコメントを外す

# ChromeDriverを起動（パスを指定しない）
driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com/recaptcha/api2/demo")

# 初期のreCAPTCHAを解決する
captcha_response = solve_captcha(driver)
driver.switch_to.default_content()

# チャレンジのiframeに切り替えてチャレンジを解決する
if captcha_response:
    print("チャレンジのiframeに切り替え中...")
    challenge_frame = WebDriverWait(driver, 20).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[starts-with(@src,'https://www.google.com/recaptcha/api2/bframe?')]"))
    )
    print("チャレンジのiframeに切り替えました")
    manually_solve_captcha(driver)  # ユーザーの手動介入が必要です
    challenge_response = solve_captcha(driver)
    driver.switch_to.default_content()

    if challenge_response:
        print(captcha_response + "|" + challenge_response)

        # 成功した場合、指定されたページに移動
        # ここに送信ボタンのクリックを追加
        submit_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "submit"))
        )
        submit_button.click()
    else:
        print("チャレンジのCAPTCHAの解決に失敗しました。")
else:
    print("初期のCAPTCHAの解決に失敗しました。")
driver.quit()