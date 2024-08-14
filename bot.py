import pandas as pd
from lxml import html
import telebot
from telebot.types import Message
from config import *
import requests
import sqlite3
import re
from statistics import mean


def newData(path: str):
    results = []
    
    try:
        excelFile = pd.read_excel(path)
    
        for i, title in enumerate(excelFile["title"]):
            url = excelFile["url"][i]
            xpath = excelFile["xpath"][i]
            
            response = requests.get(url)
            
            tree = html.fromstring(response.text)
            
            try:
                result = float(" ".join("".join(re.findall(r"[\d]+[\.,]{0,1}\d*", i.text)).replace(",", ".") for i in tree.xpath(xpath)))
            except TypeError:
                result = "NoData"
            
            results.append(result)
            
            with sqlite3.connect("data.db") as con:
                cur = con.cursor()
                
                cur.execute("""CREATE TABLE IF NOT EXISTS data (
                    title TEXT,
                    url TEXT,
                    xpath TEXT,
                    price FLOAT
                )""")
                
                cur.execute(f"INSERT INTO data (title, url, xpath, price) VALUES ('{title}', '{url}', '{xpath}', {result})")

        print("Задача успешно выполнена :)")
    except ValueError:
        print("Файл не корректен :(")
    
    return results


def main():
    bot = telebot.TeleBot(token)
    
    @bot.message_handler(content_types=["document"])
    def checkMessages(message: Message):
        byte_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
        
        path_file = f"files/{message.document.file_id}.xlsx"
        
        with open(path_file, "wb") as new_file:
            new_file.write(byte_file)
        
        new_data = newData(path_file)
        
        print("Средняя цена:", mean(new_data))
        print("===========")
        
        bot.send_message(message.chat.id, "\n".join(str(d) for d in new_data))
        bot.send_message(message.chat.id, f"Средняя цена: {mean(new_data)}")

    bot.infinity_polling()


if __name__ == "__main__":
    main()

