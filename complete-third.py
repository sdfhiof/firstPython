from cgitb import text
import speech_recognition as sr
from datetime import datetime
from pytz import timezone
from io import BytesIO
from navertts import NaverTTS
from pydub import AudioSegment
from pydub.playback import play
import requests
from collections.abc import Callable

def speech_to_text() -> str:
   recognizer = sr.Recognizer()
   microphone = sr.Microphone(device_index=1)

   with microphone as source:
      recognizer.adjust_for_ambient_noise(source) # noise check
      print('listening')
      audio = recognizer.listen(source)
   try:
      user_command = recognizer.recognize_google(audio, language="ko")
   except Exception as e:
      print("이해할 수 없습니다", e)    
   else:
      print(f"유저 입력 : {user_command}")
      return user_command
def text_to_speech(text :str) -> None:
   print(f"text_to_speech : {text}")
   tts = NaverTTS(text, lang="ko")
   fp = BytesIO()
   tts.write_to_fp(fp)
   fp = BytesIO(fp.getvalue())
   my_sound = AudioSegment.from_file(fp, format="mp3")
   play(my_sound)

def find_command_list(keywords: list[str], sentence: str) -> list[str]:
   print("find_command")
   user_command_list = []
   for k in keywords:
      if k in sentence:
         print(f"입력된 명령어 {k}")
         user_command_list.append(k)
   if not user_command_list:
      print("명령어 없음")
      user_command_list.append("none")
   return user_command_list
def find_city_list(keywords: list[str], sentence: str, default: str = "") -> list[str]:
   print("find_city")
   user_city_list = []
   for k in keywords:
      if k in sentence:
         print(f"입력된 지역 {k}")
         user_city_list.append(k)
   if not user_city_list:
      print(f"디폴트 지역 {default}")
      user_city_list.append(default)
   return user_city_list
def find_command(keywords: list[str], sentence: str) -> bool:
   found = [k for k in keywords if k in sentence]
   return True if found else False
def find_city_(keywords: list[str], sentence: str) -> bool:
   found = [k for k in keywords if k in sentence]
   return True if found else False

def report_time(user_command_city: str) -> None:
   print("report_time")
   tz = timezone(cities_dict[user_command_city])
   now_time = datetime.today().astimezone(tz)
   text_to_speech(f"{user_command_city}현재 시각 {now_time.hour}시 0분 {now_time.second}초 입니다.")
def report_date(user_command_city: str) -> None:
   print("report_date")
   days = ['월', '화', '수', '목', '금', '토', '일']
   tz = timezone(cities_dict[user_command_city])
   now_Date = datetime.today().astimezone(tz)        
   weekdays = days[now_Date.weekday()]
   text_to_speech(f"{user_command_city} 현재 {now_Date.year}년 {now_Date.month}월 {now_Date.day}일 {weekdays}요일 입니다.") 
def report_weather(user_command_city: str) -> None:
   print("report_weather")
   cities_dict = {"서울": "seoul", "부산" : "busan", "오사카" : "osaka","도쿄": "tokyo","후쿠오카": "fukuoka","삿포로": "sapporo", "오키나와" : "okinawa"}

   API_KEY = "e5d28b210ce477ee2b8f9486f021de75"
   BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
   LANGUAGE = "kr" 

   request_url = f"{BASE_URL}?appid={API_KEY}&q={cities_dict.get(user_command_city)}&lang={LANGUAGE}"

   print(request_url)
   response = requests.get(request_url)
   if response.status_code == 200:
      data = response.json()
      city_name = data['name']
      weather = data['weather'][0]['description']
      temperature = round(data["main"]["temp"] - 273.15, 2) 
      text_to_speech(f"현재 {city_name}의 날씨는 {weather} 로 온도는 {temperature}도 입니다.")
   else:
      print("An error occurred.", response.status_code)

def listen_report(command_callbacks: dict[str, Callable[[str], None]]) -> bool:
   print("listen_report")

   user_command = speech_to_text()

   if "종료" in user_command:
      text_to_speech('종료합니다')
      return False
   
   
   elif keyword := find_command(command_callbacks.keys(), user_command):
      for keyword in find_command_list(command_callbacks.keys(), user_command):
         for imported_city in find_city_list(cities_dict, user_command, "서울"):
            cammand_callbacks_city = []
            cammand_callbacks_city.append((cammand_callbacks_dict[keyword], imported_city))
            for callback, arg in cammand_callbacks_city:
               callback(arg)          
   
   else:
      text_to_speech("알 수 없는 명령입니다.")
   return True

cities_dict = {"서울": "Asia/Seoul","부산" : "Asia/Seoul", "오사카" : "Asia/Tokyo","도쿄": "Asia/Tokyo","후쿠오카": "Asia/Tokyo","삿포로": "Asia/Tokyo", "오키나와" : "Asia/Tokyo"}
cammand_callbacks_dict = {"시간" : report_time, "몇 시" : report_time, "날짜" : report_date, "날씨" : report_weather}
command_list = cammand_callbacks_dict.keys()

def main():
   while listen_report(cammand_callbacks_dict):
      continue

if __name__ == "__main__":
   main()