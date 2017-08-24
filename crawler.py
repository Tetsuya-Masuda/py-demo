import urllib.request
from bs4 import BeautifulSoup
import sys
import os
import re

TMP_PDFFILE = 'tmppdf.pdf'

def get_newslinks(url,tag,tagclass):
    '''<a>タグのurlを取得します

    Keyword arguments:
    url -- 対象サイトのurl
    tag -- <a>タグが含まれるtag名
    tagclass -- tagに指定したclass名
    '''
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,'html.parser')
    elements = soup.findAll(tag,class_=tagclass)
    news = list()
    for element in elements:
        links = element.findAll('a')
        for link in links:
            # .pdfのリンクのみ取得する
            if link.attrs['href'].find('.pdf') > -1:
                link_info = list()
                link_info.append(link.text)
                link_info.append(link.attrs['href'])
                news.append(link_info)
    return news

def save_pdftext(inputfileuri,outputfilename):
    '''指定されたuri先のfileを、pdfファイルとして保存します

    Keyword arguments:
    inputfileuri -- 保存したいファイルのuri
    outputfilename -- 保存するファイル名
    '''
    #print(inputfileuri)
    if re.match('^http?\:\/\/',inputfileuri):
        with urllib.request.urlopen(inputfileuri) as response, open(TMP_PDFFILE,'wb') as output:
            output.write(response.read())
        inputfileuri = TMP_PDFFILE
        status = os.system('pdftotext {0} {1}'.format(inputfileuri, inputfileuri + '.txt'))
        if status != 0:
            print('Error.pdftotext return illegal status code ${0}'.format())
            sys.exit()
        if os.path.exists(TMP_PDFFILE):
            os.remove(TMP_PDFFILE)
        mpa = dict.fromkeys(range(32))
        with open(inputfileuri + '.txt') as input, open(outputfilename,'wt') as output:
            for line in input:
                if line.strip() == '':
                    output.write('\n')
                else:
                    output.write(line.rstrip().translate(mpa))
    else:
        return

def main():
    get_green_news_release()
    get_blue_news_release()
    get_red_news_relase()

def get_green_news_release():
    ''' 緑系のニュースリリースを取得します    
    '''
    # 3つの変数の値を指定してください。
    news_site_url = '{news_site_uri}' 
    pdf_uri_header = '{pdf_uri_header}'
    news_text_save_directory = '{local_directory}'

    # ニュースリンクを取得
    newslinks = get_newslinks(news_site_url,'p','paragraph')

    # ニュースリンク先のファイルをローカルに保存する
    for link in newslinks:
        if -1 < link[1].find('.pdf'):
            if -1 == link[1].find('investor') and -1 == link[1].find('about'):
                inputfileuri = pdf_uri_header + '/' + link[1]
                outputfilename = news_text_save_directory + '/' + link[1].split('/').replace('pdf','txt')
                save_pdftext(inputfileuri,outputfilename)

def get_blue_news_release():
    ''' 青系のニュースリリースを取得します
    '''

    # 3つの変数の値を指定してください。
    corprate_site = '{corporate_site_top_url}'
    news_text_save_directory = '{local_directory}'
    current_year_news_site_url = '{current_news_release_site_url}'

    # 当年分のニュースリリース情報を取得する
    current_year_newslinks = get_newslinks(current_year_news_site_url,'dl','newsFlat')
    for link in current_year_news_site_url:
        inputfileuri = corprate_site + link[1]
        outputfilename = news_text_save_directory + link[1].split('/').replace('pdf','txt')
        save_pdftext(inputfileuri,outputfilename)

    # 過去年のニュースリリース情報を取得する
    for target_year in range(2006,2017):
        past_year_newslinks = get_newslinks(current_year_news_site_url.replace('index',str(target_year)),'dl','newsFlat')
        for link in past_year_newslinks:
            inputfileuri = corprate_site + link[1]
            outputfilename = news_text_save_directory + link[1].split('/').replace('pdf','txt')
            save_pdftext(inputfileuri, outputfilename)

def get_red_news_relase():
    ''' 赤系のニュースリリースを取得します
    '''
    site_top_url = '{site_top_url}'
    news_site_url = '{backnumber_news_site_url}'
    news_text_save_directory = '{local_directory}'

    news_backNumbers = get_newslinks(news_site_url + '/back_no.htm','div','section01')
    newsfile_prefix = 1
    for back_number in news_backNumbers:
        if back_number[1] == site_top_url:
            continue
        year_news = get_newslinks(news_site_url + '/' + back_number[1],'div','section01 mt10 fsM')
        if len(year_news):
            # 途中からタグクラス名が変わる
            year_news = get_newslinks(news_site_url + '/' + back_number[1],'div','section01 mt15 fsM')
        for news in year_news:
            if len(news[1].split('/')) == 2:
                inputfileuri = news_site_url + '/' + back_number[1].split('/')[0] + '/' + news[1]
                outputfilename = (news_text_save_directory + '/' + str(newsfile_prefix) + news[1].split('/')[1]).replace('.pdf','.txt')
                if outputfilename != '':
                    save_pdftext(inputfileuri, outputfilename)
                    newsfile_prefix += 1

if __name__ == '__main__':
    main()
    