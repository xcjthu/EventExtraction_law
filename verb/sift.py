import json
import math


def sortDic(d):
    ans = []
    for key in d.keys():
        ans.append((d[key], key))
    ans.sort()
    ans.reverse()
    return ans


def getImportantVerb():
    inpath = 'count.txt'
    fin = open(inpath, 'r')
    count = json.loads(fin.read())
    sumEventType = len(count)
    mincount = 4
    all = {}
    dictionary = {}
    for key in count.keys():
        all[key] = 0
        for verb in count[key]:
            if count[key][verb] <= mincount:
                continue
            all[key] += count[key][verb]
            if verb in dictionary:
                dictionary[verb] += 1
            else:
                dictionary[verb] = 1

    TR = {}
    for key in count.keys():
        TR[key] = {}
        for verb in count[key].keys():
            if count[key][verb] <= mincount:
                continue
            TCF = count[key][verb]/all[key]
            TETF = math.log(sumEventType/(1 + dictionary[verb]))
            TR[key][verb] = TCF * TETF

    fout = open('a.json', 'w')
    #ans = {}
    for key in TR.keys():
        print(json.dumps({key: sortDic(TR[key])}, ensure_ascii = False), file = fout)


getImportantVerb()