#!/usr/bin/ python
# -*- coding: utf-8 -*-

import argparse

import subprocess

from concurrent.futures import ProcessPoolExecutor


def gatk4(chrom):
    subprocess.run(['gatk','--java-options','-Xmx15G','HaplotypeCaller','-I',args.input,'-O',args.output + '.' + chrom + '.g.vcf.gz','-R',args.ref,'--emit-ref-confidence','GVCF','-OVI','False', '-L',chrom],shell=False)


parser = argparse.ArgumentParser(description='输入参数如下:')
parser.add_argument('--process', '-P', type=int, help='进程数量，必要参数', required=True)
parser.add_argument('--input', '-I', help='bam file，必要参数', required=True)
parser.add_argument('--ref', '-R', help='reference genome，必要参数', required=True)
parser.add_argument('--output', '-O', help='sample name，必要参数', required=True)
args = parser.parse_args()


if __name__ == '__main__':
    commom_wheat_chrom = ['chr7A']

    chrom_gvcf = []
    for chrom in commom_wheat_chrom:
        chrom_gvcf.append( args.output + '.' + chrom + '.g.vcf.gz')

    try:
        with ProcessPoolExecutor(max_workers=args.process) as pool:
            future1 = pool.map(gatk4,commom_wheat_chrom)
            print(list(future1))
    except Exception as e: 
        print(e)
    
    #subprocess.run('gatk GatherVcfs -RI TRUE -I ' + ' -I '.join(chrom_gvcf) + ' -O ' + args.output + '.g.vcf.gz',shell=True)
    #subprocess.run('rm -fr ' + ' '.join(chrom_gvcf),shell=True)
