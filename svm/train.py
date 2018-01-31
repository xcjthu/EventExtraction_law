import pickle
from sklearn import svm
from sklearn.externals import joblib


pkl = pickle.load(open('../data/trainingData.pkl', 'rb'))

clf = svm.SVC(C=1.0, verbose=True)

clf.fit(pkl['X'], pkl['Y'])

print("Mean accuracy", clf.score(pkl['X'], pkl['Y']))

joblib.dump(clf, "model.svm.m")

