import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import griddata

# 파일 경로를 지정합니다 (여기에는 엑셀 파일의 실제 경로를 입력해야 합니다)
# file_path = 'C:/Users/world/PycharmProjects/Dollar_future/230928_simulation_result_0.001,0.006,0.001_0.001,0.006,0.001_3,6,1_wholeday.xlsx'

file_path = 'C:/Users/world/PycharmProjects/Dollar_future/230929_simulation_result_0.002,0.008,0.001_0.002,0.01,0.001_3,10,1_wholeday.xlsx'

# 엑셀 파일에서 데이터를 불러옵니다
data = pd.read_excel(file_path)

# a와 b에 따라 데이터를 그룹화하고 total_profits의 평균을 계산합니다
grouped_data = data.groupby(['a', 'b']).total_profits.mean().reset_index()

# 데이터를 그리드로 변환합니다
x = grouped_data['a']
y = grouped_data['b']
z = grouped_data['total_profits']
x_grid, y_grid = np.meshgrid(x.unique(), y.unique())

# 그리드에 대해 z 값을 보간합니다
z_grid = griddata((x, y), z, (x_grid, y_grid), method='cubic')

# 2D 컨투어 플롯을 그립니다
fig, ax = plt.subplots(figsize=(10, 7))
contour = ax.contourf(x_grid, y_grid, z_grid, cmap='viridis', levels=20)
plt.colorbar(contour, ax=ax, label='total Profits')

# 레이블과 제목을 설정합니다
ax.set_xlabel('a')
ax.set_ylabel('b')
ax.set_title('2D Contour plot of total Profits by a and b')

# 플롯을 보여줍니다
plt.show()
