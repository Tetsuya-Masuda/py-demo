# -*- coding: utf-8 -*-
import sys
import numpy as np
from gensim.models import word2vec
from flask import Flask, render_template,request,session
from collections import Counter
import requests
import json

# 定数群
MIZUHO_MODEL_FILE_PATH = '/home/bddadmin/nlc/newsrelease/models/mizuhonews.model'
BTMU_MODEL_FILE_PATH = '/home/bddadmin/nlc/newsrelease/models/btmunews.model'
SMBC_MODEL_FILE_PATH = '/home/bddadmin/nlc/newsrelease/models/smbcnews.model'
RELATED_WORD_COUNT = 20

BANK_ID_MIZUHO = 1
BANK_ID_BTMU = 2
BANK_ID_SMBC = 4

# 自身の名称を app という名前でインスタンス化する
app = Flask(__name__)
app.secret_key = 'Jbs123456789'

# ここからウェブアプリケーション用のルーティングを記述
# リクエスト受け付けた後、ルーティングメソッドの前のイベントハンドラ
@app.before_request
def before_request():
    Flask.Mizuho = word2vec.Word2Vec.load(MIZUHO_MODEL_FILE_PATH)
    Flask.BTMU = word2vec.Word2Vec.load(BTMU_MODEL_FILE_PATH)
    Flask.SMBC = word2vec.Word2Vec.load(SMBC_MODEL_FILE_PATH)

# ホームページ
@app.route('/')
def home_page():
    return render_template('index.html',title='ようこそ')

@app.route('/word_cloud_manual',methods=['GET'])
def word_cloud_manual():

    # GETで渡されたキーワードの取得
    request_parameter = request.args.get("searchword")
    related_words = get_relatedword_allbank(request_parameter)

    if 'relatedwords' in session:
        before_related_words = session['relatedwords']
        after_related_words = merge_relatedwords(related_words,before_related_words)
    else:
        after_related_words = related_words

    jqcloud_param = convert_jQCloud_parameter(after_related_words,True)

    session['relatedwords'] = after_related_words

    jqcloud_param_sorted = sorted(jqcloud_param,key=lambda k:k['weight'],reverse=True)

    return json.dumps(jqcloud_param_sorted)
  

@app.route('/word_cloud_def', methods=['GET'])
def word_cloud_def():
    request_parameter = request.args.get("searchword")
    related_words = get_relatedword_allbank(request_parameter)

    # jQCloudのパラメータに変換する
    jqcloud_param = convert_jQCloud_parameter(related_words,False)

    return json.dumps(jqcloud_param)

@app.route('/word_cloud_clear', methods=['GET'])
def word_cloud_clear():
    session.pop('relatedwords',None)
    return json.dumps('True')

# ここから内部メソッド

def get_relatedword_allbank(keyword):

    # みずほモデルより関連するワードを取得する
    words_mizuho = get_relatedword(keyword,BANK_ID_MIZUHO)
    # BTMUモデルより関連するワードを取得する
    words_btmu = get_relatedword(keyword,BANK_ID_BTMU)
    # SMBCモデルより関連するワードを取得する
    words_smbc = get_relatedword(keyword,BANK_ID_SMBC)

    merged_words_1 = merge_relatedwords(words_mizuho,words_btmu)
    all_bank_words = merge_relatedwords(merged_words_1,words_smbc)

    return all_bank_words


def get_bankmodel(bankid):
    if bankid == BANK_ID_MIZUHO:
        return Flask.Mizuho
    elif bankid == BANK_ID_BTMU:
        return Flask.BTMU
    elif bankid == BANK_ID_SMBC:
        return Flask.SMBC
    else:
        return None

def get_relatedword(positiveword,bankid):

    param_positive = tolist_forw2vwordparam(positiveword)
    bankmodel = get_bankmodel(bankid)
    for p in param_positive:
        if p not in bankmodel.wv.vocab:
            return None

    related_words = \
    bankmodel.wv.most_similar(positive = param_positive,topn = RELATED_WORD_COUNT)

    result = {}
    for word in related_words:
        item = {}
        item['bankid'] = bankid
        item['wordcount'] = get_wordcount(word[0],bankmodel)
        result[word[0]] = item
    
    return result

def merge_relatedwords(words1,words2):

    if words1 == None and words2 == None:
        return None
    elif words1 == None and words2 != None:
        return words2
    elif words1 != None and words2 == None:
        return words1

    merged_words = {}
    # words1
    for item1 in words1.items():
        merged_words[item1[0]] = item1[1]

    # words2
    for item2 in words2.items():
        if item2[0] in merged_words:
            item = merged_words[item2[0]]
            item['wordcount'] += item2[1]['wordcount']
            item['bankid'] = merge_bankid(item['bankid'], item2[1]['bankid'])
            merged_words[item2[0]] = item
        else:
            merged_words[item2[0]] = item2[1]

    return merged_words

def merge_bankid(x,y):
    bankid = x
    if x == y:
        return bankid
    
    if (BANK_ID_MIZUHO + BANK_ID_BTMU + BANK_ID_SMBC) < x + y:
        return x 

    if x == BANK_ID_MIZUHO or x == BANK_ID_BTMU or x == BANK_ID_SMBC:
        bankid = x + y
    elif x == (BANK_ID_MIZUHO + BANK_ID_BTMU) and y == BANK_ID_SMBC:
        bankid = x + y
    elif x == (BANK_ID_MIZUHO + BANK_ID_SMBC) and y == BANK_ID_BTMU:
        bankid = x + y
    elif x == (BANK_ID_BTMU + BANK_ID_SMBC) and y == BANK_ID_MIZUHO:
        bankid = x + y    

    return bankid

# w2vへのパラメータの型に変換する
def tolist_forw2vwordparam(sentence):
    result = []
    if -1 < sentence.find(','):
        for word in sentence.split(','):
            result.append(word)
    else:
        result.append(sentence)
    return result

# モデルから単語の出現回数を取得する
def get_wordcount(word,model):
    return model.wv.vocab[word].count

def convert_jQCloud_parameter(items,isCustom):
    params = []
    for item in items:
        param = {}
        param['text'] = item
        param['weight'] = items[item]['wordcount']
        if isCustom == True:
            # fontsize
            param['fontsize'] = 20
            # fontcolor
            colorstring = '#000000'
            if items[item]['bankid'] == BANK_ID_MIZUHO:
                colorstring = '#000080' #darkblue
            elif items[item]['bankid'] == BANK_ID_BTMU:
                colorstring = '#8b0000' #darkred
            elif items[item]['bankid'] == BANK_ID_SMBC:
                colorstring = '#006400' #darkgreen
            elif items[item]['bankid'] == BANK_ID_MIZUHO + BANK_ID_BTMU:
                colorstring = '#8b008b' #darkmagenta
            elif items[item]['bankid'] == BANK_ID_MIZUHO + BANK_ID_SMBC:
                colorstring = '#87cefa' #lightskyblue
            elif items[item]['bankid'] == BANK_ID_BTMU + BANK_ID_SMBC:
                colorstring = '#fcc800' #chromeyellow
            elif items[item]['bankid'] == BANK_ID_MIZUHO + BANK_ID_BTMU + BANK_ID_SMBC:
                colorstring = '#504946' #taupe
            param['color'] = colorstring

            #param['link'] = 'http://github.com/mistic100/jQCloud'
            linkparam = {}
            #linkparam['href'] = 'http://github.com/mistic100/jQCloud'
            link_url = ''
            if items[item]['bankid'] == BANK_ID_MIZUHO:
                link_url = 'https://search.www.mizuhobank.co.jp/search?site=K2TPFCDI&design=1&group=1&charset=UTF-8&count=&pdf=&field=&mapion=0&query=' + item + '&category=2'
            elif items[item]['bankid'] == BANK_ID_BTMU:
                link_url = 'http://bk-mufg.jeevessolutions.jp/AJSearch.asp?sid=132_40_115_252_211_20170822120642_1442853&origin=1&type=&aj_charset=UTF-8&ask=' + item
            elif items[item]['bankid'] == BANK_ID_SMBC:
                link_url = 'http://pro.syncsearch.jp/search?site=O2RW5PF1&charset=UTF-8&design=3&query=' + item + '&submit=%8C%9F%8D%F5'
                
            #linkparam['href'] = link_url
            #linkparam['target'] = '_blank'

            linkparam['href'] = 'javascript:opennewssite("' + item + '","' + str(items[item]['bankid']) + '");'
            linkparam['id'] = 'word_cloud_word'
            param['link'] = linkparam
            #param['handlers'] = '''click:function(){ alert('Hoge')}'''
            
        params.append(param)
    return params

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に