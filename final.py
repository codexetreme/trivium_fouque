import numpy as np
from trivium_cube_attack import TriviumCubeAttack
import logging
from math import log2

def make_maxterm(n,limit):
    maxterm = ""
    terms = list(np.random.randint(0,limit,n))
    terms = sorted(terms)
    for i in range(n):
        maxterm = maxterm + ("v" + str(terms[i]))
    return maxterm


def random_secret_generator(degree,bbpoly):
    # randomly generate 80 values

    private_bits = np.random.randint(0, 2, degree)
    current_assignment = {}

    # sets the secret bits to the bbpoly's secret variables
    for index, secret_var in enumerate(bbpoly.secretvariables):
        current_assignment[secret_var] = private_bits[index]

    return current_assignment

    
def mobius(a,n):

    b = []
    for i in range(0,2**(n)):
        b.append(a[i]) 

    for k in range (1, n+1):
        for i in range (0, 2**(n-k)):
            for j in range(0,2**(k-1)):
                b[i*2**(k) + 2**(k-1) + j] = (bool(b[i*2**k + j]) ^ bool(b[i*2**k + 2**(k-1) + j])) % 2
                # print (b[i*2**(k) + 2**(k-1) + j])    
    return b

def get_degree(n):
    count = 0
    while n > 0:
        count = count + 1
        n = n & (n-1)
    return count


def get_density(anf):

    density = {}
    count = 0
    for i , expr in enumerate(anf):
        if expr is 1:
            deg = get_degree(i)
            density[deg] = density.get(deg, 0) + 1
            count += 1
    
    for k,v in density.items():
        v_new = v*100/count
        density[k] = v_new
    return density

def main():
    logging.basicConfig(level=logging.ERROR)
    np.random.seed(0)
    n_rounds = 799
    out_bit = 800
    f = TriviumCubeAttack(n_rounds)
    maxterm = "v2v13v20"
    num_cubes = 3
    current_assignment = random_secret_generator(80,f.bbpoly)
    dicts = []
    for i in range(num_cubes):
        truth_table = f.iterate_cubically(make_maxterm(5,80), current_assignment,out_bit)
        anf = mobius(truth_table,int (log2(len(truth_table))))
        print ("ANF Calculated is : {}".format(anf))
        dicts.append(get_density(anf))


    final_density = {}

    for i in dicts:
        for k,v in i.items():
            final_density[k] = final_density.get(k,0) + v

    for k,v in final_density.items():
        final_density[k] = v/num_cubes

    print ("\n\n\n\n======================================================\n\n\n")    
    print ("Final densities: {}".format(final_density))
    

    

if __name__ == '__main__':
    print (make_maxterm(5,80))
    print (make_maxterm(5,80))
    main()
