import numpy as np
import pandas as pd
import math
import random
import string

def random_partition(k, iterable):
    results = [[] for i in range(k)]
    for value in iterable:
        x = random.randrange(k)
        results[x].append(value)
    return results

def random_strings(k, rawchars):
    results = ["" for i in range(k)]
    for c in rawchars:
        x = random.randrange(k)
        results[x] += c
    return results

def get_morse_str(nchars=132, nwords=27, chars=None):
    if not chars:
        chars = string.ascii_uppercase + string.digits
    rawchars = ''.join(random.choice(chars) for _ in range(nchars))
    words = random_strings(nwords, rawchars)
    morsestr = ' '.join(words)
    return morsestr

def get_morse_eles(nchars=132, nwords=27, max_elt=5):
    neles = nchars*2
    raweles = ''.join(random.choice(".-") for _ in range(neles))
    morse_chars = []
    while len(raweles) > 0:
        s = random.choice(list(range(1, max_elt+1)))
        morse_chars.append(raweles[:s])
        raweles = raweles[s:]
    return random_partition(nwords, morse_chars)


class Encoder:
    def __init__(self, samples_per_dit, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.randomness = randomness
        
    def add_dit(rows, samples_per_dit):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit        
        cols = {"env": 1.0, "dit": 1.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        for i in range(samples_per_dit):
            rows.append(cols)
            
    def add_dah(rows, samples_per_dit):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit        
        cols = {"env": 1.0, "dit": 0.0, "dah": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        for i in range(3*samples_per_dit):
            rows.append(cols)
            
    def add_ele(rows, samples_per_dit):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit        
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0}
        for i in range(samples_per_dit):
            rows.append(cols)

    def add_chr(rows, samples_per_dit):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit        
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0}
        for i in range(2*samples_per_dit):
            rows.append(cols)

    def add_wrd(rows, samples_per_dit):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit        
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0}
        for i in range(4*samples_per_dit):
            rows.append(cols)

            
class DecimEncoder:
    def __init__(self, samples_per_dit, decim, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.randomness = randomness
        
    def add_dit(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 1.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim): 
                rows.append(cols)    
            self.sample_count += 1
        
    def add_dah(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 0.0, "dah": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_ele(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_chr(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0}
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_wrd(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0}
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_dah2(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 1.0, "dah": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_chr2(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 1.0, "chr": 1.0, "wrd": 0.0}
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_wrd2(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 1.0, "chr": 1.0, "wrd": 1.0}
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

class DecimEncoderStr:
    def __init__(self, samples_per_dit, decim, alphabet, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.alphabet = alphabet
        self.randomness = randomness
        
    def add_dit(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 1.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        alpha = {x: 1.0 if x == ck else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim): 
                rows.append(cols)    
            self.sample_count += 1
        
    def add_dah(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 0.0, "dah": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        alpha = {x: 1.0 if x == ck else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_ele(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0}
        alpha = {x: 1.0 if x == ck else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_chr(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0}
        alpha = {x: 1.0 if x == ck else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_wrd(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0}
        alpha = {x: 1.0 if x == ck else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
                        
class DecimEncoderBlankStr:
    def __init__(self, samples_per_dit, decim, alphabet, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.alphabet = alphabet
        self.randomness = randomness
        
    def add_dit(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 1.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0, "blk": 1.0}
        alpha = {x: 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim): 
                rows.append(cols)    
            self.sample_count += 1
        
    def add_dah(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 0.0, "dah": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0, "blk": 1.0}
        alpha = {x: 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_ele(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0, "blk": 1.0}
        alpha = {x: 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_chr(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0, "blk": 0.0}
        alpha = {x: 1.0 if x == ck else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_wrd(self, rows, ck):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0, "blk": 1.0}
        alpha = {x: 1.0 if x == ck else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
class DecimEncoderTree:
    def __init__(self, samples_per_dit, decim, alphabet, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.alphabet = alphabet
        self.randomness = randomness
        self.exclusive = False # each label except envelope is exclusive among others (no overlaps)
        self.state = "start"
        self.morse_tree = {
            "start": ("T", "E"),
            "T": ("M", "N"),
            "E": ("A", "I"),
            "M": ("O", "G"),
            "N": ("K", "D"),
            "A": ("W", "R"),
            "I": ("U", "S"),
            "O": ("Odash", "Odit"),
            "G": ("Q", "Z"),
            "K": ("Y", "C"),
            "D": ("X", "B"),
            "W": ("J", "P"),
            "R": (None, "L"),
            "U": ("Udash", "F"),
            "S": ("V", "H"),
            "Odash": ("0", "9"),
            "Odit": (None, "8"),
            "Q": (None, None),
            "Z": (None, "7"),
            "Y": (None, None),
            "C": (None, None),
            "X": (None, None),
            "B": (None, "6"),
            "J": ("1", None),
            "P": (None, None),
            "L": (None, None),
            "Udash": ("2", None),
            "F": (None, None),
            "V": ("3", None),
            "H": ("4", "5"),
            "0": (None, None),
            "1": (None, None),
            "2": (None, None),
            "3": (None, None),
            "4": (None, None),
            "5": (None, None),
            "6": (None, None),
            "7": (None, None),
            "8": (None, None),
            "9": (None, None),
        }
        
    def add_dit(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 1.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0, "nul": 0.0}
        next_state = self.morse_tree[self.state][1] # right
        if next_state is not None:
            self.state = next_state
            c = self.state if len(self.state) == 1 else ""
        else:
            c = ""
        if c == "":
            cols["nul"] = 1.0
        alpha = {x: 1.0 if x == c else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim): 
                rows.append(cols)    
            self.sample_count += 1
    
    def add_dah(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "dit": 0.0, "dah": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0, "nul": 0.0}
        next_state = self.morse_tree[self.state][0] # left
        if next_state is not None:
            self.state = next_state
            c = self.state if len(self.state) == 1 else ""
        else:
            c = ""
        if c == "":
            cols["nul"] = 1.0
        alpha = {x: 1.0 if x == c else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
    
    def add_ele(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0, "nul": 0.0}
        if self.exclusive:
            alpha = {x: 0.0 for x in self.alphabet}
        else:
            c = self.state if len(self.state) == 1 else ""
            if c == "":
                cols["nul"] = 1.0        
            alpha = {x: 1.0 if x == c else 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_chr(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0, "nul": 0.0}
        if self.exclusive:
            alpha = {x: 0.0 for x in self.alphabet}
        else:
            c = self.state if len(self.state) == 1 else ""
            if c == "":
                cols["nul"] = 1.0        
            alpha = {x: 1.0 if x == c else 0.0 for x in self.alphabet}
        self.state = "start"
        cols = {**cols, **alpha}
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_wrd(self, rows):
        self.state = "start"
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "dit": 0.0, "dah": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0, "nul": 0.0}
        alpha = {x: 0.0 for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
    

class DecimEncoderTreeSoft:
    def __init__(self, samples_per_dit, decim, alphabet, ones, zeros, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.alphabet = alphabet
        self.ones = ones
        self.zeros = zeros
        self.randomness = randomness
        self.exclusive = False # each label except envelope is exclusive among others (no overlaps)
        self.state = "start"
        self.morse_tree = {
            "start": ("T", "E"),
            "T": ("M", "N"),
            "E": ("A", "I"),
            "M": ("O", "G"),
            "N": ("K", "D"),
            "A": ("W", "R"),
            "I": ("U", "S"),
            "O": ("Odash", "Odit"),
            "G": ("Q", "Z"),
            "K": ("Y", "C"),
            "D": ("X", "B"),
            "W": ("J", "P"),
            "R": (None, "L"),
            "U": ("Udash", "F"),
            "S": ("V", "H"),
            "Odash": ("0", "9"),
            "Odit": (None, "8"),
            "Q": (None, None),
            "Z": (None, "7"),
            "Y": (None, None),
            "C": (None, None),
            "X": (None, None),
            "B": (None, "6"),
            "J": ("1", None),
            "P": (None, None),
            "L": (None, None),
            "Udash": ("2", None),
            "F": (None, None),
            "V": ("3", None),
            "H": ("4", "5"),
            "0": (None, None),
            "1": (None, None),
            "2": (None, None),
            "3": (None, None),
            "4": (None, None),
            "5": (None, None),
            "6": (None, None),
            "7": (None, None),
            "8": (None, None),
            "9": (None, None),
        }
        
    def add_dit(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "ele": self.zeros[0], "chr": self.zeros[0], "wrd": self.zeros[0], "nul": self.zeros[0]}
        next_state = self.morse_tree[self.state][1] # right
        if next_state is not None:
            self.state = next_state
            c = self.state if len(self.state) == 1 else ""
        else:
            c = ""
        if c == "":
            cols["nul"] = self.ones[0]
        alpha = {x: self.ones[0] if x == c else self.zeros[0] for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim): 
                rows.append(cols)    
            self.sample_count += 1
    
    def add_dah(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "ele": self.zeros[0], "chr": self.zeros[0], "wrd": self.zeros[0], "nul": self.zeros[0]}
        next_state = self.morse_tree[self.state][0] # left
        if next_state is not None:
            self.state = next_state
            c = self.state if len(self.state) == 1 else ""
        else:
            c = ""
        if c == "":
            cols["nul"] = self.ones[0]
        alpha = {x: self.ones[0] if x == c else self.zeros[0] for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
    
    def add_ele(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": self.ones[1], "chr": self.zeros[1], "wrd": self.zeros[1], "nul": self.zeros[1]}
        if self.exclusive:
            alpha = {x: self.zeros[0] for x in self.alphabet}
        else:
            c = self.state if len(self.state) == 1 else ""
            if c == "":
                cols["nul"] = self.ones[1]        
            alpha = {x: self.ones[1] if x == c else self.zeros[1] for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_chr(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": self.zeros[1], "chr": self.ones[1], "wrd": self.zeros[1], "nul": self.zeros[1]}
        if self.exclusive:
            alpha = {x: self.zeros[0] for x in self.alphabet}
        else:
            c = self.state if len(self.state) == 1 else ""
            if c == "":
                cols["nul"] = self.ones[1]        
            alpha = {x: self.ones[1] if x == c else self.zeros[1] for x in self.alphabet}
        self.state = "start"
        cols = {**cols, **alpha}
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_wrd(self, rows):
        self.state = "start"
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": self.zeros[0], "chr": self.zeros[0], "wrd": self.ones[0], "nul": self.zeros[0]}
        alpha = {x: self.zeros[0] for x in self.alphabet}
        cols = {**cols, **alpha}
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

            
class DecimEncoderDitDahLen:
    def __init__(self, samples_per_dit, decim, max_ele, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.max_ele = max_ele
        self.randomness = randomness
        self.elt_count = 0
        
    def add_dit(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        ditp = {f'{i}d': 1.0 if i == self.elt_count else 0.0 for i in range(self.max_ele)}
        dahp = {f'{i}D': 0.0 for i in range(self.max_ele)}
        self.elt_count += 1
        cols = {**cols, **ditp, **dahp}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
        
    def add_dah(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        ditp = {f'{i}d': 0.0 for i in range(self.max_ele)}
        dahp = {f'{i}D': 1.0 if i == self.elt_count else 0.0 for i in range(self.max_ele)}
        self.elt_count += 1
        cols = {**cols, **ditp, **dahp}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_ele(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0}
        ditp = {f'{i}d': 0.0 for i in range(self.max_ele)}
        dahp = {f'{i}D': 0.0 for i in range(self.max_ele)}
        cols = {**cols, **ditp, **dahp}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_chr(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0}
        ditp = {f'{i}d': 0.0 for i in range(self.max_ele)}
        dahp = {f'{i}D': 0.0 for i in range(self.max_ele)}
        cols = {**cols, **ditp, **dahp}
        self.elt_count = 0
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_wrd(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0}
        ditp = {f'{i}d': 0.0 for i in range(self.max_ele)}
        dahp = {f'{i}D': 0.0 for i in range(self.max_ele)}
        cols = {**cols, **ditp, **dahp}
        self.elt_count = 0
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

            
class DecimEncoderOrd:
    def __init__(self, samples_per_dit, decim, max_ele, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.max_ele = max_ele
        self.randomness = randomness
        self.elt_count = 0
        self.overlap_elt_sep = False # dah or dit overlap with element separator
        
    def add_dit(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        elep = {f'e{i}': 1.0 if i == self.elt_count else 0.0 for i in range(self.max_ele)}
        cols = {**cols, **elep}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
        
    def add_dah(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0}
        elep = {f'e{i}': 1.0 if i == self.elt_count else 0.0 for i in range(self.max_ele)}
        cols = {**cols, **elep}
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_ele(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0}
        if self.overlap_elt_sep :
            elep = {f'e{i}': 1.0 if i == self.elt_count else 0.0 for i in range(self.max_ele)}
        else:
            elep = {f'e{i}': 0.0 for i in range(self.max_ele)}
        self.elt_count += 1
        cols = {**cols, **elep}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_chr(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0}
        elep = {f'e{i}': 0.0 for i in range(self.max_ele)}
        cols = {**cols, **elep}
        self.elt_count = 0
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_wrd(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        cols = {"env": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0}
        elep = {f'e{i}': 0.0 for i in range(self.max_ele)}
        cols = {**cols, **elep}
        self.elt_count = 0
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
            
class DecimEncoderVal:
    def __init__(self, samples_per_dit, decim, max_ele, randomness):
        self.sample_count = 0
        self.samples_per_dit = samples_per_dit
        self.decim = decim # will retain 1 over decim samples
        self.max_ele = max_ele
        self.randomness = randomness
        self.elt_count = self.max_ele - 1
        self.val = 0
        self.bias = 3**(self.max_ele-1) - 1
        
    def add_dit(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        self.val += 3**(self.elt_count)
        val = self.val - self.bias
        cols = {"env": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0, "val": val}
        self.elt_count -= 1
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
        
    def add_dah(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        self.val += 2*(3**(self.elt_count))
        val = self.val - self.bias
        cols = {"env": 1.0, "ele": 0.0, "chr": 0.0, "wrd": 0.0, "val": val}
        self.elt_count -= 1
        for i in range(3*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1

    def add_ele(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        val = self.val - self.bias if self.val > 0 else 0
        cols = {"env": 0.0, "ele": 1.0, "chr": 0.0, "wrd": 0.0, "val": val}
        for i in range(samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_chr(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        val = self.val - self.bias if self.val > 0 else 0
        cols = {"env": 0.0, "ele": 0.0, "chr": 1.0, "wrd": 0.0, "val": val}
        self.elt_count = self.max_ele - 1
        self.val = 0
        for i in range(2*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
    def add_wrd(self, rows):
        samples_per_dit = np.random.randint(-self.randomness, self.randomness+1) + self.samples_per_dit
        val = self.val - self.bias if self.val > 0 else 0
        cols = {"env": 0.0, "ele": 0.0, "chr": 0.0, "wrd": 1.0, "val": val}
        self.elt_count = self.max_ele - 1
        self.val = 0
        for i in range(4*samples_per_dit):
            if int(self.sample_count/self.decim) != int((self.sample_count+1)/self.decim):
                rows.append(cols)
            self.sample_count += 1
            
            
class SoftMaxEq():
    def __init__(self, N):
        self.e = np.exp(1)
        self.e_1 = 1/self.e
        self.N = N
        
    def _den(self, n):
        return n*self.e + (self.N-n)*self.e_1 if self.N > n else 1
    
    def on(self, n):
        return self.e / self._den(n)

    def off(self, n):
        return self.e_1 / self._den(n)
    
    def scal(self):
        return self._den(1) / self.e

    
class Morse:
    def __init__(self):
        self.morsecode = {
            '0': '-----',
            '1': '.----',
            '2': '..---',
            '3': '...--',
            '4': '....-',
            '5': '.....',
            '6': '-....',
            '7': '--...',
            '8': '---..',
            '9': '----.',        
            'A': '.-',
            'B': '-...',
            'C': '-.-.',
            'D': '-..',
            'E': '.',
            'F': '..-.',
            'G': '--.',
            'H': '....',
            'I': '..',
            'J': '.---',
            'K': '-.-',
            'L': '.-..',
            'M': '--',
            'N': '-.',
            'O': '---',
            'P': '.--.',
            'Q': '--.-',
            'R': '.-.',
            'S': '...',
            'T': '-',
            'U': '..-',
            'V': '...-',
            'W': '.--',
            'X': '-..-',
            'Y': '-.--',
            'Z': '--..',    
            '/': '-..-.',
            '(': '-.--.',
            '=': '-...-',
            '+': '.-.-.',
            'Á': '.--.-',
            'Ä': '.-.-',
            'É': '..-..',
            'Ñ': '--.--',
            'Ö': '---.',
            'Ü': '..--',
        }
        self.revmorsecode = {
            '-----': '0',
            '.----': '1',
            '..---': '2',
            '...--': '3',
            '....-': '4',
            '.....': '5',
            '-....': '6',
            '--...': '7',
            '---..': '8',
            '----.': '9',        
            '.-':    'A',
            '-...':  'B',
            '-.-.':  'C',
            '-..':   'D',
            '.':     'E',
            '..-.':  'F',
            '--.':   'G',
            '....':  'H',
            '..':    'I',
            '.---':  'J',
            '-.-':   'K',
            '.-..':  'L',
            '--':    'M',
            '-.':    'N',
            '---':   'O',
            '.--.':  'P',
            '--.-':  'Q',
            '.-.':   'R',
            '...':   'S',
            '-':     'T',
            '..-':   'U',
            '...-':  'V',
            '.--':   'W',
            '-..-':  'X',
            '-.--':  'Y',
            '--..':  'Z',    
            '-..-.': '/',
            '-.--.': '(',
            '-...-': '=',
            '.-.-.': '+',
            '.--.-': 'Á',
            '.-.-':  'Ä',
            '..-..': 'É',
            '--.--': 'Ñ',
            '---.':  'Ö',
            '..--':  'Ü',
        }        
        self.alphabet = ''.join(self.morsecode.keys())
        self.alphabet2 = 'ET'
        self.alphabet6 = self.alphabet2 + 'IAMN' # 'MNAI'
        self.alphabet14 = self.alphabet6 + 'SURWOGKD' # 'OGKDWRUS'
        self.alphabet26 = self.alphabet14 + 'HVFLPJQZYCXB' # 'QZYCXBJPLFVH'
        self.alphabet36 = self.alphabet26 + '5432109876' # '0123456789'

    def _cws_to_cw(self, cws):
        s=[]
        for c in cws:
            try: # try to find CW sequence from Codebook
                s += self.morsecode[c]
                s += ' '
            except:
                s += '_'
                continue
        return ''.join(s)        

    def cws_to_cwss(self, cws):
        cwss = []
        cws_words = cws.split(' ')
        for cwsw in cws_words:
            s = []
            for c in cwsw:
                cw = self.morsecode.get(c)
                if cw:
                    s.append(cw)
            if s:
                cwss.append(s)
        return cwss
    
    def _morse_env(self, morse_code, samples_per_dit):
        env = np.zeros(samples_per_dit)
        for c in morse_code:
            if c == '.': # dit
                env = np.append(env, np.ones(samples_per_dit))
            elif c == '-': # dah
                env = np.append(env, np.ones(3*samples_per_dit))
            elif c == ' ': # character separator
                env = np.append(env, np.zeros(2*samples_per_dit))
            elif c == '_': # word separaor
                env = np.append(env, np.zeros(3*samples_per_dit))
            env = np.append(env, np.zeros(samples_per_dit)) # element separator
        return env

    @staticmethod
    def nb_samples_per_dit(Fs=8000, code_speed=20):
        # One dit of time at w wpm is 1.2/w.
        t_dit = 1.2 / code_speed
        return int(t_dit * Fs)        

    @staticmethod
    def nb_samples_per_dit_decim(Fs=8000, code_speed=20, decim=5.77):
        # One dit of time at w wpm is 1.2/w.
        t_dit = 1.2 / code_speed
        return int(t_dit * Fs), int(t_dit * Fs) / decim        

    @staticmethod
    def max_ele(alphabet):
        if len(alphabet) <= 2:
            max_ele = 1
        elif len(alphabet) <= 6:
            max_ele = 2
        elif len(alphabet) <= 14:
            max_ele = 3            
        elif len(alphabet) <= 26:
            max_ele = 4
        else:
            max_ele = 5  
        return max_ele
    
    def _morse_df(self, morse_code, encoder):
        rows = []
        encoder.add_ele(rows, samples_per_dit)
        for c in morse_code:
            if c == '.': # dit
                encoder.add_dit(rows)
                encoder.add_ele(rows)
            elif c == '-': # dah
                encoder.add_dah(rows)
                encoder.add_ele(rows)
            elif c == ' ': # character separator
                encoder.add_chr(rows)
            elif c == '_': # word separaor
                encoder.add_wrd(rows)
        return pd.DataFrame(rows, columns=["env","dit","dah","ele","chr","wrd"])
        
    def _morse_df_decim(self, morse_code, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows)
        for c in morse_code:
            if c == '.': # dit
                decim_encoder.add_dit(rows)
                decim_encoder.add_ele(rows)
            elif c == '-': # dah
                decim_encoder.add_dah(rows)
                decim_encoder.add_ele(rows)
            elif c == ' ': # character separator
                decim_encoder.add_chr(rows)
            elif c == '_': # word separaor
                decim_encoder.add_wrd(rows)
        return pd.DataFrame(rows, columns=["env","dit","dah","ele","chr","wrd"])
        
    def _morse_df_decim2(self, morse_code, decim, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows)
        for c in morse_code:
            if c == '.': # dit
                decim_encoder.add_dit(rows)
                decim_encoder.add_ele(rows)
            elif c == '-': # dah
                decim_encoder.add_dah(rows)
                decim_encoder.add_ele(rows)
            elif c == ' ': # character separator
                decim_encoder.add_chr2(rows)
            elif c == '_': # word separaor
                decim_encoder.add_wrd2(rows)
        return pd.DataFrame(rows, columns=["env","dit","dah","ele","chr","wrd"])
    
    def _morse_df_decim_str(self, cws, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows, ' ')
        for c in cws:
            ck = self.morsecode.get(c, '_')
            for s in ck:
                if s == '.': # dit
                    decim_encoder.add_dit(rows, c)
                    decim_encoder.add_ele(rows, c)
                elif s == '-': # dah
                    decim_encoder.add_dah(rows, c)
                    decim_encoder.add_ele(rows, c)
            if ck == '_':
                decim_encoder.add_wrd(rows, ' ')
            else:
                decim_encoder.add_chr(rows, ' ')
        cols=["env","dit","dah","ele","chr","wrd"] + [x for x in decim_encoder.alphabet]        
        return pd.DataFrame(rows, columns=cols)
                    
    def _morse_df_decim_blk_str(self, cws, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows, ' ')
        for c in cws:
            ck = self.morsecode.get(c, '_')
            for s in ck:
                if s == '.': # dit
                    decim_encoder.add_dit(rows, c)
                    decim_encoder.add_ele(rows, c)
                elif s == '-': # dah
                    decim_encoder.add_dah(rows, c)
                    decim_encoder.add_ele(rows, c)
            if ck == '_':
                decim_encoder.add_wrd(rows, ' ')
            else:
                decim_encoder.add_chr(rows, c)
        cols=["env","dit","dah","ele","chr","wrd","blk"] + [x for x in decim_encoder.alphabet]        
        return pd.DataFrame(rows, columns=cols)
                    
    def _morse_df_decim_tree(self, morse_code, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows)
        for c in morse_code:
            if c == '.': # dit
                decim_encoder.add_dit(rows)
                decim_encoder.add_ele(rows)
            elif c == '-': # dah
                decim_encoder.add_dah(rows)
                decim_encoder.add_ele(rows)
            elif c == ' ': # character separator
                decim_encoder.add_chr(rows)
            elif c == '_': # word separaor
                decim_encoder.add_wrd(rows)
        cols = ["env","dit","dah","ele","chr","wrd", "nul"] + [x for x in decim_encoder.alphabet]
        return pd.DataFrame(rows, columns=cols)        
        
    def _morse_df_decim_tree_soft(self, morse_code, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows)
        for c in morse_code:
            if c == '.': # dit
                decim_encoder.add_dit(rows)
                decim_encoder.add_ele(rows)
            elif c == '-': # dah
                decim_encoder.add_dah(rows)
                decim_encoder.add_ele(rows)
            elif c == ' ': # character separator
                decim_encoder.add_chr(rows)
            elif c == '_': # word separaor
                decim_encoder.add_wrd(rows)
        cols = ["env","ele","chr","wrd", "nul"] + [x for x in decim_encoder.alphabet]
        return pd.DataFrame(rows, columns=cols)        

    def _morse_df_decim_ddp(self, morse_code, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows)
        for c in morse_code:
            if c == '.': # dit
                decim_encoder.add_dit(rows)
                decim_encoder.add_ele(rows)
            elif c == '-': # dah
                decim_encoder.add_dah(rows)
                decim_encoder.add_ele(rows)
            elif c == ' ': # character separator
                decim_encoder.add_chr(rows)
            elif c == '_': # word separaor
                decim_encoder.add_wrd(rows)
        cols = ["env","ele","chr","wrd"]
        ditp = [f'{i}d' for i in range(decim_encoder.max_ele)]
        dahp = [f'{i}D' for i in range(decim_encoder.max_ele)]
        cols = cols + ditp + dahp
        return pd.DataFrame(rows, columns=cols)        
        
    def _morse_df_decim_ord(self, morse_code, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows)
        for c in morse_code:
            if c == '.': # dit
                decim_encoder.add_dit(rows)
                decim_encoder.add_ele(rows)
            elif c == '-': # dah
                decim_encoder.add_dah(rows)
                decim_encoder.add_ele(rows)
            elif c == ' ': # character separator
                decim_encoder.add_chr(rows)
            elif c == '_': # word separaor
                decim_encoder.add_wrd(rows)
        cols = ["env","ele","chr","wrd"]
        elep = [f'e{i}' for i in range(decim_encoder.max_ele)]
        cols = cols + elep
        return pd.DataFrame(rows, columns=cols)        
                
    def _morse_df_decim_val(self, morse_code, decim_encoder):
        rows = []
        decim_encoder.add_ele(rows)
        for c in morse_code:
            if c == '.': # dit
                decim_encoder.add_dit(rows)
                decim_encoder.add_ele(rows)
            elif c == '-': # dah
                decim_encoder.add_dah(rows)
                decim_encoder.add_ele(rows)
            elif c == ' ': # character separator
                decim_encoder.add_chr(rows)
            elif c == '_': # word separaor
                decim_encoder.add_wrd(rows)
        cols = ["env","ele","chr","wrd","val"]
        return pd.DataFrame(rows, columns=cols)        
                
    def encode_env(self, cws, samples_per_dit):
        cw = self._cws_to_cw(cws)
        return self._morse_env(cw, samples_per_dit)
    
    def encode_df(self, cws, samples_per_dit, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        encoder = Encoder(samples_per_dit, dit_randomness)
        return self._morse_df(cw, encoder)
    
    def encode_df_decim(self, cws, samples_per_dit, decim, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        decim_encoder = DecimEncoder(samples_per_dit, decim, dit_randomness)
        return self._morse_df_decim(cw, decim_encoder)
    
    def encode_df_decim2(self, cws, samples_per_dit, decim, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        decim_encoder = DecimEncoder(samples_per_dit, decim, dit_randomness)
        return self._morse_df_decim2(cw, decim_encoder)

    def encode_df_decim_str(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        decim_encoder = DecimEncoderStr(samples_per_dit, decim, alphabet, dit_randomness)
        return self._morse_df_decim_str(cws, decim_encoder)

    def encode_df_decim_blk_str(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        decim_encoder = DecimEncoderBlankStr(samples_per_dit, decim, alphabet, dit_randomness)
        return self._morse_df_decim_blk_str(cws, decim_encoder)

    def encode_df_decim_tree(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        decim_encoder = DecimEncoderTree(samples_per_dit, decim, alphabet, dit_randomness)
        return self._morse_df_decim_tree(cw, decim_encoder)

    def encode_df_decim_tree_softmax(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        smeq = SoftMaxEq(len(alphabet) + 4)
        zeros = [smeq.off(1), smeq.off(2)]
        ones = [smeq.on(1), smeq.on(2)]
        decim_encoder = DecimEncoderTreeSoft(samples_per_dit, decim, alphabet, ones, zeros, dit_randomness)
        return self._morse_df_decim_tree_soft(cw, decim_encoder)

    def encode_df_decim_tree_eqp(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        zeros = [0.0, 0.0]
        ones = [1.0, 0.5]
        decim_encoder = DecimEncoderTreeSoft(samples_per_dit, decim, alphabet, ones, zeros, dit_randomness)
        return self._morse_df_decim_tree_soft(cw, decim_encoder)

    def encode_df_decim_ddp(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        decim_encoder = DecimEncoderDitDahLen(samples_per_dit, decim, self.max_ele(alphabet), dit_randomness)
        return self._morse_df_decim_ddp(cw, decim_encoder)
    
    def encode_df_decim_ord(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        decim_encoder = DecimEncoderOrd(samples_per_dit, decim, self.max_ele(alphabet), dit_randomness)
        return self._morse_df_decim_ord(cw, decim_encoder)    
    
    def encode_df_decim_val(self, cws, samples_per_dit, decim, alphabet, dit_randomness=0):
        cw = self._cws_to_cw(cws)
        decim_encoder = DecimEncoderVal(samples_per_dit, decim, self.max_ele(alphabet), dit_randomness)
        return self._morse_df_decim_val(cw, decim_encoder)        
    
    def encode_df_decim_ord_morse(self, cwss, samples_per_dit, decim, max_elt, dit_randomness=0, overlap_elt_sep=False):
        if not cwss:
            cwss = get_morse_eles(max_elt=max_elt)
        cws = cws = list(map(lambda x: ' '.join(x), cwss))
        cw = ' _'.join(cws)
        decim_encoder = DecimEncoderOrd(samples_per_dit, decim, max_elt, dit_randomness)
        decim_encoder.overlap_elt_sep = overlap_elt_sep
        return self._morse_df_decim_ord(cw, decim_encoder)    
        