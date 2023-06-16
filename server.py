from flask import Flask, render_template, redirect, request
import config
import requests
import urllib.parse

app = Flask(__name__)

@app.route("/")
def index():
    # 首页
    return render_template("login.html", client_id = config.CLIENT_ID)

@app.route("/login")
def login():
    # 登录入口，跳转到方糖通行证
    return redirect(
        config.HOST_1 + # https://oauth2.rdpstudio.top
        "/oauth2/auth" + # 授权入口
        "?client_id=" + config.CLIENT_ID + # client_id
        "&scope=user" + # scope
        "&state=some_state" + # state
        "&response_type=code" + # 目前只支持这个
        "&redirect_uri=" + urllib.parse.quote_plus("https://127.0.0.1:5001/callback") # 回调地址
    )

@app.route("/callback")
def callback():
    # 回调
    # 判断state是否相同
    state = request.args.get("state")
    if state != "some_state":
        return render_template("message.html", message = "<h1>state有误</h1>")
    # 判断是否有错误
    error = request.args.get("error")
    error_description = request.args.get("error_description")
    if error:
        return render_template("message.html", message = "<h1>error: " + error + "<br/>error_description: " + error_description + "</h1>")
    # 接收code
    code = request.args.get("code")
    if not code: # 如果没有code
        return render_template("message.html", message = "<h1>code不存在</h1>")
    # 交换Token
    res = requests.post(
        config.HOST_1 + # https://oauth2.rdpstudio.top
        "/oauth2/token", # 交换Token的API
        data = {
            "code": code, # 传入code
            "client_id": config.CLIENT_ID, # client_id
            "client_secret": config.CLIENT_SECRET, # client_secret
            "redirect_uri": "https://127.0.0.1:5001/callback", # 回调地址
            "grant_type": "authorization_code" # grant模式
        }
    )
    if res.status_code != 200: # 出现错误
        error = res.json()["error"]
        error_description = res.json()["error_description"]
        return render_template("message.html", message = "<h1>交换Token时错误<br/>error: " + error + "<br/>error_description: " + error_description + "</h1>")
    else:
        access_token = res.json()["access_token"] # 访问令牌
    # 获取用户信息
    res = requests.get(
        config.HOST_2 + # https://id.rdpstudio.top
        "/oauth2/api/v1/userInfo", # 获取用户信息的API
        headers= {
            "Authorization": "Bearer " + access_token # 传入访问令牌
        }
    )
    if res.status_code != 200: # 出现错误
        error = res.json()["error"]
        error_description = res.json()["error_description"]
        return render_template("message.html", message = "<h1>交换Token时错误<br/>error: " + error + "<br/>error_description: " + error_description + "</h1>")
    else:
        print(res.json())
    return render_template("message.html", message = "<h1>请查看服务器终端</h1>")

app.run(host="0.0.0.0", port=5001, debug=True, ssl_context="adhoc")