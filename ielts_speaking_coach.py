"""
雅思口语智能教练 - IELTS Speaking Coach
通过与 AI 考官对话提升雅思口语水平

功能：
- 自由对话 / Part 1 / Part 2 / Part 3 / 完整模拟考
- 语音输入（浏览器语音识别）+ 语音输出（浏览器语音合成）
- 回答反馈与四维度评分
- 多后端：Pollinations.ai(免费无需Key) / Ollama(本地免费) / 火山方舟/OpenAI(付费)
"""
import streamlit as st
import streamlit.components.v1 as components
import requests
import json
import os
import time
from datetime import datetime

# ===================== 配置 =====================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), ".ielts_speaking_config.json")

# 后端配置
BACKENDS = {
    "blockrun": {
        "label": "🆓 BlockRun (免费，无需Key，推荐)",
        "default_url": "https://blockrun.ai/api/v1",
        "default_model": "nvidia/muse-glimmer-30b",
        "needs_key": False,
        "format": "openai",
    },
    "pollinations": {
        "label": "🆓 Pollinations.ai (免费，无需Key)",
        "default_url": "https://text.pollinations.ai",
        "default_model": "openai",
        "needs_key": False,
        "format": "pollinations",  # 直接返回文本
    },
    "ollama": {
        "label": "🖥️ Ollama (本地，免费)",
        "default_url": "http://localhost:11434/v1",
        "default_model": "llama3.1",
        "needs_key": False,
        "format": "openai",
    },
    "volcengine": {
        "label": "🌋 火山方舟 (豆包，需Key)",
        "default_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_model": "doubao-1-5-pro-32k-250115",
        "needs_key": True,
        "format": "openai",
    },
    "openai": {
        "label": "🔵 OpenAI (需Key)",
        "default_url": "https://api.openai.com/v1",
        "default_model": "gpt-4o-mini",
        "needs_key": True,
        "format": "openai",
    },
}

# ===================== 系统提示词 =====================
SYSTEM_PROMPTS = {
    "free_chat": """You are 格林 (Green), a friendly, patient English conversation partner helping an IELTS candidate practice speaking. Your name is 格林 (Green).

Rules:
- Introduce yourself as 格林 at the start.
- Have a natural, casual conversation on everyday topics (travel, food, hobbies, work, culture, etc.).
- Keep your replies brief (2-3 sentences) and ALWAYS end with a follow-up question to keep the conversation going.
- Speak naturally as a native English speaker would. Use everyday vocabulary, not overly formal language.
- IMPORTANT: After your response, gently point out any grammar or spelling mistakes the user made. Use this exact format on a new line:
  "💡 Correction: [explain the mistake and the correct version briefly]"
  If there are no mistakes, do NOT include the correction line. Only point out real errors, not stylistic preferences.
- Vary your topics and questions; don't repeat the same question.
""",

    "part1": """You are 格林 (Green), a professional IELTS Speaking examiner conducting Part 1 of the IELTS Speaking test. Your name is 格林.

Part 1 is the Introduction and Interview (4-5 minutes).

Rules:
- Start with a brief greeting: "Hi, I'm 格林. May I have your full name please?" and ask where they are from.
- Then ask 3-4 questions about everyday topics: home, family, studies, work, hobbies, food, weather, transport, etc.
- Ask ONE question at a time and WAIT for the candidate's answer before asking the next.
- Keep questions natural, clear, and at an appropriate level.
- After each of the candidate's answers, add a brief correction line at the end if they made grammar/spelling mistakes, using this format on a new line:
  "💡 Correction: [brief explanation of the mistake and correct version]"
  If no mistakes, skip this line. Do not give scores or detailed feedback during the test.
- After 3-4 questions, you may tell the candidate Part 1 is finished if they want to move on.
- Be friendly but professional, like a real examiner.
""",

    "part2": """You are 格林 (Green), a professional IELTS Speaking examiner conducting Part 2 (Individual Long Turn) of the IELTS Speaking test. Your name is 格林.

Part 2 rules:
1. Present a cue card with a topic and 3-4 bullet points of what to include.
2. Tell the candidate they have 1 minute to prepare and should speak for 1-2 minutes.
3. Wait for the candidate to deliver their talk.
4. After they finish, ask 1-2 brief rounding-off follow-up questions.

Cue card topics should cover common IELTS Part 2 themes: a person, a place, an object, an event, an activity, etc.

Format the cue card clearly. After the candidate's talk, ask 1-2 follow-up questions. If the candidate made grammar/spelling mistakes, add a brief correction line at the end using this format on a new line:
"💡 Correction: [brief explanation and correct version]"
If no mistakes, skip this line. Do not give scores or detailed feedback during the test.
""",

    "part3": """You are 格林 (Green), a professional IELTS Speaking examiner conducting Part 3 (Two-way Discussion) of the IELTS Speaking test. Your name is 格林.

Part 3 rules:
- Ask 4-5 abstract, in-depth discussion questions related to a topic.
- Questions should be more challenging than Part 1: ask the candidate to discuss opinions, compare, speculate about the future, give examples, and evaluate.
- Ask ONE question at a time and WAIT for the answer.
- You may ask brief follow-up questions to probe deeper.
- After each answer, if the candidate made grammar/spelling mistakes, add a brief correction line at the end:
  "💡 Correction: [brief explanation and correct version]"
  If no mistakes, skip this line. Do not give scores or detailed feedback during the test.
- Be professional and neutral.
""",

    "full_test": """You are 格林 (Green), a professional IELTS Speaking examiner conducting a COMPLETE IELTS Speaking mock test. Your name is 格林.

Follow this structure strictly:
1. Part 1 (Introduction): Greet as 格林, ask name/hometown, then 3-4 everyday questions. Ask one at a time.
2. Part 2 (Long Turn): Present a cue card with a topic + bullet points. Say they have 1 minute to prepare and should speak 1-2 minutes. Wait for their talk. Then ask 1-2 follow-up questions.
3. Part 3 (Discussion): Ask 4-5 abstract, in-depth questions on a related topic. Ask one at a time.

Rules:
- Ask ONE question at a time and WAIT for the answer before continuing.
- After each answer, if the candidate made grammar/spelling mistakes, add a brief correction line at the end:
  "💡 Correction: [brief explanation and correct version]"
  If no mistakes, skip this line. Do not give scores during the test.
- Be professional and friendly, like a real examiner.
- At the end, the user may ask for feedback, which you will provide separately.
""",
}

FEEDBACK_PROMPT = """You are an expert IELTS Speaking examiner. Based on the conversation history above, evaluate the candidate's speaking performance.

Provide feedback in English (with occasional Chinese explanations for key points) in this format:

## Overall Band Score: X / 9

### 1. Fluency and Coherence: X / 9
- Comments: ...

### 2. Lexical Resource: X / 9
- Comments: ...

### 3. Grammatical Range and Accuracy: X / 9
- Comments: ...

### 4. Pronunciation: X / 9
- (Note: assess based on text patterns and likely pronunciation challenges)
- Comments: ...

### Top 3 Improvement Suggestions:
1. ...
2. ...
3. ...

Be honest, specific, and constructive. Quote the candidate's actual words where helpful.
"""

# ===================== 持久化配置 =====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# ===================== LLM 调用 =====================
def call_llm(backend, api_key, base_url, model, messages, temperature=0.7, max_tokens=1500):
    """调用 LLM，支持多种后端。返回文本或 [API_ERROR] 开头的错误。"""
    cfg = BACKENDS.get(backend, BACKENDS["blockrun"])
    fmt = cfg["format"]

    try:
        if fmt == "pollinations":
            # Pollinations.ai: POST {messages, model} 直接返回文本
            payload = {"messages": messages, "model": model}
            resp = requests.post(
                f"{base_url.rstrip('/')}/",
                json=payload,
                timeout=90,
            )
            resp.raise_for_status()
            text = resp.text
            # 有时返回 JSON 字符串，有时纯文本
            try:
                data = resp.json()
                if isinstance(data, dict) and "choices" in data:
                    return data["choices"][0]["message"]["content"]
                if isinstance(data, str):
                    return data
                if isinstance(data, dict) and "response" in data:
                    return data["response"]
            except Exception:
                pass
            return text

        else:
            # OpenAI 兼容格式（Ollama / 火山方舟 / OpenAI）
            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            resp = requests.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError:
        detail = ""
        try:
            detail = resp.json().get("error", {}).get("message", "")
        except Exception:
            detail = (resp.text or "")[:300]
        return f"[API_ERROR] HTTP {resp.status_code}: {detail}"
    except requests.exceptions.ConnectionError:
        hint = ""
        if backend == "ollama":
            hint = " 请确认 Ollama 已启动（运行 ollama serve）。"
        return f"[API_ERROR] 无法连接到 {backend} 服务器。{hint}"
    except requests.exceptions.Timeout:
        return "[API_ERROR] 请求超时，请稍后重试。"
    except Exception as e:
        return f"[API_ERROR] {str(e)}"

# ===================== 语音组件 =====================
def voice_input_widget(lang="en-US", key="voice_input"):
    """语音识别组件：点击按钮说话，返回识别文本。支持英语/中文。"""
    html = f"""
    <div style="display:flex;align-items:center;gap:10px;">
      <button id="mic_btn_{key}" 
        onclick="toggleListen()" 
        style="padding:10px 20px;font-size:16px;border-radius:8px;border:none;background:#1E88E5;color:white;cursor:pointer;">
        🎤 点击说话
      </button>
      <span id="status_{key}" style="font-size:14px;color:#666;"></span>
    </div>
    <script>
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      let recognition = null;
      let listening = false;
      
      if (SR) {{
        recognition = new SR();
        recognition.lang = '{lang}';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onresult = (e) => {{
          if (e.results[0].isFinal) {{
            const transcript = e.results[0][0].transcript;
            Streamlit.setComponentValue(transcript);
            document.getElementById('status_{key}').textContent = '✓ 已识别: ' + transcript;
          }}
        }};
        
        recognition.onerror = (e) => {{
          document.getElementById('status_{key}').textContent = '错误: ' + e.error;
          listening = false;
          document.getElementById('mic_btn_{key}').textContent = '🎤 点击说话';
        }};
        
        recognition.onend = () => {{
          listening = false;
          document.getElementById('mic_btn_{key}').textContent = '🎤 点击说话';
        }};
      }} else {{
        const btn = document.getElementById('mic_btn_{key}');
        btn.textContent = '⚠ 浏览器不支持语音识别';
        btn.disabled = true;
        btn.style.background = '#999';
      }}
      
      function toggleListen() {{
        if (!recognition) return;
        if (listening) {{
          recognition.stop();
        }} else {{
          try {{
            recognition.start();
            listening = true;
            document.getElementById('mic_btn_{key}').textContent = '⏹ 停止';
            document.getElementById('status_{key}').textContent = '正在听...请开始说话';
          }} catch(err) {{
            document.getElementById('status_{key}').textContent = '启动失败: ' + err.message;
          }}
        }}
      }}
    </script>
    """
    return components.html(html, height=60)

def speak_text(text, lang="en-US", rate=1.0):
    """语音合成：让浏览器朗读文本，读完自动开始听用户说话"""
    if not text:
        return
    escaped = json.dumps(text[:2000])
    st.html(
        f"""
        <script>
        try {{
          window.speechSynthesis.cancel();
          const u = new SpeechSynthesisUtterance({escaped});
          u.lang = '{lang}';
          u.rate = {rate};
          u.pitch = 1.0;
          u.onend = function() {{
            // AI 说完，自动进入听用户说话状态
            if (window.__voiceAutoListen) window.__voiceAutoListen();
          }};
          window.speechSynthesis.speak(u);
          // 立即触发状态检测
          if (window.__voiceAutoListen) window.__voiceAutoListen();
        }} catch(e) {{}}
        </script>
        """,
        unsafe_allow_javascript=True,
    )

# ===================== 会话管理 =====================
def init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = "free_chat"
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = SYSTEM_PROMPTS["free_chat"]
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""
    if "last_ai_msg_idx" not in st.session_state:
        st.session_state.last_ai_msg_idx = -1

def reset_conversation(mode):
    st.session_state.messages = []
    st.session_state.mode = mode
    st.session_state.system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["free_chat"])
    st.session_state.feedback = ""
    st.session_state.last_ai_msg_idx = -1
    st.session_state.need_greeting = True

def build_messages():
    """构建发给 LLM 的消息列表：系统提示 + 历史对话"""
    msgs = [{"role": "system", "content": st.session_state.system_prompt}]
    for m in st.session_state.messages:
        msgs.append({"role": m["role"], "content": m["content"]})
    return msgs

# ===================== UI =====================
MODE_LABELS = {
    "free_chat": "💬 自由对话",
    "part1": "🎯 Part 1 日常问答",
    "part2": "🃏 Part 2 话题陈述",
    "part3": "💭 Part 3 深度讨论",
    "full_test": "📝 完整模拟考",
}

def sidebar():
    with st.sidebar:
        st.title("🟢 格林 · 口语教练")
        st.caption("Green · IELTS Speaking Coach")
        st.markdown("---")

        saved = load_config()

        # --- 练习模式 + 开始按钮 ---
        st.subheader("🎯 练习模式")
        mode = st.selectbox(
            "选择模式",
            list(MODE_LABELS.keys()),
            format_func=lambda m: MODE_LABELS[m],
            index=list(MODE_LABELS.keys()).index(st.session_state.get("mode", "free_chat")),
            label_visibility="collapsed",
        )
        st.session_state.mode = mode
        if st.button("▶ 开始", use_container_width=True, type="primary"):
            reset_conversation(mode)
        st.markdown("---")

        # --- 语音设置（侧边栏唯一常驻区） ---
        st.subheader("🔊 语音设置")

        stt_lang = st.selectbox(
            "识别语言",
            ["en-US", "en-GB", "zh-CN"],
            index=["en-US", "en-GB", "zh-CN"].index(saved.get("stt_lang", "en-US")),
            format_func=lambda x: {"en-US": "英语 (美音)", "en-GB": "英语 (英音)", "zh-CN": "中文"}[x],
        )
        tts_lang = st.selectbox(
            "朗读语言",
            ["en-US", "en-GB", "zh-CN"],
            index=["en-US", "en-GB", "zh-CN"].index(saved.get("tts_lang", "en-US")),
            format_func=lambda x: {"en-US": "英语 (美音)", "en-GB": "英语 (英音)", "zh-CN": "中文"}[x],
        )
        tts_rate = st.slider("朗读语速", 0.5, 1.5, 1.0, 0.1)
        auto_tts = st.checkbox("自动朗读 AI 回复", value=True)

        st.session_state.stt_lang = stt_lang
        st.session_state.tts_lang = tts_lang
        st.session_state.tts_rate = tts_rate
        st.session_state.auto_tts = auto_tts

        # 持久化语音设置
        cfg = load_config()
        cfg.update({"stt_lang": stt_lang, "tts_lang": tts_lang})
        save_config(cfg)

        # --- 高级设置（后端配置，默认折叠） ---
        with st.expander("⚙️ 高级设置（AI 后端）", expanded=False):
            backend = st.selectbox(
                "选择后端",
                list(BACKENDS.keys()),
                format_func=lambda k: BACKENDS[k]["label"],
                index=list(BACKENDS.keys()).index(saved.get("backend", "blockrun")),
            )
            bcfg = BACKENDS[backend]
            st.session_state.backend = backend

            api_key = ""
            if bcfg["needs_key"]:
                api_key = st.text_input("API Key", value=saved.get("api_key", ""), type="password")

            base_url = st.text_input("API 地址", value=saved.get("base_url", bcfg["default_url"]))
            model = st.text_input("模型", value=saved.get("model", bcfg["default_model"]))

            if st.button("💾 保存后端配置", use_container_width=True):
                save_config({
                    "backend": backend, "api_key": api_key,
                    "base_url": base_url, "model": model,
                })
                st.success("已保存")

        # 若未在 session_state 中设置，从保存的配置读取
        if "backend" not in st.session_state:
            st.session_state.backend = saved.get("backend", "blockrun")

        st.markdown("---")
        st.caption("💡 浏览器需使用 Chrome / Edge 以支持语音识别")

    # 返回后端配置（从保存的配置读取）
    cur = load_config()
    backend = st.session_state.get("backend", "blockrun")
    bcfg = BACKENDS[backend]
    api_key = cur.get("api_key", "")
    base_url = cur.get("base_url", bcfg["default_url"])
    model = cur.get("model", bcfg["default_model"])
    return api_key, base_url, model

def chat_interface(api_key, base_url, model):
    backend = st.session_state.get("backend", "blockrun")
    stt_lang = st.session_state.get("stt_lang", "en-US")

    # --- 绿色小球：语音对话核心 ---
    st.html(f"""
    <style>
    @keyframes pulse-glow {{
        0%, 100% {{ box-shadow: 0 0 20px 5px rgba(34,197,94,0.4); transform: scale(1); }}
        50% {{ box-shadow: 0 0 45px 15px rgba(34,197,94,0.8); transform: scale(1.08); }}
    }}
    @keyframes listen-pulse {{
        0%, 100% {{ box-shadow: 0 0 20px 5px rgba(239,68,68,0.5); transform: scale(1); }}
        50% {{ box-shadow: 0 0 50px 20px rgba(239,68,68,0.9); transform: scale(1.12); }}
    }}
    @keyframes float-ball {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-6px); }}
    }}
    .green-ball {{
        width: 80px; height: 80px; border-radius: 50%; cursor: pointer;
        background: radial-gradient(circle at 35% 30%, #86efac 0%, #22c55e 40%, #15803d 80%, #14532d 100%);
        margin: 0 auto;
        animation: float-ball 3s ease-in-out infinite;
        transition: all 0.3s;
    }}
    .green-ball.speaking {{
        animation: pulse-glow 0.9s ease-in-out infinite, float-ball 3s ease-in-out infinite;
    }}
    .green-ball.listening {{
        background: radial-gradient(circle at 35% 30%, #fca5a5 0%, #ef4444 40%, #b91c1c 80%, #7f1d1d 100%);
        animation: listen-pulse 0.7s ease-in-out infinite;
    }}
    .ball-status {{
        text-align:center; color:#888; font-size:13px; margin-top:6px; height:18px;
    }}
    </style>
    <div style="text-align:center;margin-bottom:14px;">
        <div class="green-ball" id="ai-ball" title="点击开始说话"></div>
        <div class="ball-status" id="ball-status">点击格林开始对话</div>
    </div>
    <script>
    (function() {{
        const ball = document.getElementById('ai-ball');
        const status = document.getElementById('ball-status');
        if (!ball) return;

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let listening = false;

        if (SR) {{
            recognition = new SR();
            recognition.lang = '{stt_lang}';
            recognition.continuous = false;
            recognition.interimResults = false;
        }}

        function setStatus(text) {{ if (status) status.textContent = text; }}

        function startListening() {{
            if (!recognition || listening) return;
            try {{
                recognition.start();
                listening = true;
                ball.classList.add('listening');
                ball.classList.remove('speaking');
                setStatus('正在听你说...');
            }} catch(e) {{}}
        }}

        function stopListening() {{
            if (recognition && listening) {{
                try {{ recognition.stop(); }} catch(e) {{}}
            }}
            listening = false;
            ball.classList.remove('listening');
        }}

        ball.addEventListener('click', function() {{
            if (listening) {{
                stopListening();
                setStatus('已停止');
            }} else {{
                // 如果 AI 正在说话，先停止
                if (window.speechSynthesis) window.speechSynthesis.cancel();
                startListening();
            }}
        }});

        if (recognition) {{
            recognition.onresult = function(e) {{
                const text = e.results[0][0].transcript;
                if (!text) return;
                setStatus('识别到: ' + text);
                const input = document.querySelector('input[placeholder="输入你的回答..."]');
                if (input) {{
                    // 用原生 setter 触发 React 状态更新
                    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    setter.call(input, text);
                    input.dispatchEvent(new Event('input', {{bubbles: true}}));
                    input.dispatchEvent(new Event('change', {{bubbles: true}}));
                    setStatus('正在发送...');
                    setTimeout(() => {{
                        const sendBtn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === '发送');
                        if (sendBtn) {{
                            sendBtn.click();
                        }} else {{
                            setStatus('未找到发送按钮，请手动发送');
                        }}
                    }}, 400);
                }} else {{
                    setStatus('未找到输入框');
                }}
            }};
            recognition.onerror = function(event) {{
                listening = false;
                ball.classList.remove('listening');
                setStatus('识别出错(' + (event.error || 'unknown') + ')，点格林重试');
            }};
            recognition.onend = function() {{
                listening = false;
                ball.classList.remove('listening');
            }};
        }}

        // 监听 TTS 状态：AI 说话时小球发光；说完自动开始听
        window.__voiceAutoListen = function() {{
            if (!recognition) return;
            if (window.speechSynthesis && window.speechSynthesis.speaking) {{
                ball.classList.add('speaking');
                setStatus('AI 正在说话...');
                const check = setInterval(() => {{
                    if (!window.speechSynthesis.speaking) {{
                        clearInterval(check);
                        ball.classList.remove('speaking');
                        // AI 说完，自动开始听用户说话
                        setTimeout(() => startListening(), 400);
                    }}
                }}, 150);
            }}
        }};
    }})();
    </script>
    """, unsafe_allow_javascript=True)

    # 点「开始」后格林先主动打招呼
    if st.session_state.get("need_greeting") and not st.session_state.messages:
        st.session_state.need_greeting = False
        with st.spinner("格林正在准备..."):
            greeting_msgs = [{"role": "system", "content": st.session_state.system_prompt}]
            reply = call_llm(backend, api_key, base_url, model, greeting_msgs, temperature=0.8)
        if not reply.startswith("[API_ERROR]"):
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.session_state.last_ai_msg_idx = len(st.session_state.messages) - 1
        else:
            st.error(reply)

    # 显示历史消息（自定义气泡）
    for m in st.session_state.messages:
        content = m["content"].replace("\n", "<br>")
        if m["role"] == "user":
            st.html(
                '<div style="display:flex;justify-content:flex-end;margin:8px 0;">'
                '<div style="background:#1a3a1a;color:#fff;padding:10px 16px;border-radius:18px 18px 4px 18px;max-width:70%;word-wrap:break-word;">'
                + content + '</div></div>',
                unsafe_allow_javascript=True,
            )
        else:
            st.html(
                '<div style="display:flex;align-items:flex-start;gap:10px;margin:8px 0;">'
                '<div style="width:32px;height:32px;border-radius:50%;background:#22c55e;flex-shrink:0;"></div>'
                '<div style="background:#1c1c1c;color:#e0e0e0;padding:10px 16px;border-radius:18px 18px 18px 4px;max-width:70%;word-wrap:break-word;">'
                + content + '</div></div>',
                unsafe_allow_javascript=True,
            )

    # 自动朗读最新 AI 消息
    ai_msgs = [i for i, m in enumerate(st.session_state.messages) if m["role"] == "assistant"]
    if ai_msgs and st.session_state.get("auto_tts", True):
        latest_idx = ai_msgs[-1]
        if latest_idx != st.session_state.get("last_ai_msg_idx", -1):
            st.session_state.last_ai_msg_idx = latest_idx
            speak_text(
                st.session_state.messages[latest_idx]["content"],
                lang=st.session_state.get("tts_lang", "en-US"),
                rate=st.session_state.get("tts_rate", 1.0),
            )

    # --- 输入区 ---
    input_col, btn_col = st.columns([5, 1])
    with input_col:
        user_text = st.text_input(
            "你的回答",
            key="user_msg_input",
            placeholder="输入你的回答...",
            label_visibility="collapsed",
        )
    with btn_col:
        send_clicked = st.button("发送", use_container_width=True, type="primary")

    # 处理输入
    if send_clicked and user_text:
        input_text = user_text.strip()
        if input_text:
            st.session_state.messages.append({"role": "user", "content": input_text})
            # 立即显示用户气泡
            safe_user = input_text.replace("\n", "<br>")
            st.html(
                '<div style="display:flex;justify-content:flex-end;margin:8px 0;">'
                '<div style="background:#1a3a1a;color:#fff;padding:10px 16px;border-radius:18px 18px 4px 18px;max-width:70%;word-wrap:break-word;">'
                + safe_user + '</div></div>',
                unsafe_allow_javascript=True,
            )

            # 调用 LLM
            reply = ""
            try:
                with st.spinner("AI 思考中..."):
                    reply = call_llm(
                        backend, api_key, base_url, model,
                        build_messages(),
                        temperature=0.8,
                    )
            except Exception as e:
                reply = f"[API_ERROR] 异常: {e}"

            if reply.startswith("[API_ERROR]"):
                st.error(reply)
                st.session_state.messages.pop()
            else:
                st.session_state.messages.append({"role": "assistant", "content": reply})
                # 立即显示 AI 气泡
                safe_ai = reply.replace("\n", "<br>")
                st.html(
                    '<div style="display:flex;align-items:flex-start;gap:10px;margin:8px 0;">'
                    '<div style="width:32px;height:32px;border-radius:50%;background:#22c55e;flex-shrink:0;"></div>'
                    '<div style="background:#1c1c1c;color:#e0e0e0;padding:10px 16px;border-radius:18px 18px 18px 4px;max-width:70%;word-wrap:break-word;">'
                    + safe_ai + '</div></div>',
                    unsafe_allow_javascript=True,
                )
                if st.session_state.get("auto_tts", True):
                    ai_idx = len(st.session_state.messages) - 1
                    st.session_state.last_ai_msg_idx = ai_idx
                    speak_text(
                        reply,
                        lang=st.session_state.get("tts_lang", "en-US"),
                        rate=st.session_state.get("tts_rate", 1.0),
                    )

# ===================== 主程序 =====================
def main():
    st.set_page_config(
        page_title="格林 · 口语教练",
        page_icon="🎙️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # --- 黑色主题 ---
    st.html("""
    <style>
    .stApp, .stApp > div { background-color: #000000 !important; }
    section[data-testid="stSidebar"] { background-color: #0a0a0a !important; }
    section[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label { color: #e0e0e0 !important; }
    .stMarkdown { color: #e0e0e0 !important; }
    /* 输入框 */
    .stTextInput input { background-color: #1a1a1a !important; color: #fff !important; border: 1px solid #333 !important; border-radius: 20px !important; padding: 10px 16px !important; }
    .stTextInput input:focus { border-color: #22c55e !important; box-shadow: none !important; }
    /* 下拉框 */
    .stSelectbox [data-baseweb="select"] > div { background-color: #1a1a1a !important; border-color: #333 !important; border-radius: 20px !important; }
    .stSelectbox [data-baseweb="select"] span, .stSelectbox [data-baseweb="select"] div { color: #e0e0e0 !important; }
    /* 下拉框弹出列表 */
    ul[role="listbox"] { background-color: #1a1a1a !important; border: 1px solid #333 !important; }
    ul[role="listbox"] li { background-color: #1a1a1a !important; color: #e0e0e0 !important; }
    ul[role="listbox"] li[aria-selected="true"] { background-color: #14532d !important; }
    ul[role="listbox"] li:hover { background-color: #14532d !important; }
    /* 按钮 */
    .stButton button { background-color: #1a1a1a !important; color: #fff !important; border: 1px solid #333 !important; border-radius: 20px !important; }
    .stButton button:hover { background-color: #2a2a2a !important; }
    /* 隐藏 Streamlit 默认装饰，但保留侧边栏展开按钮 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { background: transparent !important; }
    header [data-testid="stDecoration"] { display: none !important; }
    /* 侧边栏展开/收起按钮样式 */
    [data-testid="collapsedControl"] { background: #0a0a0a !important; }
    [data-testid="collapsedControl"] button { background: #1a1a1a !important; color: #22c55e !important; border: 1px solid #333 !important; border-radius: 10px !important; }
    /* 紧凑布局 */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 800px !important; }
    /* 去掉 radio 的边框背景 */
    .stRadio > div { background: transparent !important; }
    /* 全局所有白色背景元素强制改深色 */
    [data-testid="stHorizontalBlock"] > div { background: transparent !important; }
    </style>
    """, unsafe_allow_javascript=True)
    init_session()
    api_key, base_url, model = sidebar()
    backend = st.session_state.get("backend", "blockrun")
    cfg = BACKENDS.get(backend, BACKENDS["blockrun"])

    # 只有需要 Key 的后端才检查
    if cfg["needs_key"] and not api_key:
        st.warning(f"⚠️ 选择了「{cfg['label']}」，请在左侧输入 API Key。")
        st.info("💡 或者切换到「🆓 Pollinations.ai」后端，完全免费、无需 Key，立即可用。")
        return

    chat_interface(api_key, base_url, model)

if __name__ == "__main__":
    main()
