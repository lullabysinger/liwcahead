from collections import defaultdict
import re
from unidecode import unidecode
import string
from nltk.tokenize import sent_tokenize
from tabulate import tabulate

class LiwcAhead:
    """
    Class for encapsulating the dictionary data for replicating liwcalike/liwc functionality.
    """
    def __init__(self, filename, regex_mode=False):
        self.categories, self.patterns = self.__load_dic(filename)
        self.regex_mode = regex_mode

    def debug(self):
        pprint.pprint(self.categories)
        pprint.pprint(self.patterns)

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
                    if l != '%': # error in file format in line 0
                        raise ValueError("The dict file needs to start with a '%' on a single line.")
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
            # here, we distinguish stock LIWC from regex mode, using the compiled re
            # CASE 1: stock LIWC -- reverse compatibility
            if not self.regex_mode:
                # check that there can either be none or at most one '*'
                if pattern_string.count('*') > 1:
                    raise ValueError("Using compatibility mode, there can only be one '*' in a dictionary pattern.")
                
                # check that, if there exists one '*'
                if pattern_string.count('*') == 1:
                    if pattern_string[-1] != '*': # it must be the end
                        raise ValueError("Using compatibility mode, the '*' wildcard can only appear at the end of a dictionary pattern.")
                
                # patch it to be .* for the regex engine...
                # ... finally compile with case-INsensitivity
                compiled = re.compile(pattern_string.replace('*', '.*'), re.IGNORECASE)
        
            # CASE 2: regex mode - use as usual
            else:
                compiled = re.compiled(pattern_string)

            matches = compiled.findall(text) 
            #print(f'for {pattern_string} = {len(matches)}')

            for cat_id in self.patterns[pattern_string]:
                counts_per_category[cat_id] += len(matches)

        return counts_per_category

    def WC(self, text):
        return len(text.split())

    def WPS(self, text):
        return self.WC(text) * 1.0 / len(sent_tokenize(text))

    def get_stats(self, text):
        stats = defaultdict(list)

        text_nopunct = s.translate(str.maketrans('', '', string.punctuation))
        stats['AllPunc'] = len(text) - len(text_nopunct)

        words = text_nopunct.split()
        words_six = filter(lambda w: len(w) >= 6, words)
        stats['SixLtr'] = len(list(words_six))
        
        # code for the following adapted from Ken Benoit / quanteda.dictionaries
        stats['Period'] = text.count('.')
        stats['Comma'] = text.count(',')
        stats['Colon'] = text.count(':')
        stats['SemiC'] = text.count(';')
        stats['QMark'] = text.count('?')
        stats['Exclam'] = text.count('!')

        # requires unicode cleanup to handle fancy punctuation e.g. em-dashes, smart-quotes
        decoded_text = unidecode(text)
        stats['Dash'] = decoded_text.count('-') 
        stats['Quote'] = decoded_text.count('\"') 
        stats['Aprostro'] = decoded_text.count('\'') 

        # per Benoit:
        # "note this is specified as "pairs of parentheses""
        stats['Parenth'] = min(text.count('('), text.count(')'))

        return stats

    # this should be end-user facing...
    def analyze(self, text):
        output_table = [['Statistic', 'Count', 'Percentage']]
        counts_per_category = self.get_counts(text)
        total_words = self.WC(text)

        for cat_id in self.categories:
            count = counts_per_category[cat_id]
            percentage = count / total_words
            output_table.append([self.categories[cat_id], count, format(percentage, '.10f')])

        stats = self.get_stats(text)

        for s in stats:
            count = stats[s]
            percentage = count / total_words
            output_table.append([s, count, percentage])

        output_table.append(['WPS', count, 'N/A'])
        output_table.append(['WC' , count, 'N/A']) 
        print (tabulate(output_table, headers='firstrow', tablefmt='fancy_grid', floatfmt=".10f"))

        return output_table


def liwcahead_test_nietzsche():
    # testing code ahead
    import pprint
    la = LiwcAhead("../../Rtemp/nietzsche.dic")
    s = open("../../Rtemp/nietzsche/1895 A.txt").read()
    la.analyze(s)




