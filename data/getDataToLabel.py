import json
import os
import thulac

inpath = '/home/xcj/law_pre/predict_data1/'
outpath = 'dataToLabel.json'

getNum = 400
cut = thulac.thulac()


def get(num):
    global cut
    fileList = os.listdir(inpath)
    fout = open(outpath, 'a')
    n = 0
    for f in fileList:
        fin = open(inpath + f, 'r')
        line = fin.readline()
        while line:
            line = json.loads(line)
            ans = []
            if line['meta']['crit'] != 16 and line['meta']['crit'] != 19:
                continue
            for s in line['content']:
                sentence = ''.join(s)
                sentence = thulac.cut(sentence)
                ans.append(sentence)
            print(json.dumps(ans, ensure_ascii = False), file = fout)
            n += 1
            if n == num:
                return

            line = fin.readline()
        fin.close()

get(400)
