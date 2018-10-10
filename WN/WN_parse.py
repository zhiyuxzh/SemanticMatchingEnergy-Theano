import os
import pickle

import numpy as np
import scipy.sparse as sp

# Put the wordnet-mlj data absolute path here
datapath = '/Users/a/Downloads/SME-master2/data/increment/test/original/'

if 'data' not in os.listdir('/Users/a/Downloads/SME-master2/'):
    os.mkdir('/Users/a/Downloads/SME-master2/data')


def parseline(line):
    lhs, rel, rhs = line.split('\t')
    lhs = lhs.split(' ')
    rhs = rhs.split(' ')
    rel = rel.split(' ')
    return lhs, rel, rhs

#################################################
### Creation of the synset/indices dictionnaries

np.random.seed(753)

synlist = []
rellist = []

for datatyp in ['train', 'valid', 'test']:
    f = open(datapath + 'wordnet-mlj12-%s.txt' % datatyp, 'r')
    dat = f.readlines()
    f.close()
    for i in dat:
        lhs, rel, rhs = parseline(i[:-1])
        synlist += [lhs[0], rhs[0]]
        rellist += [rel[0]]

synset = np.sort(list(set(synlist)))
relset = np.sort(list(set(rellist)))

synset2idx = {}
idx2synset = {}

idx = 0
for i in synset:
    synset2idx[i] = idx
    idx2synset[idx] = i
    idx += 1
nbsyn = idx
print ("Number of synsets in the dictionary: ", nbsyn)
# add relations at the end of the dictionary
for i in relset:
    synset2idx[i] = idx
    idx2synset[idx] = i
    idx += 1
nbrel = idx - nbsyn
print ("Number of relations in the dictionary: ", nbrel)
print relset

f = open(datapath + 'WN_synset2idx.pkl', 'w')
g = open(datapath + 'WN_idx2synset.pkl', 'w')
pickle.dump(synset2idx, f, -1)
pickle.dump(idx2synset, g, -1)
f.close()
g.close()

for datatyp in ['train', 'valid', 'test']:
    f = open(datapath + 'wordnet-mlj12-%s.txt' % datatyp, 'r')
    dat = f.readlines()
    f.close()

    # Declare the dataset variables
    inpl = sp.lil_matrix((np.max(synset2idx.values()) + 1, len(dat)),
            dtype='float32')
    inpr = sp.lil_matrix((np.max(synset2idx.values()) + 1, len(dat)),
            dtype='float32')
    inpo = sp.lil_matrix((np.max(synset2idx.values()) + 1, len(dat)),
            dtype='float32')
    # Fill the sparse matrices
    ct = 0
    for i in dat:
        lhs, rel, rhs = parseline(i[:-1])
        inpl[synset2idx[lhs[0]], ct] = 1
        inpr[synset2idx[rhs[0]], ct] = 1
        inpo[synset2idx[rel[0]], ct] = 1
        ct += 1
    # Save the datasets
    if 'data' not in os.listdir('/Users/a/Downloads/SME-master2/'):
        os.mkdir('/Users/a/Downloads/SME-master2/data')
    f = open(datapath + 'WN-%s-lhs.pkl' % datatyp, 'w')
    g = open(datapath + 'WN-%s-rhs.pkl' % datatyp, 'w')
    h = open(datapath + 'WN-%s-rel.pkl' % datatyp, 'w')
    pickle.dump(inpl.tocsr(), f, -1)
    pickle.dump(inpr.tocsr(), g, -1)
    pickle.dump(inpo.tocsr(), h, -1)
    f.close()
    g.close()
    h.close()