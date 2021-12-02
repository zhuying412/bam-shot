# BAM shot

该包用于对BAM文件画图，依赖samtools, python3.X, pyssam版本： 主要参数:

- bam: BAM文件
- ref: 参考基因组FASTA，需要提前使用samtools faidx构建索引
- chrom: 染色体
- start: 起始位置
- end：终止位置
- extend：两端拓展长度
- ……