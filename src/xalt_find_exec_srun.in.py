# -*- python -*-
#
# Git Version: @git@

#-----------------------------------------------------------------------
# XALT: A tool to track the programs on a cluster.
# Copyright (C) 2013-2014 Robert McLay and Mark Fahey
# 
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of 
# the License, or (at your option) any later version. 
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser  General Public License for more details. 
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place, Suite 330,
# Boston, MA 02111-1307 USA
#-----------------------------------------------------------------------
from __future__             import print_function
import os, sys

dirNm, execName = os.path.split(os.path.realpath(sys.argv[0]))
sys.path.insert(1,os.path.abspath(os.path.join(dirNm, "../libexec")))

from xalt_parse_mpirun_args import find_exec

ignoreT = {
}

# srun args that take one option in the form "-arg option"
argT = {
  '-A'                        : 1,
  '-c'                        : 1,
  '-d'                        : 1,
  '-D'                        : 1,
  '-e'                        : 1,
  '-i'                        : 1,
  '-J'                        : 1,
  '-L'                        : 1,
  '-m'                        : 1,
  '-n'                        : 1,
  '-N'                        : 1,
  '-o'                        : 1,
  '-p'                        : 1,
  '-r'                        : 1,
  '-T'                        : 1,
  '-t'                        : 1,
  '-W'                        : 1,
  '-C'                        : 1,
  '-w'                        : 1,
  '-x'                        : 1,
  '-B'                        : 1,
}


def main():

  print(find_exec(ignoreT, argT, "-c", sys.argv[1:]))

if ( __name__ == '__main__'): main()