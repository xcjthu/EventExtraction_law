from itertools import chain
import nltk
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelBinarizer
import sklearn
import json
import pycrfsuite


def word2features(sent, i):
    feature = {
        'word': sent[i][0],
        'tag': sent[i][1]
    }
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

    #tagset = set(lb.classes_) - {'O'}
    #tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}

    return classification_report(
        y_true_combined,
        y_pred_combined
    )

fin = open('../data/goodData.json', 'r')
allData = []
line = fin.readline()
while line:
    sen = json.loads(line)
    allData.append(sen)
    line = fin.readline()

train = allData[:100]
test = allData[100:]

X_train = [sent2features(s) for s in train]
y_train = [sent2labels(s) for s in train]

X_test = [sent2features(s) for s in test]
y_test = [sent2labels(s) for s in test]

#print(sent2features(train[0]))

trainer = pycrfsuite.Trainer(verbose=False)

for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)

trainer.set_params({
    'c1': 1.0,   # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 50,  # stop earlier

    # include transitions that are possible, but not observed
    'feature.possible_transitions': True
})

trainer.train('crf.crfsuite')


tagger = pycrfsuite.Tagger()
tagger.open('crf.crfsuite')

lb = LabelBinarizer()

#print(sent2features(train[0]))
#y_pred = [tagger.tag(sent2features(xseq)) for xseq in zip(train)]
y_pred = [tagger.tag(xseq) for xseq in X_test]
print(bio_classification_report(y_test, y_pred))

