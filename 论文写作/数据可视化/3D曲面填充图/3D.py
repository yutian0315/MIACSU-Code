import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import matplotlib.ticker as ticker
from matplotlib.ticker import ScalarFormatter

fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
# plt.rc('font', family='Times New Roman', size=13)

data = pd.read_csv("ADHD-Iter.csv")
x = data['num_client'].values
y = data['server_iter'].values
z = data['ACC'].values
x = np.reshape(x,(6,6))
y = np.reshape(y,(6,6))
z = np.reshape(z,(6,6))
# x = np.arange(-5, 5, 0.25)
# y = np.arange(-5, 5, 0.25)
# x, y = np.meshgrid(x, y)
# # r = np.sqrt(x**2 + y**2)
# # z = np.sin(r)


ax.tick_params(axis='both', which='major', labelsize=17)
# ax.tick_params(axis='both', which='minor', labelsize=10)

ax.set_zlim(70,75)
ax.set_xlabel('num_client', fontdict={'family':'Arial', 'size':20}, weight='bold', labelpad=12)
ax.set_ylabel('server_iter', fontdict={'family':'Arial', 'size':20}, weight='bold', labelpad=12)
ax.set_zlabel('Accuracy (%)', fontdict={'family':'Arial', 'size':20}, weight='bold', labelpad=12)
# ax.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
# ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

# formatter = ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((0,0))
# ax.xaxis.set_major_formatter(formatter)
# ax.yaxis.set_major_formatter(formatter)

# ax.get_xaxis().get_offset_text().set_fontsize(12)  # 设置x轴单位的字体大小
# ax.get_yaxis().get_offset_text().set_fontsize(12)  # 设置y轴单位的字体大小

# 移动科学计数法的偏移位置
# ax.get_xaxis().get_offset_text().set_position((1, 0))
# ax.get_yaxis().get_offset_text().set_position((0, 1))
# # 使用科学计数法格式化刻度标签
# formatter = ticker.ScalarFormatter(useMathText=True)
# formatter.set_scientific(True)
# formatter.set_powerlimits((-4, 4))
#
# ax.xaxis.set_major_formatter(formatter)
# ax.yaxis.set_major_formatter(formatter)
# ax.zaxis.set_major_formatter(formatter)
#
# # 强制更新刻度标签
# ax.xaxis.get_major_formatter().set_scientific(True)
# ax.yaxis.get_major_formatter().set_scientific(True)
# ax.zaxis.get_major_formatter().set_scientific(True)

# # 调整刻度标签的格式和数量
# ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
# ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
# 旋转X轴和Y轴的刻度标签
# for label in ax.get_xticklabels():
#     label.set_rotation(10)
# for label in ax.get_yticklabels():
#     label.set_rotation(-10)

surf = ax.plot_surface(x, y, z, cmap='viridis')
# cbar = fig.colorbar(surf, pad=0.1, shrink=0.8)
# cbar.ax.set_yticklabels([])
# cbar.ax.tick_params(labelsize=13)
# ax.plot_surface(x,y,z)
plt.show()
#
plt.savefig('surface.png', dpi=800)
print("finish")