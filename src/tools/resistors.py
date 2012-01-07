#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# circuit-calc - A collection of python scripts to ease calculation of
#                electronic circuit values
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

class ResistorSeries():

    series_factors = [
        (1.0, 2.2, 4.7),
        (1.0, 1.5, 2.2, 3.3, 4.7, 6.8),
        (1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2),
        (1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1),
        tuple(map(lambda x: round( 10**(x / 48),2),range(48))),
        tuple(map(lambda x: round( 10**(x / 96),2),range(96))),
        tuple(map(lambda x: round( 10**(x / 192),2),range(192))),
    ]

    @classmethod
    def series(cls):
        return tuple(map(len,cls.series_factors))

    @classmethod
    def elements(cls,series):
        return tuple(cls.series_factors[cls.series().index(series)])

    mults = tuple(map(lambda x : 10 ** x, range(7)))

    def __init__(self,series):
        self.factors = self.elements(series)

    def __len__(self):
        return len(self.mults) * len(self.factors)

    def __getitem__(self,index):
        return round(self.mults[int(index / len(self.factors))] * self.factors[int(index % len(self.factors))],3)





