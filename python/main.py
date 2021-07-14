#! /usr/bin/python3

from read import *
from random import randint
#from rcdtype import *
import types

EPSILON = 0.000000001

SWAP        = 0
TWO_OPT     = 1
REINSERTION = 2
OR_OPT_2    = 3
OR_OPT_3    = 4

n, m = get_instance_info()

#subseq_info = types.SimpleNamespace('T C W')

def subseq_info_fill(n):
    matrix = []

    for i in range(n+1):
        matrix.append([])
        for j in range(n+1):
            matrix[i].append(types.SimpleNamespace())
            matrix[i][j].T = 0
            matrix[i][j].C = 0
            matrix[i][j].W = 0
            #matrix[i].append(subseq_info(0, 0, 0))

        print(matrix[i])



    return matrix

def construction(alpha):
    s = [0]
    c_list = []
    for i in range(1, n):
        c_list.append(i)

    r = 0

    while len(c_list) > 0:
        c_list = sorted(c_list, key = lambda i : m[i][r], reverse=False)
        print(c_list)

        '''
        for i in range(len(c_list)):
            print(m[c_list[i]][r])
        '''

        i = int(len(c_list)*alpha)
        if i == 0:
            Rc_list = [c_list[i]]
        else:
            Rc_list = c_list[:i]

        print(Rc_list)

        c = Rc_list[randint(0, len(Rc_list)-1)]
        s.append(c)
        r = c
        c_list.remove(r)

    s.append(0)

    print(s)

    return s

def subseq_info_load(s, seq):
    i = 0
    d = n + 1
    while i < d:
        k = 1 - i - int(not i)

        seq[i][i].T = 0
        seq[i][i].C = 0
        seq[i][i].W = int(not (i == 0))

        j = i + 1
        while j < d:
            a = j - 1

            seq[i][j].T = m[s[a]][s[j]] + seq[i][a].T
            seq[i][j].C = seq[i][j].T + seq[i][a].C
            seq[i][j].W = j + k

            seq[j][i].T = seq[i][j].T
            seq[j][i].C = seq[i][j].C
            seq[j][i].W = seq[i][j].W

            j += 1

        #exit(1)

        i += 1

def swap(s, i, j):
    s[i], s[j] = s[j], s[i]

    print(s)

def reverse(s, i, j):
    s[i:j+1] = s[i:j+1][::-1]
    print(s)

def reinsertion(s, i, j, pos):
    if i < pos:
        s[pos:pos] = s[i:j+1]
        s = s[:i] + s[j+1:]
    else:
        sub = s[i:j+1]
        s = s[:i] + s[j+1:]
        s[pos:pos] = sub

    print(s)

def search_swap(s, subseq):
    print(s)
    swap(s, 7, 4)
    return None

def search_two_opt(s, subseq):
    print(s)
    reverse(s, 2, 5)
    return None

def search_reinsertion(s, subseq, opt):
    print(s)
    reinsertion(s, 4, 5, 2)
    return None

def RVND(s, subseq):

    #neighbd_list = [SWAP]
    #neighbd_list = [TWO_OPT]
    neighbd_list = [REINSERTION]
    #neighbd_list = [SWAP, TWO_OPT, REINSERTION, OR_OPT_2, OR_OPT_3]

    while len(neighbd_list) > 0:
        i = randint(0, len(neighbd_list)-1)
        neighbd = neighbd_list[i]

        if neighbd == SWAP:
            search_swap(s, subseq)
        elif neighbd == TWO_OPT:
            search_two_opt(s, subseq)
        elif neighbd == REINSERTION:
            search_reinsertion(s, subseq, REINSERTION)
        elif neighbd == OR_OPT_2:
            search_reinsertion(s, subseq, OR_OPT_2)
        elif neighbd == OR_OPT_3:
            search_reinsertion(s, subseq, OR_OPT_3)

        exit(1)
        

    return None

def perturb(s):
    return None

def GILS_RVND(Imax, Iils, R):

    cost_best = float('inf')
    s_best = []

    subseq = subseq_info_fill(n)

    for i in range(Imax):
        alpha = R[randint(0, len(R)-1)]

        s = construction(alpha)
        #s = [0, 7, 8, 10, 12, 6, 11, 5, 4, 3, 2, 13, 1, 9, 0]
        # s_cost igual a 20315 p burma14
        print('aqui')
        subseq_info_load(s, subseq)
        print(subseq[0][n].C)
        #exit(1)
        sl = s
        rvnd_cost_best = subseq[0][n].C - EPSILON

        iterILS = 0
        while iterILS < Iils:
            s = RVND(s, subseq)
            rvnd_cost_crnt  = subseq[0][n].C - EPSILON
            if rvnd_cost_crnt < rvnd_cost_best:
                rvnd_cost_best = rvnd_cost_crnt
                sl = s
                iterILS = 0

            s = perturb(sl)
            subseq_info_load(s, subseq)
            iterILS += 1

        subseq_info_load(sl, subseq)
        sl_cost = subseq[0][n].C - EPSILON

        if sl_cost < cost_best:
            s_best = sl
            cost_best = sl_cost




def main():
    
    R = [0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.20, 0.21, 0.22, 0.23, 0.24, 0.25]
    
    Imax = 10
    Iils = min(n, 100)

    GILS_RVND(Imax, Iils, R)


main()
