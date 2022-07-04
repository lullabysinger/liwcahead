from collections import defaultdict
import re

class LiwcAhead:
	"""
	Class for encapsulating the dictionary data for replicating liwcalike/liwc functionality.
	"""
	def __init__(self, filename, regex_mode=False):
		self.categories, self.patterns = self.__load_dic(filename)
		self.regex_mode = regex_mode

	def debug(self):
		pprint.pprint(categories)
		pprint.pprint(patterns)

	def __load_dic(self, filename):
		categories = defaultdict(str)
		patterns   = defaultdict(list)
		with open(filename) as dict_file:
			lines = dict_file.readlines()
			reading_categories = True
			for counter, l in zip(range(len(lines)), lines):
				l = l.strip()
				#print(l)
				if counter == 0:
					assert(l == '%')
				elif counter > 0 and reading_categories and l == '%':
					# separator between categories and terms, switch modes
					reading_categories = False
				elif reading_categories and len(l) > 0:
					cat_id, cat_name = l.split('\t')
					categories[cat_id] = cat_name
				elif not reading_categories and len(l) > 0:
					cat_ids = l.split('\t')
					pattern = cat_ids.pop(0) 
					patterns[pattern] = cat_ids
		return categories, patterns


	def get_counts(self, text):
		counts_per_category = defaultdict(int)
		
		# for each pattern...
		for pattern_string in self.patterns:
			matches = re.findall(pattern_string, text) # matches can be used for debugging
			#print(f'for {pattern_string} = {len(matches)}')

			for cat_id in self.patterns[pattern_string]:
				counts_per_category[cat_id] += len(matches)

		return counts_per_category

	def WC(self, text):
		return len(text.split())

	# this should be end-user facing...
	def analyze(self, text):
		counts_per_category = self.get_counts(text)
		total_words = self.WC(text)

		for cat_id in self.categories:
			count = counts_per_category[cat_id]
			percentage = count / total_words
			print(f'{self.categories[cat_id]} \t {count} \t {percentage}')


import pprint
la = LiwcAhead("../../Rtemp/nietzsche.dic")
s = open("../../Rtemp/nietzsche/1895 A.txt").read()

la.analyze(s)

# counts_per_category = get_counts(patterns, s)
# pprint.pprint(counts_per_category)