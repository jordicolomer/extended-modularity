import sys
import math

import time
updateprogressbar_start = None
def updateprogressbar(now,end):
	global updateprogressbar_start
	if updateprogressbar_start == None:
		updateprogressbar_start = time.time()
	p = 1.*now/end
	if p>0:
		print 'progress',100.*now/end,'percent',(time.time()-updateprogressbar_start)*(1-p)/p/60/60,'hours'

def tokenize(s):
	if tokenization=='spaces':
		return s.split()

idfmap = 0
def fastidf(w,documents):
	global idfmap
	if idfmap == 0:
		idfmap = {}
		for doc in documents:
			for w in set(tokenize(doc)):
				if w not in idfmap:
					idfmap[w] = 0
				idfmap[w] = idfmap[w]+1
	count = idfmap[w]
	if math.log(1.*len(documents)/count,2)<0:
		print len(documents),count
	return math.log(1.*len(documents)/count,2)

def getWeight(t,tf):
	if weighting == 'unity':
		return 1
	if weighting == 'len':
		return len(t)
	if weighting == 'tfidf':
		return tf*fastidf(t,documents)

import collections
def jaccard(s1,s2):
	inters = 0
	c1 = collections.Counter(tokenize(s1))
	c2 = collections.Counter(tokenize(s2))
	c1Andc2 = c1 & c2
	c1Plusc2 = c1 + c2
	for w in c1Andc2:
		inters = inters+getWeight(w,c1Plusc2[w])
	union = 0
	for w in c1Plusc2:
		union = union+getWeight(w,c1Plusc2[w])
	if union == 0:
		return 0
	return 1.*inters/union

def getvectors(s1,s2):
	w1 = collections.Counter(tokenize(s1))
	w2 = collections.Counter(tokenize(s2))
	x1=[]
	x2=[]
	for w in set(w1+w2):
		if w in w1:
			x1.append(getWeight(w,w1[w]))
		else:
			x1.append(0)
		if w in w2:
			x2.append(getWeight(w,w2[w]))
		else:
			x2.append(0)
	return x1,x2

def cosinecalc(x1,x2):
	num = 0
	den1 = 0
	den2 = 0
	for i in range(len(x1)):
		w1=x1[i]
		w2=x2[i]
		num = num+w1*w2
		den1 = den1+w1*w1
		den2 = den2+w2*w2
	den = (math.sqrt(den1)*math.sqrt(den2))
	if den==0:
		return 0
	return num/den

def cosine(s1,s2):
	x1,x2=getvectors(s1,s2)
	return cosinecalc(x1,x2)

def euclideancalc(x1,x2):
	suma=0
	den=0
	for i in range(len(x1)):
		suma+=math.pow(x1[i]-x2[i],2)
		den+=math.pow(max(x1[i],x2[i]),2)
	if den==0:
		return 0
	return 1-math.sqrt(suma)/math.sqrt(den)

def euclidean(s1,s2):
	x1,x2=getvectors(s1,s2)
	return euclideancalc(x1,x2)

import networkx
def getsimmatrix():
	if similarity=='jaccard':
		simf = jaccard
	if similarity=='cosine':
		simf = cosine
	if similarity=='euclidean':
		simf = euclidean
	G=networkx.Graph()
	G.add_nodes_from(range(0,len(documents)))
	for i in range(len(documents)):
		updateprogressbar(len(documents)*len(documents)-(len(documents)-i)*(len(documents)-i),len(documents)*len(documents))
		for j in range(len(documents)):
			if i<j:
				sim = simf(documents[i], documents[j])
				G.add_edge(i, j, weight=sim )
	return G

# variables globales
inputf=sys.argv[1]
similarity=sys.argv[2]
weighting=sys.argv[3]
tokenization=sys.argv[4]
alpha=float(sys.argv[5])
outputf=sys.argv[6]

# leer documentos
documents = []
f = open(inputf, "r")
l = f.readline()
while l:
	l = l.rstrip('\r\n')
	documents.append(l)
	l = f.readline()

# generate graph
G = getsimmatrix()

print 'calling community detection algorithm'
import community
community.alpha = alpha
clustering = community.best_partition(G)
f = open(outputf, 'w')
for i in range(len(documents)):
	f.write(str(clustering[i])+'\n')
f.close()
