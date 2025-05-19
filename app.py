### 安裝函式庫 ###
from os
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
import requests

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    TemplateMessage, ConfirmTemplate, MessageAction,
    CarouselTemplate, CarouselColumn, URIAction, PostbackAction
)

import json
import random



### Crawler ###

def crawler(search_word):
  url = "https://taigitube.com/api/search"

  headers = {
      "User-Agent": "Mozilla/5.0",
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Origin": "https://taigitube.com",
      "Referer": "https://taigitube.com/",
  }

  # 注意：只需要這三個欄位（過多反而會錯）
  payload = {
      "query": search_word,  # 搜尋關鍵字
      "v": "",          # 可以留空
      "t": "0"          # 通常是影片時間篩選參數
  }

  response = requests.post(url, headers=headers, json=payload).json()

  reply = []
  # 如果 response 超過10個就隨機取出10個 (LineBot templete 最多只能10個)
  if len(response) > 10:
    response = random.sample(response, 10)

  for r in response:
    #print(r['video_name'])
    #print(r['transcript'])
    yt_url = 'https://youtu.be/watch?v=' + str(r['video_id']) + '&t=' + str(r['start_second']) + 's'
    photo_url = 'https://i.ytimg.com/vi/' + str(r['video_id']) + '/hqdefault.jpg'
    #print(yt_url)
    #print(photo_url)

    reply.append([r['video_name'], r['transcript'], yt_url, photo_url])


  return reply



### Line Bot ###
  
app = Flask(__name__)

configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
line_handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

@app.route('/')
def index():
    return 'TaigiTube LINE Bot is running!'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

      
        data = crawler(event.message.text)
        print(data)

        template_list = []
        for d in data:
            template_list.append(
                CarouselColumn(
                    thumbnail_image_url = d[3],
                    title = d[0],
                    text = d[1],
                    actions=[
                        URIAction(label = '「' + d[0] + '」的「' + event.message.text + '」怎麼講', uri = d[2])
                    ]
                )
            )
        reply = TemplateMessage(
            alt_text = '「' + event.message.text + '」怎麼講',
            template = CarouselTemplate(columns = template_list)
        )
        

        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    reply
                ]
            )
        )


if __name__ == "__main__":
    app.run()