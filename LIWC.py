# Language Style Matching module. 

import os
import re
import StringIO
import sys
import utilities.io
from settings import *
import operator
import collections

# Tag codes which are relevant to Language Style Matching. 
LSM_CODES = [3, 9, 10, 12, 16, 17, 18, 19, 20] 
SEXUAL_CODES = [149]
TOPIC_CODES = [149, 354, 355, 356, 357, 358, 359, 360]
PERSONALITY_CODES = [565, 566, 567, 568, 569, 570, 571, 572, 573, 574] 

# LIWC2007 dictionary is needed to correctly parse text according to the LSM 
# algorithm (see 'Language Style Matching Predicts Relationship Initiation and 
# Stability' by Ireland et al. 2011).
# LIWC2007 was downloaded from http://code.google.com/p/negotiations-ling773/ - 
# TODO I believe it may be proprietary data obtained from http://www.liwc.net/.

class LiwcTag(object):
	def __str__(self):
		return "%s_%s" % (str(self.code), self.tag) 
		
	def __repr__(self):
		return self.__str__() 
		
	def __init__(self, code, tag):
		self.code = int(code)
		self.tag = tag 

class  LiwcWord(object): 
	def __init__(self, word):
		self.word = word
		self.tags = []
		
	def __len__(self):
		return len(self.word)
		
	def __getitem__(self, index):
		return self.word.__getitem__(index) 
		
	def __str__(self):
		return self.word
	
	def append_tag(self, tag):
		self.tags.append(tag)

class LiwcDict(utilities.io.Pickle): 
	all_words = [] 
	def __init__(self, dict_loc = LIWC2007_LOC, **kwargs):
		self.dict_loc = dict_loc
		# See http://www.liwc.net/descriptiontable1.php for a description of each tag.
		self.tags_dict = {}
		self.words = []
		self.pickle_file_format = PICKLE_LOC 
		if kwargs.get("unpickle", False):
				self.unpickle()
				self.__class__.all_words = self.words
				
		else:
			self.construct_LIWC_dict()
			self.pickle()
		# None means all codes. 
		self.codes = None
	
	# Iterating over LiwcDict instance will iterate over the word strings
	# it contains. 
	def __iter__(self):
		for w in self.words:
			yield w.word
	
	# TODO performance can be improved by improving this function. 
	def word_cmp(self, s1, s2):
		if s1[len(s1) - 1] == WORD_STEM_DELIMITER:
			s1 = s1[:len(s1) - 1] 
			if len(s2) > len(s1):
				s2 = s2[:len(s1)]
		
		elif s2[len(s2) - 1] == WORD_STEM_DELIMITER: 
			s2 = s2[:len(s2) - 1] 
			if len(s1) > len(s2):
				s1 = s1[0:len(s2)]	
		if s1 > s2:
			return 1
		elif s2 > s1:
			return -1
		return 0 
				
		

	# Binary search of words associated with this dictionary. TODO If word
	# ends with *, than we have a problem...
	def search(self, s):
		# Binary search 
		r = 0
		min = 0
		max = len(self.words) - 1
		while 1:
			if max < min:
				return None
			m = (min + max) / 2
			r = self.word_cmp(self.words[m].word, s)
			if r < 0:
				min = m + 1
			elif r > 0:
				max = m - 1
			else:
				# print s, self.words[m]
				return self.words[m]
		
		'''
		# Standard search - if we get a print, something must have gone wrong. 
		for w in self.words:
			if self.word_cmp(w.word, s) == 0:
				return w
		return None
		'''	
		
            
	def print_words(self):
		for w in self.words:
			print w.word,
			for t in w.tags:
				print t.code, 
			print
	
	def code_fltr(self, w):
		temp_tags = []
		for t in w.tags:
			if t.code in self.codes:
				temp_tags.append(t)
		if len(temp_tags) > 0:
			w.tags = temp_tags
			return True
		return False 
		
	def fltr(self, *args):
		self.words = self.__class__.all_words
		if "LSM" in args:
			self.codes = LSM_CODES
			
		if "sexual" in args:
			self.codes = SEXUAL_CODES
			
		if "topic" in args:
			self.codes = TOPIC_CODES
			
		if "personality" in args:
			self.codes = PERSONALITY_CODES
		
		self.words = filter(self.code_fltr, self.words) 

	def construct_LIWC_dict(self):
		f = open(self.dict_loc, 'r')
		raw_dict = f.read().split(DIVIDER)
		raw_words = StringIO.StringIO(raw_dict[2])
		raw_tags = StringIO.StringIO(raw_dict[1])
		for line in raw_tags.readlines():
			match = re.search(TAGS_REGEX, line)
			if match:
				print match.group(CODE_GROUP), match.group(TAG_GROUP)
				self.tags_dict[int(match.group(CODE_GROUP))] = LiwcTag(int(match.group(CODE_GROUP)), match.group(TAG_GROUP))
		cur_word = None
		for line in raw_words.readlines():
			match = re.search(WORDS_REGEX_WORD, line)
			if match:
				print match.group()
				self.words.append(LiwcWord(match.group()))
			match = re.findall(WORDS_REGEX_CODE, line)
			for m in match:
				self.words[len(self.words)-1].append_tag(self.tags_dict[int(m)]) 
		print self.tags_dict
		f.close()
	
	# Must pass in own counts object so that it can be filled and the changes
	# will persist. 
	def count(self, material, **kwargs):
		
		counts = LiwcCounts()
		
		if kwargs.get("fltr", False):
			self.fltr(kwargs["fltr"])
			
		# Create an entry for all tags in counts. Ensures that if no 
		# instance of a particular tag is found, still get a zero count
		# as opposed to having it ommited from the LiwcCounts instance
		# which is returned. 
		# This is desirable if we want the same number of statistics
		# for every analysis performed by the Stat.us module. 
		for w in self.words:
			for t in w.tags:
				counts[self.tags_dict[t.code]] = 0.0
				
		# Iterate over material and check for matches. 
		for m in material:
			match = self.search(m)
			if match:
				for t in match.tags:
					counts[self.tags_dict[t.code]] += 1
								
		if kwargs.get("no_zero", False):
			for k in counts:
				if counts[k] == 0.0:
					counts.pop(k)
					
		return counts
			
class LiwcCounts(collections.OrderedDict):
	def __init__(self, *args, **kwargs): 
		super(LiwcCounts, self).__init__(*args, **kwargs)
		
	def __str__(self):
		s = ''
		for t in self.srtd():
			s += t[0].tag + "(%.2f%%)" % t[1] + ", " 
			
		return s 
				
	def transform(self, denom, *args):
		for i in self:
			self[i] = (float(self[i])/denom)
			if "percentage" in args:
				self[i] = self[i] * 100
	
	# TODO Redundant because class inherits from OrderedDict.		
	def srtd(self):
		return sorted(self.iteritems(), key=operator.itemgetter(1), reverse=True)
		
	# Iterates over the raw counts.  	
	def raw(self):
		for v in self.srtd():
			yield v[1]
			

