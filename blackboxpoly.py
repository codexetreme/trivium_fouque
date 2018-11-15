"""
b = blackboxpoly()
publicvariables = b.publicvariables
secretvariables = b.secretvariables (list)

b.evaluate(assignment)
b.evalonline(assignment)
"""
import numpy as np
import re
import logging

# # seed = 371
# seed = np.random.randint(0, 1000)
# logging.info("Seed is {}".format(seed))

# np.random.seed(seed)

#np.random.seed(1234)

def sum_mod2(a,b):
    return (a+b) % 2


class BlackBoxPoly:
    def __init__(self, degree=3):

        self.degree = degree

        self.publicvariables = []
        self.secretvariables = []

        for i in range(1,degree+1):
            self.secretvariables.append("x" + str(i))
            self.publicvariables.append("v" + str(i))

        self.maxterms = []

        copy_vars = self.publicvariables + self.secretvariables

        for i in range(len(copy_vars)):

            current_vars = copy_vars[i+1:]
            current_var = copy_vars[i]

            def gen_maxterms(var, vars):
                if len(vars) == 0:
                    self.maxterms.append(var)
                    return

                gen_maxterms(var + vars[0],
                             vars[1:])

                gen_maxterms(var,
                             vars[1:])

                return

            gen_maxterms(current_var, current_vars)

        self.maxterms.append('constant')

        random_array = np.random.choice(2, [2**(self.degree*2)], p=[0.8, 0.2])

        k=0

        self.coefficients = {}


        random_array = np.random.randint(0, 2, [2**(self.degree*2)])
        
        k=0
        
        self.coefficients = {}

        for maxterm in self.maxterms:
            self.coefficients[maxterm] = random_array[k]
            k += 1

        self.private_key = np.random.randint(0, 2, degree)

        debug_string = ""

        for key_max in self.coefficients.keys():

            if self.coefficients[key_max] == 1:
                debug_string += " " + key_max

        logging.info("The eqn is " + debug_string)
        logging.info("The private key is " + str(self.private_key))

    def evaluate(self, assignment, index=None):

        # public_assignment = {}
        # private_assignment = {}
        #
        # for i in range(self.degree):
        #     public_assignment[self.publicvariables[i]] = assignment[i]
        #     private_assignment[self.secretvariables[i]]= self.private_key[i]
        #
        # ans = 0
        #
        # for maxterm in self.coefficients.keys():
        #
        #     if self.coefficients[maxterm] == 0:
        #         continue
        #
        #     if maxterm == 'constant':
        #         ans = sum_mod2(ans, 1)
        #         continue
        #
        #     temp_ans = 1
        #
        #     for pbv in public_assignment.keys():
        #         if pbv in maxterm:
        #             temp_ans *= public_assignment[pbv]
        #
        #     for prv in private_assignment.keys():
        #         if prv in maxterm:
        #             temp_ans *= private_assignment[prv]
        #
        #     ans = sum_mod2(ans, temp_ans)
        # return ans

        return self.evalonline(assignment)

    def evalonline(self, assignment_dict):
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

        ans = 0

        for maxterm in self.coefficients.keys():

            if self.coefficients[maxterm] == 0:
                continue

            if maxterm == 'constant':
                ans = sum_mod2(ans, 1)
                continue

            temp_ans = 1

            for pbv in public_assignment.keys():
                # logging.debug(maxterm + ' iiii ' + pbv)

                if re.match('([xv0-9]*' + pbv + '$)|([xv0-9]*' + pbv + '[xv])', maxterm):
                    # logging.debug(pbv + " oooo " + maxterm)
                    temp_ans *= public_assignment[pbv]

            for prv in private_assignment.keys():
                if re.match('([xv0-9]*' + prv + '$)|([xv0-9]*' + prv + '[xv])', maxterm):
                    temp_ans *= private_assignment[prv]

            if pbv in maxterm:
                temp_ans *= public_assignment[pbv]

            for prv in private_assignment.keys():
                if prv in maxterm:
                    temp_ans *= private_assignment[prv]

            ans = sum_mod2(ans, temp_ans)

        return ans


def blackboxpoly(degree=3):
    b = BlackBoxPoly(degree)
    return b



