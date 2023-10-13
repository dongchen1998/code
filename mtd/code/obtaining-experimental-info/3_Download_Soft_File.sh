#!/bin/bash
# 根据Nc的GSE号，批量下载GSE与相关GSM的实验信息原始数据
# 一般下的并不全，但是绝大部分都能下载到

Nc='/home/dongjc/work/mtd/code/Obtaining_experimental_information/Nc'
Nc_file='/home/dongjc/work/mtd/code/Obtaining_experimental_information/Nc/File'
Nc_GSE_soft='/home/dongjc/work/mtd/code/Obtaining_experimental_information/Nc/GSE_soft'
Nc_GSM_soft='/home/dongjc/work/mtd/code/Obtaining_experimental_information/Nc/GSM_soft'

mkdir $Nc
mkdir $Nc_file
mkdir $Nc_GSE_soft
mkdir $Nc_GSM_soft

cat Nc_gse.txt | while read gse; do geofetch -i $gse --processed -n $Nc_file --just-metadata ; done

cd $Nc_file

mv GSE*_GSE.soft $Nc/GSE_soft
mv GSE*_GSM.soft $Nc/GSM_soft