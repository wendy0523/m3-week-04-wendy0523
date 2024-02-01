from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)


#Channel Access Token
line_bot_api = LineBotApi(os.getenv('YOUR_CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('YOUR_CHANNEL_SECRET'))
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

#OpenAi
def generate_response(prompt, role="user"):

    response = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "你是一個很有用的AI幫手"},
        {"role": "user", "content": prompt}
      ]
    )

    return response.choices[0].message.content

# @app.route("/", methods=['POST'])
# def home():
#     return "<h1>AI-CAT</h1>"

#監聽line POST 請求 ，交給handler處理
# @app.route("/callback", methods=['POST'])
# def callback():
#     signature = request.headers['X-Line-Signature']
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     try:
#         handler.handle(body, signature)
#     except InvalidSignatureError:
#         app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
#         abort(400)

#     return 'OK'
@app.route("/callback", methods=['GET', 'POST'])
def callback():
    if request.method == 'POST':
        # 處理 POST 請求
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)
        app.logger.info("Request body: " + body)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return 'OK'
    elif request.method == 'GET':
        # 處理 GET 請求（用於驗證）
        # 在這裡返回 Line 平台提供的驗證 token
        return request.args.get('hub.challenge', '')
    else:
        abort(405)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.lower()
    if msg.startswith('/echo'):
        #/echo 開頭，回傳訊息中去掉 /echo 部分的文字
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=msg[6:]))
    elif msg.startswith('/q'):
        response = generate_response(msg[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    elif msg.startswith('/t'):
        response = generate_response("請幫我翻譯繁體中文"+ msg[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    elif msg.startswith('/e'):
        response = generate_response("請幫我翻譯英文"+ msg[3:])
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    elif msg.startswith('/ghost'):
        ghost = "請講30字以上的鬼故事，請使用正體中文"
        response = generate_response(ghost)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    elif msg.startswith('/joke'):
        joke = "請講冷笑話，請使用正體中文"
        response = generate_response(joke)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    elif msg.startswith('/ls'):
        ls = "1./echo 指令：重複回覆user輸入訊息  2./q 指令:回答問題 3./t 指令:翻譯成中文 4./e 指令:翻譯成英文 5./ghost 指令:講鬼故事給你聽owo 6./joke指令:講冷笑話給你聽:) "
        response = generate_response(ls)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response))
    else:
        response = '輸入 /ls 會給指令'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
        
    # # with ApiClient(configuration) as api_client:
    #     line_bot_api = MessagingApi(api_client)
    #     line_bot_api.reply_message_with_http_info(
    #         ReplyMessageRequest(
    #             reply_token=event.reply_token,
    #             messages=[TextMessage(text=event.message.text)]
    #         )
    #     )

if __name__ == "__main__":
    app.run(debug=True)