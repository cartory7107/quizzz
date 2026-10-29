import os
import sys
import requests

# এনভায়রনমেন্ট ভ্যারিয়েবল থেকে তথ্য সংগ্রহ
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_RECIPIENT_NUMBER = os.getenv("WHATSAPP_RECIPIENT_NUMBER")

OLLAMA_API_URL = "https://ollama.com/api/chat"
OLLAMA_MODEL = "gemma4:31b-cloud"


def generate_morning_content() -> str:
    """Ollama Cloud API এবং gemma4:31b-cloud দিয়ে বাংলা ধাঁধা ও শুভকামনা তৈরি করে।"""
    if not OLLAMA_API_KEY:
        raise ValueError("OLLAMA_API_KEY সেট করা নেই!")

    prompt = (
        "তুমি একজন চমৎকার বাংলা কন্টেন্ট ক্রিয়েটর। "
        "আজকের জন্য একটি আকর্ষণীয় ও বুদ্ধিদীপ্ত বাংলা মজার ধাঁধা তৈরি করো (ধাঁধার কোনো উত্তর দেবে না, উত্তর সম্পূর্ণ গোপন থাকবে)। "
        "ধাঁধার ঠিক নিচে কর্মদিবসের জন্য একটি অনুপ্রেরণামূলক উক্তি এবং সফল কর্মদিবসের শুভকামনা যুক্ত করো।\n\n"
        "আউটপুট ফরম্যাট হুবহু নিচের মতো হবে:\n\n"
        "☀️ সুপ্রভাত!\n\n"
        "🧩 **আজকের মজার ধাঁধা:**\n"
        "[ধাঁধার বিবরণ]\n"
        "*(উত্তর নিয়ে কিছুক্ষণ ভাবুন, মেধা শাণিত করুন!)*\n\n"
        "💡 **আজকের অনুপ্রেরণা:**\n"
        "[কাজ ও সাফল্যের জন্য ১-২ লাইনের শক্তিশালী অনুপ্রেরণামূলক কথা বা উক্তি]\n\n"
        "✨ আপনার আজকের দিনটি আনন্দময়, কর্মমুখর ও সফল হোক!"
    )

    headers = {
        "Authorization": f"Bearer {OLLAMA_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {
                "role": "system",
                "content": "You are an inspiring Bengali assistant creating morning riddles and daily work motivation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    print(f"[*] Ollama Cloud API কল করা হচ্ছে (Model: {OLLAMA_MODEL})...")
    response = requests.post(OLLAMA_API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()
    generated_text = data.get("message", {}).get("content", "").strip()

    if not generated_text:
        raise ValueError("Ollama থেকে কোনো টেক্সট পাওয়া যায়নি!")

    print("[✓] মেসেজ সফলভাবে তৈরি হয়েছে।")
    return generated_text


def send_telegram_message(message: str) -> bool:
    """টেলিগ্রাম চ্যানেলে মেসেজ পাঠায়।"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Telegram ক্রেডেনশিয়াল অনুপস্থিত। স্কিপ করা হলো।")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            print("[✓] টেলিগ্রামে মেসেজ সফলভাবে পৌঁছেছে।")
            return True
        
        # Markdown পার্সিং ব্যর্থ হলে সাধারণ প্লেইন টেক্সট হিসেবে রিট্রাই
        payload.pop("parse_mode", None)
        retry_res = requests.post(url, json=payload, timeout=20)
        if retry_res.status_code == 200:
            print("[✓] টেলিগ্রামে প্লেইন টেক্সটে মেসেজ সফলভাবে পৌঁছেছে।")
            return True
        print(f"[!] Telegram ত্রুটি: {retry_res.text}")
        return False
    except Exception as e:
        print(f"[!] Telegram রিকোয়েস্ট এক্সেপশন: {e}")
        return False


def send_whatsapp_message(message: str) -> bool:
    """মেটা হোয়াটসঅ্যাপ ক্লাউড এপিআই দিয়ে মেসেজ পাঠায়।"""
    if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID or not WHATSAPP_RECIPIENT_NUMBER:
        print("[!] WhatsApp ক্রেডেনশিয়াল অনুপস্থিত। স্কিপ করা হলো।")
        return False

    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": WHATSAPP_RECIPIENT_NUMBER.strip().replace("+", ""),
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code in [200, 201]:
            print("[✓] হোয়াটসঅ্যাপে মেসেজ সফলভাবে পৌঁছেছে।")
            return True
        print(f"[!] WhatsApp Cloud API ত্রুটি: HTTP {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"[!] WhatsApp রিকোয়েস্ট এক্সেপশন: {e}")
        return False


def main():
    try:
        content = generate_morning_content()
        tg_ok = send_telegram_message(content)
        wa_ok = send_whatsapp_message(content)

        if not tg_ok and not wa_ok:
            print("[!] কোনো প্ল্যাটফর্মেই মেসেজ পাঠানো যায়নি।")
            sys.exit(1)

        print("[✓] আজকের অটোমেশন সফলভাবে সম্পন্ন হয়েছে।")
    except Exception as err:
        print(f"[CRITICAL ERROR]: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
