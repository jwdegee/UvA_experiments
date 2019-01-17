#!/usr/bin/env python
# encoding: utf-8
"""
exp.py

Created by Tomas Knapen on 2011-02-16.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""
import os, sys, datetime, readline
import numpy as np
import scipy as sp
import scipy.stats as stats
import pandas as pd
import glob

from IPython import embed as shell

def analyse_yesno(filename):
    
    # read data:
    df = pd.read_csv(filename, sep='\t')
    df = df.iloc[0::2,:]

    df['hit'] = ((df['present']==1) & (df['answer']==1)).astype(int)
    df['fa'] = ((df['present']==0) & (df['answer']==1)).astype(int)
    df['miss'] = ((df['present']==1) & (df['answer']==0)).astype(int)
    df['cr'] = ((df['present']==0) & (df['answer']==0)).astype(int)
    df['correct'] = df['hit'] + df['cr']

    print
    print("number trials: %i." % len(df))
    print
    print("mean rt: %f." % df['answer_time'].mean())
    print("# too slow: %i." % sum(df['answer']==-1))
    print
    print("correct: %f." % df['correct'].mean())
    print("# fa: %i." % df['fa'].sum())
    print("# miss: %i." % df['miss'].sum())
    # print("d-prime: %f" % d_prime
    # print("criterion: %f." % criterion
    print

if __name__ == '__main__':
    initials = raw_input('Your initials: ')
    index_number = int(raw_input('Which run: '))
    version = int(raw_input('Version: ') )

	# analyse_yesno(subject=initials, index=index_number, version=version)



