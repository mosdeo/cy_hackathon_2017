#====================== for Line Bot SDK =================
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
#===========================================================

from flask import Flask, request, render_template
import logging
import logging.config
import yaml
from kh import predict

app = Flask(__name__, static_url_path='')

my_CHANNEL_ACCESS_TOKEN = 'Nejo7izbm3I94qsFsvVeHrJmQ8KGVHQWjk0Z7RdFBDzrUzPCGwmrYNzO7LG/a+ZiNkcDGStjtvcvy8ASyXPEYy8JsrevPPBALpRLkWstbkNb3G702j+eILRA+tm4Ikt/ElI6UPZ8fv4gT7BRdwHq9AdB04t89/1O/w1cDnyilFU=' #open('channel_access_keys/channel_access_token.ini').read()
print(my_CHANNEL_ACCESS_TOKEN)

my_CHANNEL_SECRET = '123b64f1cbb589326196a5683e98f663' #open("channel_access_keys/channel_access_secret.ini").read()
print(my_CHANNEL_SECRET)

line_bot_api = LineBotApi(my_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(my_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=predict(event.message.text)))


try:
    with open('logging.yml') as fd:
        conf = yaml.load(fd)
        logging.config.dictConfig(conf['logging'])
except OSError:
    conf = None

logger = logging.getLogger('app')
input_logger = logging.getLogger('app.input')

if conf:
    logger.info('logging.yml found, applying config')
    logger.debug(conf)
else:
    logger.info('logging.yml not found')


from uuid import uuid4

@app.route('/')
def root():
    uuid = request.cookies.get('uuid', uuid4())
    resp = app.send_static_file('index.html')
    resp.set_cookie('uuid', str(uuid))
    return resp

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    rec = {'ip': ip(),
           'uuid': request.cookies.get('uuid'),
           'data': request.form.get('in')}
    input_logger.info(rec)
    return predict(request.form.get('in'))

def ip():
    return request.environ.get('REMOTE_ADDR', request.remote_addr)

if __name__ == '__main__':
    app.run()

