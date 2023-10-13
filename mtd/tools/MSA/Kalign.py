import sys
from subprocess import Popen, PIPE

"""
@use: python3 Kalign.py 1-Get_Seq.fasta 2-Aligned_Seq.fasta
"""

def kalign(input_fasta, output_fasta):
    cmd = f'kalign {input_fasta} > {output_fasta}'
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print(stderr.decode('utf-8'))
    return p.returncode  # return code 0 means no error

# Command line arguments
input_file = sys.argv[1]  # this corresponds to 1-Get_Seq.fasta
output_file = sys.argv[2]  # this corresponds to 2-Aligned_Seq.fasta

kalign(input_file, output_file)