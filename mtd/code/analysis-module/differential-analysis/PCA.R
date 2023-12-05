#!/usr/bin/env Rscript
library(DESeq2)
library(ggplot2)
library(plotly)
library(optparse)

# 定义命令行参数
option_list <- list(
  make_option(c("-c", "--input_count"), type = "character", default = NULL, help = "基因表达谱(Count)", metavar = "file"),
  make_option(c("-s", "--input_sample"), type = "character", default = NULL, help = "样本分组信息", metavar = "file"),
  make_option(c("-o", "--output_pic"), type = "character", default = NULL, help = "输出的PCA静态图", metavar = "file")
)

# 解析命令行参数
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

# 检查输入文件是否存在
if (!file.exists(opt$input_count)) {
  stop("输入文件不存在: ", opt$input_count)
}
if (!file.exists(opt$input_sample)) {
  stop("输入文件不存在: ", opt$input_sample)
}

# 读取基因表达谱
count_df <- read.csv(file = opt$input_count, header = TRUE, row.names = 1)
# 读取样本分组信息
sample_df <- read.csv(file = opt$input_sample, header = TRUE, row.names = 1)

# 对样本信息进行预处理
rownames(count_df) <- gsub("-", ".", rownames(count_df))
rownames(sample_df) <- gsub("-", ".", rownames(sample_df))
sample_df$Group <- gsub("-", ".", sample_df$Group)

# 创建dds对象用于差异表达分析
sample_df$Group <- factor(sample_df$Group)
deseq2.obj1 <- DESeqDataSetFromMatrix(
    countData = count_df,
    colData = DataFrame(sample_df),
    design = ~Group
)

# 执行DESeq分析
deseq2.obj2 <- DESeq(deseq2.obj1)

# 准备数据进行PCA分析
dds <- deseq2.obj2
dds <- estimateSizeFactors(dds)
rld <- rlog(dds)

# 绘制PCA图
pcaData <- plotPCA(rld, intgroup="Group", returnData=TRUE)
percentVar <- attr(pcaData, "percentVar")

ggplot(pcaData, aes(x=PC1, y=PC2, color=Group)) +
  geom_point(size=6) +  # 调整点的大小为6，可以根据需要调整
  xlab(paste0("PC1: ",round(percentVar[1]*100),"% variance")) +
  ylab(paste0("PC2: ",round(percentVar[2]*100),"% variance")) +
  coord_fixed() +
  ggtitle("") +
  theme_bw() +  # 使用theme_bw作为基础主题
  theme(
    panel.border = element_rect(colour = "#000000b0", fill=NA, linewidth=0.6)  # 设置边框颜色和线宽
  )

# 保存图片
ggsave(opt$output_pic, width=6, height=4, dpi=300)
