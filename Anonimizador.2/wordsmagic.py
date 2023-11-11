#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 19:18:18 2023

@author: pablo
"""

class wordsMagic:
	def __init__(self, listOfWords, normalizedMagicText):
		self.normalizedMagicText = normalizedMagicText
		
		self.listOfWords = []
		for word in listOfWords:
			splitChars = [x for x in word if not x.isalpha()]
			for s in splitChars:
				word = max(word.split(s), key=lambda x: len(x)).strip()
			
			self.listOfWords.append(word)
			
		self.listOfWords = set([self.normalizedMagicText(x) for x in self.listOfWords if len(x)>0])
		self.initialize()
		
	def initialize(self):
		self.data = dict()
		self.shorts = dict()
		for W in self.listOfWords:
			
			if len(W)<4:
				if W[0] not in self.shorts.keys():
					self.shorts[W[0]] = []
				self.shorts[W[0]].append(W)
			
			else:
				prefix = W[:3]
				letter = W[3]
				#print(self.data)
				
				if prefix not in self.data:
					self.data[prefix] = dict()
					
				if letter not in self.data[prefix]:
					self.data[prefix][letter] = [ W[3:] ]
				else:
					self.data[prefix][letter].append( W[3:] )
		
		# define valid err prefixes
		self.variablePrefix = dict()
		for prefix in self.data.keys():
			a,b,c = prefix[0],prefix[1],prefix[2]
			varA = '?%s%s'%(b,c)
			varB = '%s?%s'%(a,c)
			varC = '%s%s?'%(a,b)
			
			if varA not in self.variablePrefix:
				self.variablePrefix[varA] = [prefix]
			else:
				self.variablePrefix[varA].append(prefix)
			if varB not in self.variablePrefix:
				self.variablePrefix[varB] = [prefix]
			else:
				self.variablePrefix[varB].append(prefix)
			if varC not in self.variablePrefix:
				self.variablePrefix[varC] = [prefix]
			else:
				self.variablePrefix[varC].append(prefix)
	
	def removeWords(self, words):
		for w in words:
			W = self.normalizedMagicText(w) 
			if W in self.listOfWords:
				self.listOfWords.remove(W)
		self.initialize()
	
	def addWords(self, words):
		for w in words:
			W = self.normalizedMagicText(w)
			if W not in self.listOfWords:
				self.listOfWords.add(W)
		self.initialize()
			
	
	def getSufixes(self, prefix):
		sufixes = []
		withPrefix = self.data.get(prefix)
		if withPrefix:
			for letter in withPrefix.keys():
				sufixes += withPrefix.get(letter)

		return sufixes
	
	def findSufixes(self, prefix, letter):
		withPrefix = self.data.get(prefix)
		if withPrefix:
			out = withPrefix.get(letter)
			if not out: out = []
		else:
			out = []
		return out
	
	def findWords(self, prefix):
		sufixes = self.getSufixes(prefix)
		return [prefix + x for x in sufixes]

	def prefixSearch(self, search):
		prefixes = self.variablePrefix.get(search)
		if prefixes:
			return prefixes
		else:
			return []
	
	def match(self, input_text):
		text = self.normalizedMagicText(input_text)
		
		if len(text) != len(input_text):
			raise Exception('''Normalization string function doesnt presever len of\n\n%s\n\nAborting!'''%input_text)
			
		if len(text)<4:
			return None, None
		
		matchesErr = []
		matches = []
		for cur in range(1, len(text)-3):
			if not text[cur].isalpha(): #TODO: agregar cualquier caracter que no esté en PREFIXES
				continue
			
			curMatch = cur-1
			a,b,c = text[curMatch:cur+2]
			# ERROR IN PREFIX
			# S=suffix
			
			# 1 extra char 12X3S: ignore 3rd
			prefix = a+b+text[curMatch+3]
			sufixes = self.findSufixes(prefix, text[curMatch+4])
			matchesErr+= [(prefix+s, (curMatch, curMatch+4+len(s))) for s in sufixes if s==text[curMatch+4:curMatch+4+len(s)]]
			#print(matchesErr)
			
			# 1 extra char, 1X23S: ignore 2nd
			prefix = a+c+text[curMatch+3]
			sufixes = self.findSufixes(prefix, text[curMatch+4])
			matchesErr+= [(prefix+s, (curMatch, curMatch+4+len(s))) for s in sufixes if s==text[curMatch+4:curMatch+4+len(s)]]
			#print(matchesErr)
		
			# permutation 132S
			prefix = a+c+b
			sufixes = self.findSufixes(prefix, text[curMatch+3])
			matchesErr+= [(prefix+s, (curMatch, curMatch+3+len(s))) for s in sufixes if s==text[curMatch+3:curMatch+3+len(s)]]
			#print(matchesErr)
			
			# permutation 213S
			prefix = b+a+c
			sufixes = self.findSufixes(prefix, text[curMatch+3])
			matchesErr+= [(prefix+s, (curMatch, curMatch+3+len(s))) for s in sufixes if s==text[curMatch+3:curMatch+3+len(s)]]
			#print(matchesErr)

			# missed letter 12_S, 1_3S
			abx = '%s%s?'%(a,b)
			axc = '%s?%s'%(a,b)
			xbc = '?%s%s'%(a,b)
			prefixes = self.prefixSearch(abx) + self.prefixSearch(axc) + self.prefixSearch(xbc)
			for prefix in prefixes:
				sufixes = self.findSufixes(prefix, c)
				matchesErr+= [(prefix+s, (curMatch, curMatch+2+len(s))) for s in sufixes if s==text[curMatch+2:curMatch+2+len(s)]]
			#print(matchesErr)

			# wrong letter 12XS, 1X3S, X23S
			abx = '%s%s?'%(a,b)
			axc = '%s?%s'%(a,c)
			#xbc = '?%s%s'%(b,c)
			prefixes = self.prefixSearch(abx) + self.prefixSearch(axc) #+ self.prefixSearch(xbc)
			for prefix in prefixes:
				if prefix == a+b+c:
					continue
				sufixes = self.findSufixes(prefix, text[curMatch+3])
				matchesErr+= [(prefix+s, (curMatch, curMatch+3+len(s))) for s in sufixes if s==text[curMatch+3:curMatch+3+len(s)]]	 
			#print(matchesErr)
			#continue
			
			# NO ERROR IN PREFIX
			# 123S
			prefix = a+b+c
			sufixes = self.getSufixes(prefix)
			for s in sufixes:
				w = text[curMatch+3:curMatch+4+len(s)]
				d = min(len(s)-1, len(w)-1)
				
				p = 0
				while p<d and s[p]==w[p]:
					p+=1
				#print(f's={s}\nw={w}\np={p}\nd={d}')
				if p==len(s)-1 and w[p]==s[p]:
					#print(f's={s}\nw={w}\np={p}\nd={d}\ncur={cur}')
					matches.append((prefix+s, (curMatch, curMatch+3+len(s))))
			
				elif p==len(s)-1:
					matchesErr.append((prefix+s, (curMatch, curMatch+3+len(s)-1)))
					
				else:
					if (w[p+1:]==s[p:]): #extraChar
						matchesErr.append((prefix+s, (curMatch, curMatch+3+len(s)+1)))
					if len(w)-1==len(s) and s[p:]==w[p+1]+w[p]+w[p+2:]: #permutation
						matchesErr.append((prefix+s, (curMatch, curMatch+3+len(s))))
					if (w[p:len(s)-1]==s[p+1:]): #missedChar
						matchesErr.append((prefix+s, (curMatch, curMatch+3+len(s)-1)))
					if (w[p+1:-1]==s[p+1:]): #wrongLetter
						matchesErr.append((prefix+s, (curMatch, curMatch+3+len(s))))
					#if any([extraChar, permutati, missed, wronglett]):
					#	matchesErr.append((prefix+s, curMatch))
		
		matchCount = dict()
		for word,idx in matches:
			if word not in matchCount.keys():
				matchCount[word] = []
			matchCount[word].append(idx)
			
		matchErrCount = dict()
		for word,idx in matchesErr:
			if word not in matchErrCount.keys():
				matchErrCount[word] = []
			matchErrCount[word].append(idx)
		
		return matchCount, matchErrCount



class exactMatcher:
	def __init__(self, listOfWords, normalizedMagicText):
		self.normalizedMagicText = normalizedMagicText
		self.listOfWords = set([self.normalizedMagicText(x) for x in listOfWords if len(x)>0])
		self.initialize()
		
	def initialize(self):
		self.data = dict()
		self.shorts = dict()
		for W in self.listOfWords:
			
			if len(W)<4:
				if W[0] not in self.shorts.keys():
					self.shorts[W[0]] = []
				self.shorts[W[0]].append(W)
			
			else:
				prefix = W[:3]
				letter = W[3]
				
				if prefix not in self.data:
					self.data[prefix] = dict()
					
				if letter not in self.data[prefix]:
					self.data[prefix][letter] = [ W[3:] ]
				else:
					self.data[prefix][letter].append( W[3:] )
	
	def removeWords(self, words):
		for w in words:
			W = self.normalizedMagicText(w) 
			if W in self.listOfWords:
				self.listOfWords.remove(W)
		self.initialize()
	
	def addWords(self, words):
		for w in words:
			W = self.normalizedMagicText(w)
			if W not in self.listOfWords:
				self.listOfWords.add(W)
		self.initialize()
		
	def getSufixes(self, prefix):
		sufixes = []
		withPrefix = self.data.get(prefix)
		if withPrefix:
			for letter in withPrefix.keys():
				sufixes += withPrefix.get(letter)

		return sufixes
	
	
	def matchShorts(self, input_text):
		text = self.normalizedMagicText(input_text) + '@'
		if len(text)-1 != len(input_text):
			raise Exception('''Normalization string function doesnt presever len of\n\n%s\n\nAborting!'''%input_text)
		
		matches = []
		for cur in range(len(text)-1):
			
			for s in self.shorts.get(text[cur], []):
				if s == text[cur:cur+len(s)]:
					matches.append((s, (cur, cur+len(s))))
		return matches
	
	
	def match(self, input_text):
		if len(input_text)<4:
			return self.matchShorts(input_text)
		
		text = self.normalizedMagicText(input_text)
		if len(text) != len(input_text):
			raise Exception('''Normalization string function doesnt presever len of\n\n%s\n\nAborting!'''%input_text)

		matches = []
		for cur in range(1, len(text)-3):
			if not text[cur].isalpha(): #TODO: agregar cualquier caracter que no esté en PREFIXES
				continue

			curMatch = cur-1	
			prefix = text[curMatch:cur+2]
			sufixes = self.getSufixes(prefix)
			for s in sufixes:
				w = text[curMatch+3:curMatch+3+len(s)]
				
				if s==w:
					matches.append((prefix+s, (curMatch, curMatch+3+len(s))))
		
		matches += self.matchShorts(input_text)
		
		matchCount = dict()
		for word,idx in matches:
			if word not in matchCount.keys():
				matchCount[word] = []
			matchCount[word].append(idx)
			
		return matchCount, None



class replacementSet:
	def __init__(self, inputData):
		self.data = []
		for cursor, replacement in inputData:
			self.data.append( {'a':cursor[0], 'b':cursor[1], 'replacement': replacement } )
		
		self.data = sorted(self.data, key=lambda x: x['b'])
		
		self.memo = [(-1,[])]*len(self.data)
		
		if len(self.data)>0:
			self.memo[0] = (self.data[0]['b']-self.data[0]['a'], [0]) #coverage, indexes of intervals
			self.maxCoverageIndexes = []
			self.maxCoverage = self.memo[0][0]
			
	def maxCoverageIncludingInterval(self, i):
		if self.memo[i][0] != -1:
			return self.memo[i][0]
		else:
			intervalsIndexes = []
			coverage = self.data[i]['b']-self.data[i]['a']
			maxCov = coverage
			
			for k in range(i-1,-1,-1):
				if self.data[k]['b']<=self.data[i]['a']:
					newCov = coverage + self.maxCoverageIncludingInterval(k)
					if (newCov>maxCov) or (newCov==maxCov and len(intervalsIndexes)<len(self.memo[k][1])):
					#if coverage + self.maxCoverageIncludingInterval(k) > maxCoverage:
						maxCov = newCov
						intervalsIndexes = [] + self.memo[k][1]
					
			
			intervalsIndexes.append(i)
			self.memo[i] = (maxCov, intervalsIndexes)
				
			return maxCov
			
	def computeMaximumReplacementSet(self):
		if len(self.data) < 1:
			return []
		else:
			for j in range( len(self.data) ):
				maxCov = self.maxCoverageIncludingInterval(j)
				# update global result
				if maxCov > self.maxCoverage:
					self.maxCoverage = maxCov
					#self.maxCoverageIndexes.append(j)
					
				#elif  maxCov==self.maxCoverage and len(intervalsIndexes)<len( self.memo[self.maxCoverageIndex][1] ):
				#		self.maxCoverageIndex = i
		
		replacementSets = []
		for i in range(len(self.data)):
			if self.memo[i][0] == self.maxCoverage:
				coverageIntervals=[]
				for j in self.memo[i][1]:
					coverageIntervals.append(  ((self.data[j]['a'], self.data[j]['b']), self.data[j]['replacement']) )
				
				replacementSets.append(coverageIntervals)
		
		return replacementSets
			
			
			
# #TODO remover
# with open('apellidos_arg.csv', 'r') as f:
#  	apellidosArg = sorted([x.split(',')[1].strip('\n') for x in f.readlines()])


# def normalizarTexto(text):
#  	# quitar latin1
#  	#return unidecode.unidecode( text.encode('latin-1', 'replace').decode('latin-1'), errors='replace').upper()
#  	return ''.join( [ (unidecode.unidecode(x) if len(unidecode.unidecode(x))==1 else '?') for x in text ]  ).upper()

# APELLIDOSLAR = wordsMagic([x for x in apellidosArg if len(x)>=6], normalizarTexto)
# #APELLIDOSCOR = exactMatcher([x for x in apellidosArg if len(x)<6], normalizarTexto)

# import random
# ape = 'ETERREN'
# for n in range(1000):
# 	t1 = ''.join(['X' if random.randint(0,1)==1 else '' for _ in range(10)])
# 	t2 = ''.join(['X' if random.randint(0,1)==1 else '' for _ in range(10)])
# 	texto = t1 + ape + t2
# 	matchs, matchsErr = APELLIDOSLAR.match(texto)
# 	if len(matchs.keys()) > 0:
# 		if any(['X' in x for x in matchs.keys()]):
#  			print(texto)
#  			break
# 	if len(matchsErr.keys()) > 0:
# 		if any(['X' in x for x in matchs.keys()]):
#  			print(texto)
#  			break
		
	
# listaDeReemplazos = [((1, 10), 'APELLIDO', 0),
#  ((1, 9), 'APELLIDO', 0),
#  ((3, 10), 'APELLIDO', 0),
#  ((11, 18), 'APELLIDO', 0),
#  ((3, 9), 'APELLIDO', 0),
#  ((11, 17), 'APELLIDO', 0),
#  ((21, 27), 'APELLIDO', 0),
#  ((1, 10), 'NOMBRE', 0),
#  ((3, 10), 'NOMBRE', 0)]

# R = replacementSet( sorted(listaDeReemplazos, key=lambda x:x[2]) )

# reemplazos = R.maxCoverageIncludingInterval(6)
