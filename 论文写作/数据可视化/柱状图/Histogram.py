import matplotlib.pyplot as plt
import numpy as np


bar_width = 0.12
# index = np.arange(2)
plt.rc('font', size=18, weight='bold')
# 定义两组指标数据

# data2 = [72.91, 75.68, 83.99, 60.04, 76.88]
# #ABIDE-TAM
# GSF-ATTN
# data1 = [68.72, 71.91, 75.10, 61.62, 71.99]
# #GSF-TAM-concat(w/o)
# data2 = [71.05, 75.16, 74.86, 66.54, 73.30]
# # GSF-TAM-Mul(w/o)
# data3 = [72.21, 75.41, 79.20, 64.03, 75.26]
# #ABIDE-SL
# data4 = [70.47, 73.68, 77.19, 62.81, 73.64]
# # GSF
# data5 = [72.91, 75.68, 83.99, 60.04, 76.88]

data1 = [68.72]
#GSF-TAM-concat(w/o)
data2 = [71.05]
# GSF-TAM-Mul(w/o)
data3 = [72.21]
#ABIDE-SL
data4 = [70.47]
# GSF
data5 = [72.91]

# ADHD-TAM
# data1 = [68.55,	68.51,	42.32,	83.35,	47.98]
# # GSF-TAM-concat(w/o)
# data2 = [69.21, 68.57, 42.24, 84.94, 44.56]
# # GSF-TAM-Mul(w/o)
# data3 = [71.71, 72.05, 55.93, 81.03, 58.89]
# data4 = [69.47,	72.02,	60.09,	75.01,	57.59]
# # ADHD-GSF
# data5 = [72.50, 72.15,   60.80,   79.31, 61.45]

#
data1 = [68.55]
# GSF-TAM-concat(w/o)
data2 = [69.21]
# GSF-TAM-Mul(w/o)
data3 = [71.71]
# ADHD-SL
data4 = [69.47]
# ADHD-GSF
data5 = [72.50]

# 创建图形和子图
fig, ax = plt.subplots()


# D4F4F1
# A9E9E4
# 7DDFD7
# 249087
# 18605A

# '#DAE3F5'
# '#B6C7EA'
# '#91ACE0'
# '#2E54A1'
# 1E386B

# 绘制第一组柱状图
# rects1 = ax.bar(index, data1, bar_width, color='#D4F4F1', label='FS\u00b2G w/o TAM')
# # 绘制第二组柱状图
# rects2 = ax.bar(index + bar_width+0.03, data2, bar_width, color='#A9E9E4', label='FS\u00b2G-TAM w/o concat')
# # 绘制第二组柱状图
# rects3 = ax.bar(index + (bar_width+0.03)*2, data3, bar_width, color='#7DDFD7', label='FS\u00b2G-TAM w/o mul')
# rects4 = ax.bar(index + (bar_width+0.03)*3, data4, bar_width, color='#249087', label='FS\u00b2G w/o SL')
# rects5 = ax.bar(index + (bar_width+0.03)*4, data5, bar_width, color='#18605A', label='FS\u00b2G')

rects1 = ax.bar((bar_width+0.02)*1, data1, bar_width, color='#DAE3F5', label='DSG w/o TAM')
# 绘制第二组柱状图
rects2 = ax.bar((bar_width+0.02)*2, data2, bar_width, color='#B6C7EA', label='DSG-TAM w/o Concat')
# 绘制第二组柱状图
rects3 = ax.bar((bar_width+0.02)*3, data3, bar_width, color='#91ACE0', label='DSG-TAM w/o Mul')
rects4 = ax.bar((bar_width+0.02)*4, data4, bar_width, color='#2E54A1', label='DSG w/o SL')
rects5 = ax.bar((bar_width+0.02)*5, data5, bar_width, color='#1E386B', label='DSG')

# 设置图形元素样式
# ax.set_xlabel('Categories')
ax.set_ylabel('ACC(%)', fontweight='bold', fontsize=20)
# ax.set_title('Ablation analysis on ABIDE', fontweight='bold', fontsize=20)
# ax.set_xticks(index + bar_width/2)
# ax.set_xticklabels(('ACC', 'AUC'), fontweight='bold', fontsize=20)
ax.set_xticklabels('', fontweight='bold', fontsize=20)
# ax.set_xticklabels(('ACC', 'AUC', 'SPE', 'SEN', 'F1'))

# ax.grid(color='grey', linestyle='--', linewidth=1, alpha=0.2)
ax.set_ylim(50, 100)
ax.legend()

# 在柱状图上设置数据标签
ax.bar_label(rects1, padding=4, label_type='center', rotation='vertical', fontweight='bold', fontsize=20)
ax.bar_label(rects2, padding=4, label_type='center', rotation='vertical', fontweight='bold', fontsize=20)
ax.bar_label(rects3, padding=4, label_type='center', rotation='vertical',fontweight='bold', fontsize=20)
ax.bar_label(rects4, padding=4, label_type='center', rotation='vertical', fontweight='bold', fontsize=20)
ax.bar_label(rects5, padding=4, label_type='center', rotation='vertical', fontweight='bold', fontsize=20)

plt.tight_layout()
plt.show()