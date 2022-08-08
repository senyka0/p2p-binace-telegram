import telebot
import requests
import pandas as pd
from time import sleep

telegramId = 501179740

symbols = ["USDT"] #crypto currencies
fiats = ["UAH", "EUR"] #fiat currencies
transAmount = ["4000", "100"] #amount for eachh fiat currency
payTypes = ['Privatbank', 'Monobank', 'Oschadbank', 'izibank', 'sportbank', "revolut"] #pay types


bot = telebot.TeleBot('') #put your telegrem bot keys

while True:
    df = pd.DataFrame()
    for symbol in symbols:
        for idx, fiat in enumerate(fiats):
            try:
                res = requests.post("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search", json = {'asset':symbol, 'countries': [], 'fiat': fiat, 'page': 1, 'payTypes': payTypes, 'publisherType': None, 'rows': 10, 'transAmount': transAmount[idx], 'tradeType': 'BUY'}).json()['data']
                res2 = requests.post("https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search", json = {'asset':symbol, 'countries': [], 'fiat': fiat, 'page': 1, 'payTypes': payTypes, 'publisherType': None, 'rows': 10, 'transAmount': transAmount[idx], 'tradeType': 'SELL'}).json()['data']
                data = [{'tradeType': 'BUY', 'asset': i['adv']['asset'], 'fiatUnit': i['adv']['fiatUnit'], 'price': i['adv']['price'], 'minSingleTransAmount': i['adv']['minSingleTransAmount'], 'maxSingleTransAmount': i['adv']['maxSingleTransAmount'], 'tradeMethods': [x['payType'] for x in i['adv']['tradeMethods']], 'platform': 'Binance P2P'} for i in res]
                data2 = [{'tradeType': 'SELL', 'asset': i['adv']['asset'], 'fiatUnit': i['adv']['fiatUnit'], 'price': i['adv']['price'], 'minSingleTransAmount': i['adv']['minSingleTransAmount'], 'maxSingleTransAmount': i['adv']['maxSingleTransAmount'], 'tradeMethods': [x['payType'] for x in i['adv']['tradeMethods']], 'platform': 'Binance P2P'} for i in res2]
                tempDf = pd.DataFrame(data=data).sort_values(by=['price'])
                tempDf2 = pd.DataFrame(data=data2).sort_values(by=['price'], ascending=False)
                df = pd.concat([df, tempDf, tempDf2], axis=0)

            except Exception as e:
                print(e)
                continue
    df = df.reset_index(drop=True)
    for fiat in fiats:
      Min = df[(df['tradeType'] == 'BUY')&(df['fiatUnit']==fiat)].sort_values(by=['price']).iloc[0]
      Max = df[(df['tradeType'] == 'SELL')&(df['fiatUnit']==fiat)].sort_values(by=['price'], ascending=False).iloc[0]
      if (float(Max['price']) - float(Min['price']))/float(Min['price'])*100 > 1:
          bot.send_message(f'✅ New trade found ✅ \n \n💵Profit: {(float(Max["price"]) - float(Min["price"]))/float(Min["price"])*100} % \n \n🟢\n{Min.to_string()} \n \n🔴\n{Max.to_string()}')
    sleep(10)
