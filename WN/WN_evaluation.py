#! /usr/bin/python
import sys
# import cPickle
import pickle
import json
from model import *


def load_file(path):
    return scipy.sparse.csr_matrix(pickle.load(open(path, "rb")),
            dtype=theano.config.floatX)


def convert2idx(spmat):
    rows, cols = spmat.nonzero()
    return rows[np.argsort(cols)]


def RankingEval(datapath='/Users/a/Downloads/SME-master2/data/increment/test', dataset='WN-test', decre=False,
        loadmodel='best_valid_model.pkl', neval='all', Nsyn=1984, n=10,
        idx2synsetfile='WN_idx2synset.pkl'):

    # Load model
    f = open(loadmodel, "rb")
    embeddings = pickle.load(f)
    leftop = pickle.load(f)
    rightop = pickle.load(f)
    simfn = pickle.load(f)
    f.close()

    # Load data
    l = load_file(datapath + dataset + '-lhs.pkl')
    r = load_file(datapath + dataset + '-rhs.pkl')
    o = load_file(datapath + dataset + '-rel.pkl')
    if type(embeddings) is list:
        o = o[-embeddings[1].N:, :]

    # Convert sparse matrix to indexes
    if neval == 'all':
        idxl = convert2idx(l)
        idxr = convert2idx(r)
        idxo = convert2idx(o)
    else:
        idxl = convert2idx(l)[:neval]
        idxr = convert2idx(r)[:neval]
        idxo = convert2idx(o)[:neval]

    ranklfunc = RankLeftFnIdx(simfn, embeddings, leftop, rightop,
            subtensorspec=Nsyn)
    rankrfunc = RankRightFnIdx(simfn, embeddings, leftop, rightop,
            subtensorspec=Nsyn)

    res = RankingScoreIdx(ranklfunc, rankrfunc, idxl, idxr, idxo)
    dres = {}
    dres.update({'microlmean': np.mean(res[0])})
    dres.update({'microlmedian': np.median(res[0])})
    dres.update({'microlhits@n': np.mean(np.asarray(res[0]) <= n) * 100})
    dres.update({'micrormean': np.mean(res[1])})
    dres.update({'micrormedian': np.median(res[1])})
    dres.update({'microrhits@n': np.mean(np.asarray(res[1]) <= n) * 100})
    resg = res[0] + res[1]
    dres.update({'microgmean': np.mean(resg)})
    dres.update({'microgmedian': np.median(resg)})
    dres.update({'microghits@n': np.mean(np.asarray(resg) <= n) * 100})

    print ("### MICRO:")
    print ("\t-- left   >> mean: %s, median: %s, hits@%s: %s%%" % (
            round(dres['microlmean'], 5), round(dres['microlmedian'], 5),
            n, round(dres['microlhits@n'], 3)))
    print ("\t-- right  >> mean: %s, median: %s, hits@%s: %s%%" % (
            round(dres['micrormean'], 5), round(dres['micrormedian'], 5),
            n, round(dres['microrhits@n'], 3)))
    print ("\t-- global >> mean: %s, median: %s, hits@%s: %s%%" % (
            round(dres['microgmean'], 5), round(dres['microgmedian'], 5),
            n, round(dres['microghits@n'], 3)))

    listrel = set(idxo)
    dictrelres = {}
    dictrellmean = {}
    dictrelrmean = {}
    dictrelgmean = {}
    dictrellmedian = {}
    dictrelrmedian = {}
    dictrelgmedian = {}
    dictrellrn = {}
    dictrelrrn = {}
    dictrelgrn = {}

    for i in listrel:
        dictrelres.update({i: [[], []]})

    for i, j in enumerate(res[0]):
        dictrelres[idxo[i]][0] += [j]

    for i, j in enumerate(res[1]):
        dictrelres[idxo[i]][1] += [j]

    for i in listrel:
        dictrellmean[i] = np.mean(dictrelres[i][0])
        dictrelrmean[i] = np.mean(dictrelres[i][1])
        dictrelgmean[i] = np.mean(dictrelres[i][0] + dictrelres[i][1])
        dictrellmedian[i] = np.median(dictrelres[i][0])
        dictrelrmedian[i] = np.median(dictrelres[i][1])
        dictrelgmedian[i] = np.median(dictrelres[i][0] + dictrelres[i][1])
        dictrellrn[i] = np.mean(np.asarray(dictrelres[i][0]) <= n) * 100
        dictrelrrn[i] = np.mean(np.asarray(dictrelres[i][1]) <= n) * 100
        dictrelgrn[i] = np.mean(np.asarray(dictrelres[i][0] +
                                           dictrelres[i][1]) <= n) * 100

    dres.update({'dictrelres': dictrelres})
    dres.update({'dictrellmean': dictrellmean})
    dres.update({'dictrelrmean': dictrelrmean})
    dres.update({'dictrelgmean': dictrelgmean})
    dres.update({'dictrellmedian': dictrellmedian})
    dres.update({'dictrelrmedian': dictrelrmedian})
    dres.update({'dictrelgmedian': dictrelgmedian})
    dres.update({'dictrellrn': dictrellrn})
    dres.update({'dictrelrrn': dictrelrrn})
    dres.update({'dictrelgrn': dictrelgrn})

    dres.update({'macrolmean': np.mean(list(dictrellmean.values()))})
    dres.update({'macrolmedian': np.mean(list(dictrellmedian.values()))})
    dres.update({'macrolhits@n': np.mean(list(dictrellrn.values()))})
    dres.update({'macrormean': np.mean(list(dictrelrmean.values()))})
    dres.update({'macrormedian': np.mean(list(dictrelrmedian.values()))})
    dres.update({'macrorhits@n': np.mean(list(dictrelrrn.values()))})
    dres.update({'macrogmean': np.mean(list(dictrelgmean.values()))})
    dres.update({'macrogmedian': np.mean(list(dictrelgmedian.values()))})
    dres.update({'macroghits@n': np.mean(list(dictrelgrn.values()))})

    print ("### MACRO:")
    print ("\t-- left   >> mean: %s, median: %s, hits@%s: %s%%" % (
            round(dres['macrolmean'], 5), round(dres['macrolmedian'], 5),
            n, round(dres['macrolhits@n'], 3)))
    print ("\t-- right  >> mean: %s, median: %s, hits@%s: %s%%" % (
            round(dres['macrormean'], 5), round(dres['macrormedian'], 5),
            n, round(dres['macrorhits@n'], 3)))
    print ("\t-- global >> mean: %s, median: %s, hits@%s: %s%%" % (
            round(dres['macrogmean'], 5), round(dres['macrogmedian'], 5),
            n, round(dres['macroghits@n'], 3)))
    if not decre:
        idx2synset = pickle.load(open(datapath + idx2synsetfile, 'rb'))
    else:
        idx2synset = pickle.load(open(decre + idx2synsetfile, 'rb'))

    offset = 0
    if type(embeddings) is list:
        o = o[-embeddings[1].N:, :]
        offset = l.shape[0] - embeddings[1].N
    for i in np.sort(list(listrel)):
        print ("### RELATION %s:" % idx2synset[offset + i])
        print ("\t-- left   >> mean: %s, median: %s, hits@%s: %s%%, N: %s" % (
                round(dictrellmean[i], 5), round(dictrellmedian[i], 5),
                n, round(dictrellrn[i], 3), len(dictrelres[i][0])))
        print ("\t-- right  >> mean: %s, median: %s, hits@%s: %s%%, N: %s" % (
                round(dictrelrmean[i], 5), round(dictrelrmedian[i], 5),
                n, round(dictrelrrn[i], 3), len(dictrelres[i][1])))
        print ("\t-- global >> mean: %s, median: %s, hits@%s: %s%%, N: %s" % (
                round(dictrelgmean[i], 5), round(dictrelgmedian[i], 5),
                n, round(dictrelgrn[i], 3),
                len(dictrelres[i][0] + dictrelres[i][1])))
    #print(res)
    g1 = open(datapath+'rank-left.pkl', 'wb')
    g2 = open(datapath+'rank-right.pkl', 'wb')
    pickle.dump(res[0], g1)
    pickle.dump(res[1], g2)
    g1.close()
    g2.close()
    f = open(datapath + 'top10-left.json', 'w')
    g = open(datapath + 'top10-right.json', 'w')
    json.dump(res[2], f)
    json.dump(res[3], g)
    f.close()
    g.close()
    return dres


def ClassifEval(datapath='/Users/a/Downloads/SME-master2/data/', validset='WN-valid', testset='WN-test',
        loadmodel='best_valid_model.pkl', seed=647):

    # Load model
    f = open(loadmodel, "rb")
    embeddings = pickle.load(f)
    leftop = pickle.load(f)
    rightop = pickle.load(f)
    simfn = pickle.load(f)
    f.close()

    np.random.seed(seed)

    # Load data
    lv = load_file(datapath + validset + '-lhs.pkl')
    lvn = lv[:, np.random.permutation(lv.shape[1])]
    rv = load_file(datapath + validset + '-rhs.pkl')
    rvn = rv[:, np.random.permutation(lv.shape[1])]
    ov = load_file(datapath + validset + '-rel.pkl')
    ovn = ov[:, np.random.permutation(lv.shape[1])]
    if type(embeddings) is list:
        ov = ov[-embeddings[1].N:, :]
        ovn = ovn[-embeddings[1].N:, :]

    # Load data
    lt = load_file(datapath + testset + '-lhs.pkl')
    ltn = lt[:, np.random.permutation(lt.shape[1])]
    rt = load_file(datapath + testset + '-rhs.pkl')
    rtn = rt[:, np.random.permutation(lt.shape[1])]
    ot = load_file(datapath + testset + '-rel.pkl')
    otn = ot[:, np.random.permutation(lt.shape[1])]
    if type(embeddings) is list:
        ot = ot[-embeddings[1].N:, :]
        otn = otn[-embeddings[1].N:, :]

    simfunc = SimFn(simfn, embeddings, leftop, rightop)

    resv = simfunc(lv, rv, ov)[0]
    resvn = simfunc(lvn, rvn, ovn)[0]
    rest = simfunc(lt, rt, ot)[0]
    restn = simfunc(ltn, rtn, otn)[0]

    # Threshold
    perf = 0
    T = 0
    for val in list(np.concatenate([resv, resvn])):
        tmpperf = (resv > val).sum() + (resvn <= val).sum()
        if tmpperf > perf:
            perf = tmpperf
            T = val
    testperf = ((rest > T).sum() + (restn <= T).sum()) / float(2 * len(rest))
    print ("### Classification performance : %s%%" % round(testperf * 100, 3))

    return testperf


if __name__ == '__main__':
    #ClassifEval()
    #RankingEval(loadmodel=sys.argv[1])
    #ClassifEval(datapath='/Users/a/Downloads/SME-master2/data/', loadmodel='/Users/a/Downloads/SME-master2/data/WN_SME_lin/best_valid_model.pkl')
    #RankingEval(datapath='/Users/a/Downloads/SME-master2/data/', loadmodel='/Users/a/Downloads/SME-master2/data/WN_SME_lin/best_valid_model.pkl')
    # ClassifEval(datapath='/Users/a/Downloads/SME-master2/data/increment/1w/changed/',
    #             loadmodel='/Users/a/Downloads/SME-master2/data/increment/1w/retrain/best_valid_model.pkl')
    RankingEval(datapath='/Users/a/Downloads/SME-master2/data/increment/test/original/',
                # decre='/Users/a/Downloads/SME-master2/data/increment/test/changed/',
                loadmodel='/Users/a/Downloads/SME-master2/data/increment/test/changed/SME-bil/best_valid_model.pkl', Nsyn=1635)
