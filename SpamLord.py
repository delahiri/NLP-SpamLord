import sys
import os
import re
import pprint

# my_first_pat = '(\w+)@(\w+).edu'

# Components of email address
local_part = '(([\w-]+|[\w-]+\.[\w-]+)'
followed_by = '(\s.?\(followed by.*)?'
at = '(\s(at|where)\s|\s?(@|&.*;)\s?)'
domain = '([\w-]+|[\w-]+([\.;]|\s(do?t)\s|\s)[\w-]+)'
dot = '(\s(do?t|do?m)\s|\s|[\.;])'
end = r'''((-?e-?d-?u|-?c-?o-?m|-?n-?e-?t|-?o-?r-?g|-?g-?o-?v)\b)
        |(obfuscate\('(\w+\.(edu|com|net|org|gov))','(\w+)'\)))'''

email_pat = local_part + followed_by + at + domain + dot + end

# Components of phone number
area = '\(?(\d{3})\)?'
separator = '[ -]'
second = '(\d{3})'
last = '(\d{4})'

phone_pat = area + separator + '?' + second + separator + last + '\D+' # No more numbers after this

#print email_pat


"""
TODO
This function takes in a filename along with the file object (actually
a StringIO object) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""
def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        # match email
        matches = re.findall(email_pat, line, re.I|re.VERBOSE) # ignore whitespace and comments and ignore case
        for matched in matches:
            local = ''
            dom = ''
            las = ''
           # print matched
            if matched[13]:
                local = matched[16].replace("-","")
             #  print local
                last_word = matched[14]
             #  print last_word
                last_word_index = last_word.rindex(".")
                dom = last_word[0:last_word_index].replace(" dot ",".").replace("-","").replace("-", "").replace(" ",".").replace(";",".")
             #  print domain
                las = last_word[last_word_index+1:].replace("-", "")
             #  print last
            else:
             #  print matched
                local = matched[1].replace("-","")
                dom = matched[6].replace(" dot ",".").replace("-","").replace("-", "").replace(" ",".").replace(";",".")
                las = matched[12].replace("-", "")
             #  print "local "+local
             #  print "dom "+dom
             #  print "las "+las
            if local and dom and las and local.lower() != 'server':
                email = local + '@' + dom + '.' + las
             # print email
             # print email
                res.append((name, 'e', email))

        # match phone number
        matches = re.findall(phone_pat, line, re.VERBOSE) # ignore whitespace and comments
        for matched in matches:
            area = matched[0]
            sec = matched[1]
            las = matched[2]
            phone = area + '-' + sec + '-' + las
            # print phone
            res.append((name, 'p', phone))
    return res

"""
You should not need to edit this function, nor should you alter
its interface
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
