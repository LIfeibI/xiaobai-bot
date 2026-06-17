import subprocess,threading,time,json,sys,os,webbrowser
from flask import Flask,request
from openai import OpenAI
import hashlib,xml.etree.ElementTree as ET,requests

WECHAT_APP_ID="wx3dffeebce55d5f08"
WECHAT_APP_SECRET="8b50e3…188d"
WECHAT_TOKEN="xiaobai2024"
MIMO_API_KEY="tp-cbe8tzyt96h3oagymzuh2uy5vf3q2qzpj4231xpomoz4l5o7"
MIMO_BASE_URL="https://token-plan-cn.xiaomimimo.com/v1"
MIMO_MODEL="mimo-v2.5-pro"

app=Flask(__name__)
mimo_client=OpenAI(api_key=MIMO_API_KEY,base_url=MIMO_BASE_URL)
user_conv={}
SYSTEM_PROMPT="你是小白，专业AI助手。能力：问答、代码、分析、翻译。简洁高效，500字以内。"

def get_token():
    try:
        r=requests.get(f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}",timeout=10)
        return r.json().get("access_token")
    except:return None

def chat(uid,msg):
    if uid not in user_conv:user_conv[uid]=[{"role":"system","content":SYSTEM_PROMPT}]
    msgs=user_conv[uid];msgs.append({"role":"user","content":msg})
    if len(msgs)>20:msgs=[msgs[0]]+msgs[-16:]
    user_conv[uid]=msgs
    try:
        r=mimo_client.chat.completions.create(model=MIMO_MODEL,msgs=msgs,max_tokens=1000)
        reply=r.choices[0].message.content;msgs.append({"role":"assistant","content":reply});return reply
    except:return "小白开小差了，稍后再试～"

def verify(sig,ts,nonce):
    params=sorted([WECHAT_TOKEN,ts,nonce])
    return hashlib.sha1("".join(params).encode()).hexdigest()==sig

@app.route("/wx",methods=["GET","POST"])
def wx():
    if request.method=="GET":
        s=request.args.get("signature","");t=request.args.get("timestamp","");n=request.args.get("nonce","");e=request.args.get("echostr","")
        return e if verify(s,t,n) else ("error",403)
    else:
        try:
            root=ET.fromstring(request.data.decode());mt=root.find("MsgType").text;fu=root.find("FromUserName").text;tu=root.find("ToUserName").text
            if mt=="text":
                c=root.find("Content").text;reply=chat(fu,c)
                return f'<xml><ToUserName><![CDATA[{fu}]]></ToUserName><FromUserName><![CDATA[{tu}]]></FromUserName><CreateTime>{int(time.time())}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[{reply}]]></Content></xml>'
            elif mt=="event" and root.find("Event").text=="subscribe":
                return f'<xml><ToUserName><![CDATA[{fu}]]></ToUserName><FromUserName><![CDATA[{tu}]]></FromUserName><CreateTime>{int(time.time())}</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[你好！我是小白🤖\n直接发消息给我就行！]]></Content></xml>'
            return "success"
        except:return "success"

@app.route("/")
def idx():return "小白运行中🤖"

def run_server():
    print("🚀服务器启动中...");app.run(host="0.0.0.0",port=80,debug=False)

def run_ngrok():
    time.sleep(3);print("🌐启动ngrok...")
    subprocess.Popen(["ngrok","http","80","--log=stdout"],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    time.sleep(5)
    try:
        r=requests.get("http://localhost:4040/api/tunnels",timeout=5);t=r.json().get("tunnels",[])
        if t:
            url=t[0].get("public_url","")
            if url:
                print(f"\n{'='*50}\n✅公网地址:{url}\n🔗回调地址:{url}/wx\n{'='*50}")
                print(f"\n📋微信配置:\n   URL:{url}/wx\n   Token:xiaobai2024\n   EncodingAESKey:点随机生成")
                webbrowser.open("https://developers.weixin.qq.com");return url
    except:pass
    print("⚠️获取ngrok地址失败");return None

if __name__=="__main__":
    print("🤖小白一键启动")
    t1=threading.Thread(target=run_server,daemon=True);t1.start()
    url=run_ngrok()
    if url:
        print("\n🎉成功！不要关闭此窗口");[time.sleep(1) for _ in iter(int,1)]
    else:print("❌失败，请检查ngrok");input()