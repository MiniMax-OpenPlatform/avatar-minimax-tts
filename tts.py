import requests
import json

api_key = 'api_key'    #请输入您的api_key


url = "https://api.minimax.chat/v1/t2a_v2"

payload = json.dumps({
  "model": "speech-02-hd",
  #"stream": True,
  "text": "师傅您好,我是小明,请问我可以为您做什么?",
  "voice_setting": {
    "voice_id": "male-qn-qingse",
  }

})
headers = {
  'Authorization': f'Bearer {api_key}',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, stream=True, headers=headers, data=payload)
parsed_json = json.loads(response.text)

# 获取audio字段的值
audio_value = bytes.fromhex(parsed_json['data']['audio'])
output_file = 'output.mp3'
with open(output_file, 'wb') as f:
    f.write(audio_value)
    print(f"音频文件已保存到: {output_file}")
    print("trace_id", response.headers.get("Trace-Id"))
