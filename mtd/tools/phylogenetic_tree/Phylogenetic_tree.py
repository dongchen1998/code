import os
import re
import sys
import time
import argparse
import pandas as pd

"""
@Usage: python3 Phylogenetic_tree.py -i input/input.fasta -o output/output.tre
"""

def read_config():
    parser = argparse.ArgumentParser(description='This script was used to construct a simple gene tree by FASTA sequencing')
    parser.add_argument('--input', '-i', required=True, help='input sequence file')
    parser.add_argument('--output', '-o', required=False, default='/BTP/output/output.tre', help='tre file')
    arg = parser.parse_args()
    input_fasta_path = arg.input
    fasttree_prot_output = arg.output
    
    return input_fasta_path,fasttree_prot_output


# 比对嗜热毁丝霉蛋白序列
def blast_prot(input_fasta:str, species_db_prot) -> str:
    
    if os.path.exists(input_fasta) == False:
        print("Error: The input fasta file does not exist. Please check again.")
        sys.exit(1)
    
    os.system("blastp -query "+input_fasta+" -db "+species_db_prot+" -outfmt 6 -task blastp -out "+blast_output_path+" -evalue 1e-10")


# 根据标识符，从菌种蛋白序列中提取相关序列，合并到一个新的fasta
def read_prot_sequences(species_prot, ae_list, regular, extract_output_path):

    if os.path.exists(species_prot) == False:
        print("Error: The input file does not exist. Please check again.")
        sys.exit(1)
        
    with open(species_prot, 'r') as f:
        fasta = f.readlines() 
        fasta_dict = {}

        for line in fasta:
            if line.startswith('>'):
                name = line  
                fasta_dict[name] = ''  
                continue
            fasta_dict[name] += line
        
    count = 0
    sequence = []

    for ano,sequences in fasta_dict.items():
        for ae in ae_list:
            ae_name = re.search(regular, ano).group(1)  #  re.search匹配，group获取匹配的内容
            if ae == ae_name:
                sequence.append([ano, sequences])
                count += 1

    with open(extract_output_path, 'w') as r:
        for line in sequence:
            r.writelines(line)
        
    return sequence


# mafft对齐序列
def mafft(extract_output, mafft_output):

    if os.path.exists(extract_output) == False:
        print("Error: The input file does not exist. Please check again.")
        sys.exit(1)

    os.system("mafft --auto "+extract_output+" > "+mafft_output)


# fasttree构建tre文件
def fasttree_prot(mafft_output, fasttree_prot_output_path):

    if os.path.exists(mafft_output) == False:
        print("Error: The input file does not exist. Please check again.")
        sys.exit(1)

    os.system("FastTree "+mafft_output+" > "+fasttree_prot_output_path)



if __name__ == "__main__":

    time1 = time.time()

    input_fasta_path, fasttree_prot_output = read_config()

    # 设置工作目录
    workdir = ('/home/dongjc/BTP/') 

    # 构建的蛋白库
    species_db_prot_path = (workdir + 'db_prot/Myceliophthora_thermophila_ATCC_42464_prot/Myceliophthora_thermophila_ATCC_42464') # 嗜热毁丝霉
    all_species_db_prot_path = (workdir + 'db_prot/total_prot/total') # 所有菌种

    # blast比对完的输出
    blast_output_path = (workdir + 'output/blast_output.tsv') 

    # 比对所有菌种构建的蛋白库
    blast_output = blast_prot(input_fasta_path, all_species_db_prot_path)

    # 菌种蛋白序列地址
    species_prot_path = (workdir + 'prot/Myceliophthora_thermophila_ATCC_42464.faa') 
    all_species_prot_path = (workdir + 'prot/total.faa') 

    # 提取标识符(蛋白ID)
    df_blast_ouput = pd.read_csv(blast_output_path, header=None, sep='\t')
    ae_list = list(df_blast_ouput.iloc[:, 1])

    # 正则定义
    regular = '>(.*?)\s' 

    # 提取同源序列后合并成fasta文件的地址
    extract_output_path = (workdir + 'output/merger.fasta')

    # mafft对齐完输出的文件地址
    mafft_output_path = (workdir + "output/mafft.fasta")

    # 匹配所有的菌种蛋白序列，提取序列并合并
    merger_output = read_prot_sequences(all_species_prot_path, ae_list, regular, extract_output_path)

    # 对齐
    mafft_output = mafft(extract_output_path, mafft_output_path)

    # 构建tre文件
    fasttree_prot_output = fasttree_prot(mafft_output_path, fasttree_prot_output)

    time2 = time.time()
    print(time2 - time1)