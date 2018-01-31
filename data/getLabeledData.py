#coding:utf-8
import numpy as np
import json
import pickle
import configparser

config = configparser.ConfigParser()
config.read('config', encoding='utf-8')

def generateRandom():
    l = ['n', 'np', 'ns', 'ni', 'nz', 'm', 'q', 'mq', 't', 'f', 's', 'v', 'a', 'd', 'h', 'k', 'i', 'j', 'r', 'c', 'p',
         'u', 'y', 'e', 'o', 'g', 'w', 'x']
    d = {}
    for v in l:
        d[v] = np.random.rand(1, config.getint('feature', 'partOfSpeechSize'))
    fout = open(config.get('path', 'partOfSpeechPath'), 'wb')
    pickle.dump(d, fout, protocol=pickle.HIGHEST_PROTOCOL)
    fout.close()

#generateRandom()


class Word2vec():
    word_num = 0
    vec_len = 0
    word2id = None
    vec = None

    def __init__(self, word_dic = config.get('path', 'word_dic'), vec_path = config.get('path', 'wordVec_path')):
        print("begin to load word embedding")
        f = open(word_dic, "rb")
        (self.word_num, self.vec_len) = pickle.load(f)
        self.word2id = pickle.load(f)
        f.close()
        self.vec = np.load(vec_path)
        print("load word embedding succeed")

    def load(self, word):
        try:
            return self.vec[self.word2id[word]].astype(dtype=np.float32)
        except:
            return self.vec[self.word2id['UNK']].astype(dtype=np.float32)



class Transform():
    def __init__(self):
        self.getWordVec = Word2vec()
        self.n = config.getint('feature', 'n-gram')
        self.wordVecSize = config.getint('feature', 'wordVecSize')
        with open(config.get('path', 'partOfSpeechPath'), 'rb') as fin:
            self.partOfSpeech = pickle.load(fin)
        self.zero = np.zeros(self.wordVecSize + config.getint('feature', 'partOfSpeechSize'))
        #print(self.partOfSpeech)

    def wordVec(self, word):
        try:
            return np.concatenate([self.getWordVec.vec[self.getWordVec.word2id[word[0]]].astype(dtype=np.float32), self.partOfSpeech[word[1]]])
        except:
            return np.concatenate([self.getWordVec.vec[self.getWordVec.word2id['UNK']].astype(dtype=np.float32), np.zeros(config.getint('feature', 'partOfSpeechSize'))])

    def getFeature(self, sentence, k):
        '''type(sentence) == list   get the feature of kth word in the sentence'''
        listOfvec = [self.wordVec(sentence[k])]
        for i in range(1, self.n + 1):
            if k - i < 0:
                listOfvec.append(self.zero)
            else:
                listOfvec.append(self.wordVec(sentence[k - i]))

        ans = np.concatenate(listOfvec, axis = 0)
        return ans

if __name__ == '__main__':
    l = [['佛山市', 'ns', 0], ['顺德区', 'ns', 0], ['人民', 'n', 0], ['检察院', 'n', 0], ['指控', 'v', 0], ['称', 'v', 0], ['，', 'w', 0], ['2014年', 't', 0], ['12月', 't', 0], ['28日', 't', 0], ['23时', 't', 0], ['许', 'm', 0], ['，', 'w', 0], ['在', 'p', 0], ['佛山市', 'ns', 6], ['顺德区', 'ns', 6]]
    transformer = Transform()
    print(transformer.getFeature(l, 0))
