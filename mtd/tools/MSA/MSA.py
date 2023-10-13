# 修改上一个代码块的代码，使得它可以接受命令行参数
# Path: MSA.py
import os
import sys
import subprocess
import argparse

"""
@usage: python3 MSA.py input_file output_file
"""

parser = argparse.ArgumentParser(description='Multiple Sequence Alignment')
parser.add_argument('input_file', help='input file')
parser.add_argument('output_file', help='output file')
args = parser.parse_args()

def kalign(input_file, output_file):
    
      cmd = ["kalign", input_file, "-o", output_file]
      proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
      stdout, stderr = proc.stdout, proc.stderr
      if proc.returncode != 0:
        print("Error running kalign:", stderr)
      else:
        print("kalign completed successfully")

if __name__ == "__main__":
    kalign(args.input_file, args.output_file)