#用来统计一个 出现原告和被告的句子中的动词
#按照罪名类型来统计动词

import json
import thulac


inpath = '/disk/mysql/law_data/critical_data/'

f = open('accusation_list.txt', 'r')
accusations_list = json.loads(f.readline())
cutter = thulac.thulac()


def analyseSentence(sentence):
    ans = []
    if ('原告' in sentence) or ('被害人' in sentence) or ('受害人' in sentence):
        if ('被告' in sentence):
            m = cutter.cut(sentence)
            for v in m:
                if v[1] == 'v':
                   ans.append(v[0])
    return ans



def analyse():
    verbInAccusation = {}
    for a in accusations_list:
        verbInAccusation[a] = {}
    for i in range(20):
        fin = open(inpath + str(i), 'r')
        line = fin.readline()
        num = 0
        while line:
            line = json.loads(line)
            if 'AJJBQK' in line['document']:
                caseContent = line['document']['AJJBQK'].replace("b", "").replace("\t", "")
                accusation = line['meta_info']['name_of_accusation']
                sentences = caseContent.split('。')
                for s in sentences:
                    verbs = analyseSentence(s)
                    for a in accusation:
                        if a in verbInAccusation:
                            for v in verbs:
                                if v in verbInAccusation[a]:
                                    verbInAccusation[a][v] += 1
                                else:
                                    verbInAccusation[a][v] = 1
            line = fin.readline()
            if num % 1000 == 0:
                print(v)
                print(num)
            num += 1
        break

    fout = open('result.txt', 'w')
    print(json.dumps(verbInAccusation), file = fout)


if __name__ == '__main__':
    analyse()
