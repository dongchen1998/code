#!/bin/bash

# 检查文件夹Count_File是否存在，如果不存在则创建
if [ ! -d "Count_File" ]; then
  mkdir Count_File
fi

# 遍历move.txt中的每一行
while read line; do
  # 检查文件是否存在
  if [ -f "${line}.txt" ]; then
    # 如果文件存在，则移动到Count_File文件夹中
    mv "${line}.txt" Count_File/
  fi
done < Nc_SRR.txt