import numpy as np
import re
import logging
logging.basicConfig(level=logging.INFO)
from blackboxpoly import BlackBoxPoly
from blackboxpoly import sum_mod2


class CubeAttack(object):

    def __init__(self, degree=3, mode="random"):

        self.degree = degree
        self.mode = mode

        self.bbpoly = None

        self.possible_maxterms = None

        self.index_to_take = None

    def iterate_cubically(self, maxterm, private_assignment=None,out_bit=None):

        if out_bit is not None:
            self.index_to_take = out_bit

        if not private_assignment:
            private_assignment = {}

        # print(private_assignment)

        logging.info("iterating cubically " + maxterm + " " + str(private_assignment))

        n_terms = maxterm.count('v')

        answer = 0

        truth_table = []

        for i in range(2 ** n_terms):

            assign_string = format(i, 'b')

            while len(assign_string) != n_terms:
                assign_string = '0' + assign_string
            terms = maxterm.split('v')[1:]
            # print (terms)
            assignment = private_assignment

            for j, term in enumerate(terms):
                assignment['v' + term] = int(assign_string[j])

            # logging.debug(assignment)

            answer = sum_mod2(self.bbpoly.evaluate(assignment, self.index_to_take), answer)
            truth_table.append(answer)

        if out_bit is not None:           
            return truth_table
        else:
            return answer

    def test_maxterm(self, maxterm, index=0):

        self.index_to_take = index

        logging.debug("... testing maxterm ... " + maxterm)

        assign_strings = []

        for i in range(2**self.degree - 5, 2**self.degree):

            assign_string = format(i, 'b')

            while len(assign_string) != self.degree:
                assign_string = '0' + assign_string

            assign_strings.append(assign_string)

        for i in range(2**(self.degree - 2) - 5, 2**(self.degree - 2)):

            assign_string = format(i, 'b')

            while len(assign_string) != self.degree:
                assign_string = '0' + assign_string

            assign_strings.append(assign_string)
            # print ("str : {}".format(assign_strings))
        ################################################################################

        logging.debug(" ... checking if not constant ... " + maxterm)

        not_constant = False

        n_checked = 0

        # print(len(assign_strings))

        for i,assign_string in enumerate(assign_strings):
            # print("constant check ", n_checked)

            n_checked += 1

            current_assignment = {}

            for index, secret_var in enumerate(self.bbpoly.secretvariables):
                current_assignment[secret_var] = int(assign_string[index])
                # print (int(assign_string[index]))
            if i==0:
                first_answer = self.iterate_cubically(maxterm, current_assignment)
                print(maxterm)
                continue

            else:
                answer = self.iterate_cubically(maxterm, current_assignment)
                if answer != first_answer:
                    not_constant = True
                    break

            logging.debug(str(answer))

            if n_checked >= 80:
                break

        if not not_constant:
            logging.debug('False ' + maxterm)
            return False

        #################################################################################

        logging.debug(" ... checking if linear ... " + maxterm)

        linear = True

        n_checked = 0

        for assign1 in assign_strings:
            for assign2 in assign_strings:
                # print("linear check ", n_checked)
                logging.debug('assign1: ' + assign1)
                logging.debug('assign2: ' + assign2)

                current_assignment = {}

                for index, secret_var in enumerate(self.bbpoly.secretvariables):
                    current_assignment[secret_var] = 0

                ans_1 = self.iterate_cubically(maxterm, current_assignment)

                current_assignment = {}

                for index, secret_var in enumerate(self.bbpoly.secretvariables):
                    current_assignment[secret_var] = int(assign1[index])

                ans_2 = self.iterate_cubically(maxterm, current_assignment)

                current_assignment = {}

                for index, secret_var in enumerate(self.bbpoly.secretvariables):
                    current_assignment[secret_var] = int(assign2[index])

                ans_3 = self.iterate_cubically(maxterm, current_assignment)

                lhs = sum_mod2(sum_mod2(ans_1, ans_2), ans_3)
                logging.debug('lhs: ' +  str(lhs))

                rhs_argument = format(int(assign1, 2) ^ int(assign2, 2), 'b')

                while len(rhs_argument) != self.degree:
                    rhs_argument = '0' + rhs_argument

                logging.debug('rhs argument: ' + str(rhs_argument))

                current_assignment = {}

                for index, secret_var in enumerate(self.bbpoly.secretvariables):
                    current_assignment[secret_var] = int(rhs_argument[index])

                rhs = self.iterate_cubically(maxterm, current_assignment)

                if lhs != rhs:
                    linear = False
                    break

                n_checked += 1

                if n_checked >= 80:
                    break

            if not linear:
                break

        if not linear:
            logging.debug('False ' + maxterm)
            return False

        #################################################################################

        logging.debug('True ' + maxterm)
        return True

    def find_superpoly(self, maxterm):

        secret_vars = self.bbpoly.secretvariables

        superpoly = {}

        current_assignment = {var:0 for var in secret_vars}

        constant_value = self.iterate_cubically(maxterm, current_assignment)

        superpoly["constant"] = constant_value

        for sv in secret_vars:

            current_assignment[sv] = 1

            value = self.iterate_cubically(maxterm, current_assignment)

            superpoly[sv] = constant_value ^ value

            current_assignment[sv] = 0

        logging.info("superpoly for {} is {}".\
                     format(maxterm, " ".join([k for k in superpoly.keys() if superpoly[k] == 1])))

        return superpoly

    def execute_offline_attack(self):
        logging.debug(self.possible_maxterms)

        valid_maxterms = []

        for maxterm in self.possible_maxterms:

            if self.test_maxterm(maxterm):
                valid_maxterms.append(maxterm)

        logging.info("VALID MAXTERMS :" + str(valid_maxterms))

        superpolys = {}

        for maxterm in valid_maxterms:

            superpolys[maxterm] = self.find_superpoly(maxterm)

        return superpolys

    def execute_online_attack(self, superpolys):

        equations = {}

        for maxterm in superpolys.keys():

            value = self.iterate_cubically(maxterm)

            equations[maxterm] = (superpolys[maxterm], value)

            logging.info("equation for maxterm {} is {} = {}".format\
                     (maxterm, " ".join([k for k in superpolys[maxterm].keys() if superpolys[maxterm][k] == 1]),
                      value))

class RandomCubeAttack(CubeAttack):

    def __init__(self, degree):
        super().__init__(degree)

        self.degree = degree

        self.bbpoly = BlackBoxPoly(degree=self.degree)

        possible_maxterms = self.bbpoly.maxterms[:-1]

        self.possible_maxterms = []

        for term in possible_maxterms:
            if 'x' not in term:
                self.possible_maxterms.append(term)