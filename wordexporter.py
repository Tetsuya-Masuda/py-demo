import MeCab
import sys
import os


def get_files(directorypath):
    ''' 指定したディレクトリ配下のファイルを取得します
    '''
    files = []
    for file in os.listdir(directorypath):
        filefullpath = directorypath + '/' + file
        if os.path.isfile(filefullpath):
            files.append(filefullpath)
    return files

def get_linewords(filepath):
    ''' ファイル内に含まれる文章の単語を取得します
    '''
    txtfile = open(filepath, 'r')
    words = []
    for line in txtfile:
        if line.find('。') == -1:
            words.append(get_words(line))
        else:
            segments = sentence.split('。')
            for segment in segments:
                words.append(get_words(segment))
    txtfile.close()
    return words

def get_words(sentence):
    ''' 文章を単語に分解し、不要な単語を除外し、必要な単語群を返却します
    '''
    mecab = MeCab.Tagger('-Ochasen -d /usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd')
    features = []
    mecab.parse('')
    node = mecab.parseToNode(sentence)
    while node:
        surface = node.surface
        meta = node.feature.split(',')
        if IsSafeNoun(meta[0]) and IsSafeMark(meta[6]):
            features.append(meta[6].strip())
        node = node.next
    return features

def write_txtfile(filename,words):
    ''' 単語群を学習用のテキストファイルに書き込みます
    '''
    wakatid_file = open(filename, 'a', encoding = 'utf-8')
    for line_words in words:
        for word in line_words:
            wakatid_file.write(word + ' ')
        wakatid_file.write('\n')
    wakatid_file.close()

def IsSafeNoun(candidate):
    return candidate != '助動詞' and candidate != '記号' and candidate != '副詞'
def IsSafeMark(candidate):
    return candidate != '*' and candidate != '>' and candidate != '＞' and candidate != '<' and candidate != '＜' and 0 <= len(candidate.strip())

def main():
    ''' 緑、青、赤分を実施してください
    '''
    pdf_file_directory = '{crawler.pyで指定したpdf保存先ディレクトリ}'
    wakatied_file_name = '{分かち書きしたテキストファイル}'

    files = get_files(pdf_file_directory)
    for filePath in files:
        words = get_linewords(filePath)
        write_txtfile(wakatied_file_name,words)




if __name__ == '__main__':
    main()