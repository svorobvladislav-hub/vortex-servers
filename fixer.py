import requests, re, time, os
from github import Github

REPO = "svorobvladislav-hub/vortex-servers"
FILE = "config.txt"

GT = "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"
GM = "AIzaSyAB8RN6Lt92deKl3cP9GzT-OMdwm_ggNb-Ai_6e0bR8Jmc63liQ"
DS = "sk-5173119b8956417babf12bf875eaafe2"
HF = "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"

def ok(d):
    try:
        requests.get(f"https://{d}", timeout=3)
        return True
    except:
        return False

def ask_gemini(c):
    try:
        d = {"contents":[{"parts":[{"text":f"Give ONLY vless:// link for {c}"}]}]}
        r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GM}", json=d, timeout=10)
        if r.status_code==200:
            t = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            m = re.search(r'vless://[^\s]+', t)
            if m: return m.group(0)
    except: pass
    return None

def ask_deepseek(c):
    try:
        h = {"Authorization":f"Bearer {DS}","Content-Type":"application/json"}
        d = {"model":"deepseek-chat","messages":[{"role":"user","content":f"Give ONLY vless:// link for {c}"}]}
        r = requests.post("https://api.deepseek.com/v1/chat/completions", headers=h, json=d, timeout=10)
        if r.status_code==200:
            t = r.json()["choices"][0]["message"]["content"]
            m = re.search(r'vless://[^\s]+', t)
            if m: return m.group(0)
    except: pass
    return None

def ask_hf(c):
    try:
        h = {"Authorization":f"Bearer {HF}"}
        r = requests.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1", headers=h, json={"inputs":f"vless:// link for {c}"}, timeout=10)
        if r.status_code==200:
            t = r.json()[0]["generated_text"]
            m = re.search(r'vless://[^\s]+', t)
            if m: return m.group(0)
    except: pass
    return None

def fix():
    g = Github(GT)
    r = g.get_repo(REPO)
    c = r.get_contents(FILE)
    old = c.decoded_content.decode()
    new = old
    for l in old.split('\n'):
        if 'vless://' in l and '@' in l:
            dm = re.search(r'@([^:]+)', l).group(1)
            cn = l.split('#')[-1] if '#' in l else '...'
            if not ok(dm):
                res = ask_gemini(cn) or ask_deepseek(cn) or ask_hf(cn)
                if res:
                    new = new.replace(l, res)
                    print(f"Fixed {cn}")
    if new != old:
        r.update_file(FILE, "Auto-fix", new, c.sha)

while True:
    fix()
    time.sleep(1800)
