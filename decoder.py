import morse
import numpy as np

class MorseDecoderRegen:
    def __init__(self, alphabet=morse.alphabet, dit_len=8, max_ele=5, thr=0.9, his_len=400):
        self.nb_alpha = len(alphabet)
        self.alphabet = alphabet
        self.dit_len = dit_len
        self.max_ele = max_ele
        self.thr = thr
        self.res = ""
        self.char = " "
        self.env_char = []
        self.morsestr = ""
        self.his_len = his_len
        self.his = np.zeros(his_len)
        self.pprev = 0
        self.wsep = False
        self.csep = False
        self.scounts = [0 for x in range(3)] # separators
        self.ecounts = [0 for x in range(self.max_ele)] # Morse elements
        self.estarts = [0 for x in range(self.max_ele)] # Identified element start
        self.nb_char_samples = 0
        self.dit_l = 1.375 # 11
        self.dit_h = 2.875 # 23
        self.dah_l = 3.125 # 25
        print("MorseDecoderRegen.__init__:", self.dit_l*dit_len, self.dit_h*dit_len, self.dah_l*dit_len)

    def set_dit_len(self, dit_len):
        self.dit_len = dit_len

    def set_thr(self, thr):
        self.thr = thr

    def reset_hist(self):
        self.his = np.zeros(self.his_len)

    def new_sample(self, sample):
        """ Takes one temporal sample element which is an array of:
            character separator, word separator and element sense at the current time point
            returns a tuple of booleans
                - ret_char: true if a character has been decoded
                - ret_env: true if reconstructed envelope is available
        """
        self.nb_char_samples += 1
        ret_char = False
        ret_env = False
        for i, s in enumerate(sample): # c, w, [pos]
            if s >= self.thr:
                if i < 2:
                    self.scounts[i] += 1
                    if i == 1:
                        self.ecounts[0] = 0
                else:
                    self.estarts[i-2] = self.nb_char_samples
            else:
                if i == 0:
                    self.scounts[0] = 0
                    self.csep = False
                if i == 1:
                    self.scounts[1] = 0
                    self.wsep = False
            if i >= 2:
                self.ecounts[i-2] += s
            if i == 0 and self.scounts[0] > 0.8*self.dit_len and not self.csep: # character separator
                self.his = np.concatenate((self.his[self.max_ele:],self.ecounts))
                self.env_char = [0 for x in range(self.nb_char_samples)] # initialize envelope for character period
                morsestr = ""
                for ip in range(self.max_ele):
                    if self.ecounts[ip] >= self.dit_l*self.dit_len and self.ecounts[ip] < self.dit_h*self.dit_len: # dit
                        start = self.estarts[ip]
                        zl = int(self.ecounts[ip] * 0.5)
                        self.env_char[start:start+zl] = zl*[1]
                        #print(f'dit {start} for {zl}')
                        morsestr += "."
                    elif self.ecounts[ip] >= self.dah_l*self.dit_len: # dah
                        start = self.estarts[ip]
                        zl = int(self.ecounts[ip] * 0.75)
                        sl = int(self.ecounts[ip] * 0.55)
                        self.env_char[start-sl:start-sl+zl] = zl*[1]
                        #print(f'dah {start} for {zl}')
                        morsestr += "-"
                self.char = morse.revmorsecode.get(morsestr, '_')
                self.res += self.char
                ret_char = True
                #print("MorseDecoderRegen.new_sample", self.scounts[0], self.ecounts, morsestr, char, self.nb_char_samples)
                self.csep = True
                ret_env = True
                self.ecounts = self.max_ele*[0]
                self.nb_char_samples = 0
            if i == 1 and self.scounts[1] > 1.2*self.dit_len and not self.wsep: # word separator
                self.char = " "
                self.res += self.char
                ret_char = True
                #print("MorseDecoderRegen.new_sample", "w")
                self.wsep = True
        return ret_char, ret_env
