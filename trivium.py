from collections import deque
from itertools import repeat
from sys import version_info
import logging
import numpy as np

"""
degree

self.publicvariables = []
self.secretvariables = []
self.maxterms = []
self.coefficients = {}
def evaluate(self, assignment_dict):
"""


class Trivium:
    def __init__(self, n_rounds, key=None):

        self.degree = 80
        self.publicvariables = ['v' + str(i) for i in range(1, 81)]
        self.secretvariables = ['x' + str(i) for i in range(1, 81)]

        self.n_rounds = n_rounds

        if not key:
            self.private_key = np.random.randint(0, 2, self.degree)

        else:
            self.private_key = key

        sk_list = [str(x) for x in self.private_key.tolist()]

        self.sk_list = sk_list

        logging.info("private key is %s", "".join(sk_list))

        sk_hex = "{:020X}".format(int("".join(sk_list), 2))

        logging.info("private key (hex) is %s", sk_hex)

    def _init_trivium(self, iv):

        init_list = list(map(int, list(self.sk_list)))
        init_list += list(repeat(0, 13))

        # len 84
        init_list += list(map(int, list(iv)))
        init_list += list(repeat(0, 4))

        # len 111
        init_list += list(repeat(0, 108))
        init_list += list([1, 1, 1])
        self.state = init_list

        for i in range(self.n_rounds):
            self._gen_keystream()

    def evaluate(self, assignment_dict, out_bit):

        public_assignment = {}
        private_assignment = {}

        for i in range(self.degree):
            public_assignment[self.publicvariables[i]] = 0
            private_assignment[self.secretvariables[i]] = self.private_key[i]

        for as_var in assignment_dict.keys():

            if 'v' in as_var:
                public_assignment[as_var] = assignment_dict[as_var]

            elif 'x' in as_var:
                private_assignment[as_var] = assignment_dict[as_var]

        pub_binary = "".join([str(public_assignment['v'+str(z)]) for z in range(1, 81)])
        pri_binary = "".join([str(private_assignment['x'+str(z)]) for z in range(1, 81)])

        self._init_trivium(pub_binary)

        for i in range(out_bit - self.n_rounds):
            self._gen_keystream()

        if out_bit < self.n_rounds:
            raise Exception("output bit index {} must be >= number of rounds {}".format(out_bit,
                                                                                        self.n_rounds))

        return self._gen_keystream()

    def _gen_keystream(self):

        t_1 = self.state[65] ^ self.state[92]
        t_2 = self.state[161] ^ self.state[176]
        t_3 = self.state[242] ^ self.state[287]

        out = t_1 ^ t_2 ^ t_3

        t_1 = t_1 ^ self.state[90] & self.state[91] ^ self.state[170]
        t_2 = t_2 ^ self.state[174] & self.state[175] ^ self.state[263]
        t_3 = t_3 ^ self.state[285] & self.state[286] ^ self.state[68]

        self.state[0:93] = [t_3] + self.state[0:92]
        self.state[93:177] = [t_1] + self.state[93:176]
        self.state[177:288] = [t_2] + self.state[177:287]

        return out

def hex_to_bits(n):
    return list("{:080b}".format(int(n, 16)))

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)

    f = {'v' + str(k): 0 if v < 20 else 1 for (v, k) in enumerate(range(1, 81), 0)}

    pu = "".join([str(f['v'+str(z)]) for z in range(1, 81)])

    print("{:020X}".format(int(pu, 2)))

    tv = Trivium(4*288)

    for i in range(20):
        print(tv.evaluate(f, i+4*288))

#
# if __name__ == "__main__":
#     main()