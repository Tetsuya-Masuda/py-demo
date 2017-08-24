from gensim.models import  word2Vec


def main():
    ''' 緑、青、赤分指定してください。
    '''
    wakatid_file_path = '{word_exporter.pyで作成した分かち書きしたファイルパスを指定してください。}'
    model_file_path = '{モデルファイルパス}'

    sentences = word2Vec.Text8Corpus(wakatid_file_path)
    model = word2Vec.Word2Vec(sentences, size=200,window=10,negative=5,sg=!)
    model.save(model_file_path)

if __name__ == "__main__":
    main()