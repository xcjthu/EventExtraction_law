from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import json
import pycrfsuite

classes = {}
def init():
    global classes
    f = open('../data/classes.txt', 'r')
    line = f.readline()
    while line:
        tmp = line.split()
        classes[tmp[0]] = int(tmp[1])
        line = f.readline()
    f.close()

init()

def word2features(sent, i):
    global classes

    feature = {
        'word': sent[i][0],
        'tag': sent[i][1]
    }
    try:
        feature['classes'] = classes[sent[i][0]]
    except Exception as err:
        feature['classes'] = -1
    if i != 0:
        #feature['wordB'] = sent[i - 1][0]
        feature['wordBTag'] = sent[i - 1][1]
        try:
            feature['wordBClass'] = classes[sent[i - 1][0]]
        except Exception as err:
            feature['wordBClass'] = -1
    else:
        #feature['wordB'] = ' '
        feature['wordBTag'] = 'NULL'
        feature['wordBClass'] = -1

    if i >= (len(sen) - 1):
        #feature['wordN'] = ' '
        feature['wordNTag'] = 'NULL'
        feature['wordNClass'] = -1
    else:
        try:
            #feature['wordN'] = sent[i + 1][0]
            feature['wordNTag'] = sent[i + 1][1]
            try:
                feature['wordNClass'] = classes[sent[i + 1][0]]
            except Exception as err:
                feature['wordNClass'] = -1
        except Exception as err:
            pass
            #print(i, len(sent))
            # print(err)
    return feature


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def sent2labels(sent):
    d = {
        0: 'None',
        1: 'THING',
        2: 'VALUE',
        3: 'WEAPON',
        4: 'METHOD',
        5: 'RESULT',
        6: 'PLACE',
        7: 'SUFFERER',
        8: 'TRIGGER'
    }
    return [d[v[2]] for v in sent]
    #return [str(v[2]) for v in sent]
    #return [v[2] for v in sent]

def bio_classification_report(y_true, y_pred):
    """
    Classification report for a list of BIO-encoded sequences.
    It computes token-level metrics and discards "O" labels.

    Note that it requires scikit-learn 0.15+ (or a version from github master)
    to calculate averages properly!
    """
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
    y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))

    tagset = set(lb.classes_)
    #tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}

    return classification_report(
        y_true_combined,
        y_pred_combined
    )

def check(d):
    keys = d.keys()
    if ('SUFFERER' in keys) and ('TRIGGER' in keys) and ('PLACE' in keys) and ('THING' in keys):
        #拥有key arguments
        if len(d['TRIGGER']) == 1:
            #只有一个Trigger
            if len(d['PLACE']) == 1:
                #只有一个地点
                return True
    return False


def standardlize(sentence, checkForCorrect = check):
    #print(sentence)
    temp = []
    s = ''
    t = ''
    last = 'None'
    for word in sentence:
        s += word[0]
        if word[2] == 'None' and last == 'None':
            #temp.append([t, last])
            #last = 'None'
            #t = ''
            continue

        if word[2] == last:
            t += word[0]
        else:
            temp.append([t, last])
            t = word[0]
            last = word[2]

    ans = {}
    for word in temp:
        if word[1] not in ans:
            ans[word[1]] = [word[0]]
        else:
            ans[word[1]].append(word[0])
    try:
        ans.pop('None')
    except:
        pass
    ans['content'] = s

    if checkForCorrect(ans):
        return ans
    else:
        return None




def predict(tag):
    fout = open('../data/predict_formed_data.json', 'w')
    fout1 = open('../data/predict_data.json', 'w')
    fin = open('../data/allRobData.json', 'r')
    doc = fin.readline()
    #ans = []
    while doc:
        try:
            doc = json.loads(doc)
            docans = []
            for s in doc:
                feature = sent2features(s)
                T = tag.tag(feature)
                m = []
                for i, t in enumerate(T):
                    m.append([s[i][0], s[i][1], t])
                tmp = standardlize(m)
                if not tmp is None:
                    print(json.dumps(m, ensure_ascii = False), file = fout1)
                    #docans.append(tmp)
                    print(json.dumps(tmp, ensure_ascii = False), file = fout)
            doc = fin.readline()
            #ans.append(docans)
            #if not docans == []:
            #    print(json.dumps(docans, ensure_ascii = False), file = fout)
        except Exception as err:
            print(err)
            print(doc)
            doc = fin.readline()



fin = open('../data/goodData.json', 'r')
allData = []
line = fin.readline()
while line:
    sen = json.loads(line)
    allData.append(sen)
    line = fin.readline()

#train = allData[31:]
train = allData
print('dataSize:', len(allData))


X_train = [sent2features(s) for s in train]
y_train = [sent2labels(s) for s in train]

trainer = pycrfsuite.Trainer(verbose=False)

for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)

trainer.set_params({
    'c1': 1.0,   # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 100,  # stop earlier
    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})

trainer.train('crf.crfsuite')


tagger = pycrfsuite.Tagger()
tagger.open('crf.crfsuite')

test = allData[:31]
X_test = [sent2features(s) for s in test]
y_test = [sent2labels(s) for s in test]

#print(tagger.tag())

#print(sent2features(train[0]))
#y_pred = [tagger.tag(sent2features(xseq)) for xseq in zip(train)]
y_pred = [tagger.tag(xseq) for xseq in X_train]
#print(y_pred[0])
print(bio_classification_report(y_train, y_pred))
#print(classification_report(y_train, y_pred))
y_pred_test = [tagger.tag(xseq) for xseq in X_test]
print(bio_classification_report(y_test, y_pred_test))


predict(tagger)
# the predicted data has a high precision but has a low recall


'''
0 None
1 被抢物品
2 金额
3 凶器
4 手段
5 被害人结果
6 地点
7 被抢对象
8 trigger word
'''

# model = gensim.models.KeyedVectors.load_word2vec_format('vectors.bin', binary = True)