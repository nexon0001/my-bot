import telebot
import random
import imaplib
import email
from email.header import decode_header
import threading

# ==================== CORRECT CREDENTIALS ====================
API_TOKEN = '6889587318:AAHbmqAhDDYRIZrl-Qnm7PiIUtDHU58YhN8'
bot = telebot.TeleBot(API_TOKEN)

IMAP_SERVER = 'mail.sudipbio.pro'
IMAP_USER = 'admin@sudipbio.pro'
IMAP_PASS = 'Sudip1221@'  # Updated with Capital S

MY_DOMAINS = ["sudipbio.pro"]

FIRST_PART = ["amit", "rahul", "rohit", "vikram", "tanmay", "sanjay", "deepak", "animesh", "alok", "abhi", "raj", "sunil", "ajay", "vijay", "pankaj"]
SECOND_PART = ["kumar", "singh", "sharma", "verma", "das", "mondal", "gupta", "roy", "sen", "joshi", "bose", "paul", "mishra", "yadav"]

def gen_automatic_indian_username():
    f = random.choice(FIRST_PART)
    s = random.choice(SECOND_PART)
    num = random.randint(10, 999)
    return f"{f}{s}{num}".lower().replace(" ", "")

# ==================== BOT COMMANDS ====================
@bot.message_handler(commands=['start', 'gen'])
def generate_mail(message):
    chat_id = message.chat.id
    username = gen_automatic_indian_username()
    domain = random.choice(MY_DOMAINS)
    fake_email = f"{username}@{domain}"
    
    markup = telebot.types.InlineKeyboardMarkup()
    refresh_btn = telebot.types.InlineKeyboardButton("🔄 Live OTP / Check Inbox", callback_data=f"chk_{fake_email}")
    markup.add(refresh_btn)
    
    bot.send_message(chat_id, f"🇮🇳 **Email Ready:** `{fake_email}`", parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('chk_'))
def check_otp_live(call):
    fake_email = call.data.split('_')[1]
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id, "⏳ Checking...")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select("Inbox")
        
        status, messages = mail.search(None, "ALL")
        mail_ids = messages[0].split()
        
        if not mail_ids:
            bot.send_message(chat_id, "📬 Inbox empty.")
            mail.logout()
            return
            
        found = False
        # Last 5 emails check karne ke liye
        for m_id in mail_ids[-5:]:
            res, msg_data = mail.fetch(m_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    if fake_email in str(msg.get("To")).lower():
                        subject, _ = decode_header(msg["Subject"])[0]
                        body = msg.get_payload(decode=True).decode(errors="ignore")
                        bot.send_message(chat_id, f"✨ **Mail Found!**\n\nSubject: {subject}\n\nContent:\n`{body[:200]}`", parse_mode="Markdown")
                        found = True
                        break
            if found: break
                
        if not found: bot.send_message(chat_id, "⏳ No mail yet.")
        mail.logout()
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {str(e)}")

# ==================== START BOT ====================
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling()
