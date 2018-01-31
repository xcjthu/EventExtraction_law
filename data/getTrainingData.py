from getLabeledData import Transform
import argparse, json
import numpy as np
import pickle

def main(args):
    X = []
    Y = []
    lines = open(args.path, 'r').readlines()
    transformer = Transform()
    for line in lines:
        sts = json.loads(line)
        for i in range(len(sts)):
            X.append(transformer.getFeature(sts, i))
            Y.append(sts[i][2])
    opt = {
        'X': np.array(X),
        'Y': np.array(Y)
    }
    pickle.dump(opt, open(args.out, 'wb'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="path of labeled data (.json)")
    parser.add_argument("out", help="output file name (.pkl)")
    args = parser.parse_args()
    main(args)
