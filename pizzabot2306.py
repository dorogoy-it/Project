import telebot
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from telebot import types

bot = telebot.TeleBot("1092393023:AAFMo27hmQDkPrLuZ5K8UhIaFXS49EdTrTo")

conn = sqlite3.connect('C:\\bdbot\\sqlite3\\SQLiteStudio\\pizzas.db', check_same_thread=False)
cursor = conn.cursor()
a = []
b = ["Заказать", "Отмена"]
client = []


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item8 = types.KeyboardButton("хочу пиццу")
    markup.add(item8)
    bot.send_message(message.chat.id, "Привет! Я ПиццаБот. Если ты хочешь заказать пиццу, то нажми кнопку 'хочу пиццу' внизу экрана.", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
        if message.chat.type == "private":
            if message.text.lower() == "хочу пиццу":
                cursor.execute("SELECT denomination FROM pizza;")
                den_results = cursor.fetchall()

                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

                for i in range(len(den_results)):
                    a.append(den_results[i][0])

                button_list = [types.KeyboardButton(text=x) for x in a]
                keyboard.add(*button_list)
                msg = bot.send_message(message.chat.id, "Вот что у нас есть:", reply_markup=keyboard)
                bot.register_next_step_handler(msg, choose_a_pizza)

@bot.callback_query_handler(func=lambda message: True)
def choose_a_pizza(message):
    for i in range(len(a)):
        if message.text == a[i]:
            global choose
            choose = message.text
            cursor.execute("SELECT denomination FROM pizza;")
            name_results = cursor.fetchall()
            name_results_item = name_results[i][0]

            cursor.execute("SELECT description FROM pizza;")
            des_results = cursor.fetchall()
            des_results_item = des_results[i][0]

            cursor.execute("SELECT link_to_pic FROM pizza;")
            link_results = cursor.fetchall()
            link_results_item = link_results[i][0]
            img = open(link_results_item, 'rb')
            bot.send_photo(message.from_user.id, img)

            cursor.execute("SELECT price FROM pizza;")
            price_results = cursor.fetchall()
            global price_results_item
            price_results_item = price_results[i][0]

            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button_list = [types.KeyboardButton(text=x) for x in b]
            keyboard.add(*button_list)
            msg = bot.send_message(message.from_user.id, "Название: " + str(name_results_item) + "\nОписание: " + str(des_results_item) + "\nЦена: " + str(price_results_item) + "руб.", reply_markup=keyboard)
            bot.register_next_step_handler(msg, taking_order)

@bot.callback_query_handler(func=lambda message: True)
def taking_order(message):
    if message.text == b[0]:
        msg = bot.send_message(message.from_user.id, "Введите ваш номер телефона", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_count)
    elif message.text == b[1]:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_list = [types.KeyboardButton(text=x) for x in a]
        keyboard.add(*button_list)
        msg = bot.send_message(message.chat.id, "Вот что у нас есть:", reply_markup=keyboard)
        bot.register_next_step_handler(msg, choose_a_pizza)


def get_count(message):
    global tel
    tel = message.text
    tsifra = bot.send_message(message.from_user.id, "Сколько пицц вы хотите?")
    bot.register_next_step_handler(tsifra, get_name)

def get_name(message):
    global count
    count = int(message.text)
    imya = bot.send_message(message.from_user.id, "Как вас зовут?")
    bot.register_next_step_handler(imya, get_street)

def get_street(message):
    global name
    name = message.text

    ulitsa = bot.send_message(message.from_user.id, "На какой улице живёте?")
    bot.register_next_step_handler(ulitsa, get_home)

def get_home(message):
    global street
    street = message.text
    global hour
    hour = message.text
    dom = bot.send_message(message.from_user.id, "В каком доме живёте?")
    bot.register_next_step_handler(dom, get_delivery)

def get_delivery(message):
    global home
    home = message.text
    chas = bot.send_message(message.from_user.id, "Укажите время доставки")
    bot.register_next_step_handler(chas, get_delivery1)
def get_delivery1(message):
    global time
    time = message.text
    cursor.execute("INSERT INTO clients VALUES(?,?,?,?)", (tel, name, street, home))
    conn.commit()
    price = price_results_item * count
    bot.send_message(message.from_user.id, "К оплате " + str(price) + " руб.")
    msg = MIMEText('Поступил заказ на ' + str(count) + " " + choose + " по адресу " + street + ", " + home  + " на время " + time + ". " + "Телефон заказчика " + tel, 'plain', 'utf-8')
    msg['Subject'] = Header('Додо Пицца', 'utf-8')
    msg['From'] = "dorogoymv@mail.ru"
    msg['To'] = "dorogoymv@gmail.com"

    smtpObj = smtplib.SMTP_SSL('smtp.mail.ru:465')
    smtpObj.login('dorogoymv@mail.ru', 'qC7nJQwEhDuWcMATmtAp')

    smtpObj.sendmail("dorogoymv@mail.ru","dorogoymv@gmail.com", msg.as_string())
    smtpObj.quit()

if __name__ == '__main__':
    bot.polling(none_stop=True)