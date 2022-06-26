import csv
from pathlib import Path

import ImageProcess as ip

if __name__ == "__main__":



# 上方不要修改！！！
#
# 安装Anaconda运行python 或者自己会python的话保证有python环境 numpy和pillow库即可直接使用
# Anaconda官网 https://docs.anaconda.com/anaconda/install/windows/
# 知乎教程 https://zhuanlan.zhihu.com/p/32925500
# 
# 使用须知
# 1. 只有下方的PATH RED GREEN BLUE SZIE需要修改参数 其余部分请不要更改
# 2. 使用时复制文件夹路径 修改PATH参数 不会复制的自己看百度 https://jingyan.baidu.com/article/2c8c281daad6aa4109252a01.html
# 3. 程序会自动识别文件夹中的png jpg jpeg tif和tiff文件进行处理
# 4. 运行结束后数据自动生成在图片文件夹内的csv文件中 用excel打开
# 5. 建议SIZE的值不要设置过大 建议不超过100 否则可能因为递归过深 内存不足 导致运行失败
# 6. 设置好参数后运行本文件
# 7. 保证ImageProcess.py文件和本文件在同一文件夹 路径最好不要有中文
# 6. 出现bug联系 zhouchen96@iccas.ac.cn
#
# 以下是参数设置部分
    PATH = "/Users/zhouchen/Library" # 在双引号内写上图片文件夹路径
    RED = (0, 255) # 修改红色选色范围
    GREEN = (0, 255) # 修改绿色选色范围
    BLUE = (0, 255) # 修改蓝色选色范围
    SIZE = 20 # 修改面积最小值 即舍去小于这一值的区域
#
# 下方不要修改！！！

    path = Path(PATH)

    data = ip.image_process(path, RED, GREEN, BLUE, int(SIZE))

    count = 0
    data_name = 'data'
    data_path = path / f'{data_name}.csv'
    while data_path.is_file():
        count += 1
        data_path = path / f'{data_name}{count}.csv'

    with open(data_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['name', 'area', 'intensity'])
        for record in data:
            writer.writerow(record)
    
    print(f"分析完成!数据储存于{data_path.name}\n路径: {path}")