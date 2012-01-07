#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# icl7665.py - This program is part of circuit-calc. It matches the resistor
#              values of standard resistor series against a given voltage ratio
#              for the ICL7665 ic.
# 
# Copyright (C) 2012  Andreas Messer <andi@bastelmap.de>
# 
# circuit-calc is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from math import log10, fmod,fabs, ceil
from tools.resistors import ResistorSeries

v_ref = 1.3

def calc_resistor_ratio(v1,v2):
    b = v1 / v_ref - 1
    c = v2 / v_ref - 1 - b

    return (1,b,c)

def calc_voltages(a,b,c):
    v1 = v_ref * (1 + (c + b) / a)
    v2 = v_ref * (1 + b / a)

    return (v1,v2)


def optimize_resistor_sum_fixedij(series,a,b,c,i,j):
    
    best_factor = (b+c)/a
    
    delta_min = (-best_factor, None)
    delta_max = (+best_factor, None)
    
    while i < len(series) and j < len(series):
        for k in range(len(series)):
            factor = (series[j] + series[k]) / series[i]
            
            delta = factor - best_factor
            
            if delta >= 0 and delta < delta_max[0]:
                delta_max = (delta,(i,j,k))

            if delta <= 0 and delta > delta_min[0]:
                delta_min = (delta,(i,j,k))
                
            if factor > best_factor:
                break;
            
        i += len(series.factors)
        j += len(series.factors)
        
    return tuple(filter(lambda x: x,( delta_min[1], delta_max[1])))

def optimize_resistors(series,a,b,c):

    log10factors = tuple(map(log10,series.factors))

    l = len(log10factors)
    m = len(series)

    def calc_diff(i,j):
        return ((int(i),int(j)),log10factors[int(fmod(j,l))] - log10factors[int(fmod(i,l))] + ceil((j - l + 1)/ l) - ceil((i -l + 1) / l))

    log10differences = list(calc_diff(x / l, x % l) for x in range(l*l))
    
    # first selection - optimize according the lower voltage
    logfactor = log10(b/a)
    
    delta_min =  (- fabs(logfactor),None, None)
    delta_max =  ( fabs(logfactor), None, None)

    # second selection - optimize according the lower voltage
    logfactor_higher = log10((b+c)/a)

    keys_higher = dict()
     
    for key,value in log10differences:
        remaining = logfactor - value
        decades   = round(remaining)
          
        delta = remaining - decades
          
        if delta >= 0 and delta < delta_max[0]:
            delta_max = (delta,decades,key)
        
        if delta <= 0 and delta > delta_min[0]:
            delta_min = (delta,decades,key)

        i,k = key
        
        remaining_higher = logfactor_higher - value
        decades_higher   = round(remaining_higher)
          
        if decades_higher + value <= logfactor_higher:
            if decades_higher >= 0:
                k = k + decades_higher * l
            else:
                i = i + decades_higher * l
                              
            keys_higher[i] = min(max(k+1, keys_higher.get(i,0)),m)
        
    results = set()
         
    
    for delta,decades,key in delta_min,delta_max:
        i,j = key
        
        if i == j:
            i = j = 0
            
        if decades > 0:
            j = j + decades * l
        if decades < 0:
            i = i + decades * l
            
        for i,j,k in optimize_resistor_sum_fixedij(series, a, b, c, i,j):
            while max(i,j,k) + l < m:
                i += l
                j += l
                k += l
            
            results.add((i,j,k))

    best_ratio_sum = (b+c) / a
    best_ratio     = b / a
    
    optimized = dict()
            
    def calc_weighted_deviation(a,b):
        a *= 10
        return a*a + b*b
                
    for i,k in keys_higher.items():
        
        # at first scale up to maximum i/k
        while max(i,k) + l < m:                
            i = i + l
            k = k + l
                    
        j = 0
        while k >= 0:
            ratio_sum = (series[j] + series[k]) / series[i]
            ratio     = series[j] / series[i]
            
            dev_sum = ratio_sum/best_ratio_sum - 1
            dev     = ratio/best_ratio - 1

            key = (dev_sum < 0, dev < 0)
            
            weight = calc_weighted_deviation(dev_sum, dev)
                         
            if not optimized.get(key,None) or optimized[key][0] > weight:
                optimized[key] = (weight,i,j,k) 
            
            if ratio_sum > best_ratio_sum:
                k = k -1
            else:
                j = j + 1
            
    
    for weight,i,j,k in optimized.values():
        results.add((i,j,k))
        
    return list( (series[i], series[j], series[k]) for i,j,k in results)

import argparse

parser = argparse.ArgumentParser(description="Calculate best matching resistor values for ICL7665")

parser.add_argument('voltages', metavar='V', type=float, nargs=2, 
                    help='The switching voltages of the ICL7665')

parser.add_argument('-s', '--series', dest='series', action='append',
                    choices = tuple(map(lambda x : "E%d" % x, ResistorSeries.series())),
                    help='The Resistor Series to use for matching')

args=parser.parse_args()

v_high = max(args.voltages)
v_low  = min(args.voltages)

if not args.series:
    args.series = ['E24']
    
for s in args.series:
    e = int(s[1:])
    
    ratios = calc_resistor_ratio(v_low,v_high)

    print("E%d:" % e)

    for resistors in sorted(optimize_resistors(ResistorSeries(e),*ratios),key=lambda x : calc_voltages(*x)[0]):
        voltages  = calc_voltages(*resistors)
    
        print ("  Resistors: %.2f %.2f %.2f" % resistors + " Voltages: %f %f" % voltages)

    