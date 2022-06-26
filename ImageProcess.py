import os, re
import numpy as np
from pathlib import Path
from PIL import Image

def _read_image(path: Path, name: str, error_flag: list) -> np.ndarray:
    """传入路径和名称 读取图像RGB数值 返回三维numpy数组 对应R G B"""

    # 读取图像 将不是RGB格式的转为RGB格式
    try:
        with Image.open(path / name) as im:
            row, column = im.size
            rgb = np.empty((row, column, 3))

            if im.mode != 'RGB':
                error_flag[0] = 'Not RGB Mode'
            else:
                # 读取图像的RGB数值
                for x in range(row):
                    for y in range(column):
                        rgb[x, y, 0], rgb[x, y, 1], rgb[x, y, 2] = im.getpixel((x, y))
        return rgb
    except OSError:
        error_flag[0] = 'Open Failed'
        return None

def _read_image_names(path: Path) -> list:
    """传入路径 读取路径下的所有图像文件 返回文件名构成的列表"""

    # 读取路径下所有文件名称
    image_names = os.listdir(path)

    # 去除不是图像文件的文件名
    image_name_regex = re.compile(r'.(png|jpg|jpeg|tif|tiff)$')
    for name in image_names[:]:
        if not image_name_regex.search(name.lower()):
            image_names.remove(name)

    return image_names

def _color_selection(color: np.ndarray, color_range: tuple) -> np.ndarray:
    """传入一种颜色和选色范围 返回单色选色布尔矩阵"""

    selection_array = np.logical_and(color >= color_range[0], color <= color_range[1])
    
    return selection_array

def _colors_selection(rgb: np.ndarray, RED: tuple, GREEN: tuple, BLUE: tuple) -> np.ndarray:
    """传入图像RGB数组和R G B选色范围 返回RGB选色布尔矩阵"""

    red = rgb[:, :, 0]
    green = rgb[:, :, 1]
    blue = rgb[:, :, 2]

    selection_array = np.logical_and(_color_selection(red, RED), _color_selection(green, GREEN))
    selection_array = np.logical_and(_color_selection(blue, BLUE), selection_array)

    return selection_array

def _connected_analysis(selection_array: np.ndarray, record_array: np.ndarray, records: list, x: int, y: int, limit_area: int, current_area: int) -> int:
    """传入选色矩阵 记录矩阵和列表 坐标点 已记录面积 判断该点衍生出的色块大小 返回新的已记录面积"""

    if current_area >= limit_area:
        return current_area

    x_bound, y_bound = selection_array.shape
    if x > 0:
        # 上方点
        if selection_array[x - 1][y] and record_array[x - 1][y]:
            records.append((x - 1, y))
            record_array[x - 1][y] = 0
            current_area = _connected_analysis(selection_array, record_array, records, x - 1, y, limit_area, current_area + 1)
            if current_area >= limit_area:
                return current_area
        # 左上方点
        if y > 0 and selection_array[x - 1][y - 1] and record_array[x - 1][y - 1]:
            records.append((x - 1, y - 1))
            record_array[x - 1][y - 1] = 0
            current_area = _connected_analysis(selection_array, record_array, records, x - 1, y - 1, limit_area, current_area + 1)
            if current_area >= limit_area:
                return current_area
        # 右上方点
        if y < (y_bound - 1) and selection_array[x - 1][y + 1] and record_array[x - 1][y + 1]:
            records.append((x - 1, y + 1))
            record_array[x - 1][y + 1] = 0
            current_area = _connected_analysis(selection_array, record_array, records, x - 1, y + 1, limit_area, current_area + 1)
            if current_area >= limit_area:
                return current_area
    if x < (x_bound - 1):
        # 下方点
        if selection_array[x + 1][y] and record_array[x + 1][y]:
            records.append((x + 1, y))
            record_array[x + 1][y] = 0
            current_area = _connected_analysis(selection_array, record_array, records, x + 1, y, limit_area, current_area + 1)
            if current_area >= limit_area:
                return current_area
        # 左下方点
        if y > 0 and selection_array[x + 1][y - 1] and record_array[x + 1][y - 1]:
            records.append((x + 1, y - 1))
            record_array[x + 1][y - 1] = 0
            current_area = _connected_analysis(selection_array, record_array, records, x + 1, y - 1, limit_area, current_area + 1)
            if current_area >= limit_area:
                return current_area
        # 右下方点
        if y < (y_bound - 1) and selection_array[x + 1][y + 1] and record_array[x + 1][y + 1]:
            records.append((x + 1, y + 1))
            record_array[x + 1][y + 1] = 0
            current_area = _connected_analysis(selection_array, record_array, records, x + 1, y + 1, limit_area, current_area + 1)
            if current_area >= limit_area:
                return current_area
    # 左侧点
    if y > 0 and selection_array[x][y - 1] and record_array[x][y - 1]:
        records.append((x, y - 1))
        record_array[x][y - 1] = 0
        current_area = _connected_analysis(selection_array, record_array, records, x, y - 1, limit_area, current_area + 1)
        if current_area >= limit_area:
            return current_area
    # 右侧点
    if y < (y_bound - 1) and selection_array[x][y + 1] and record_array[x][y + 1]:
        records.append((x, y + 1))
        record_array[x][y + 1] = 0
        current_area = _connected_analysis(selection_array, record_array, records, x, y + 1, limit_area, current_area + 1)

    return current_area

def _area_verify(selection_array: np.ndarray, limit_area: int) -> None:
    """传入选色矩阵和最小面积 将最小面积不满足的像素点选色取消"""

    record_array = np.ones_like(selection_array)
    x_bound, y_bound = selection_array.shape

    for x in range(x_bound):
        for y in range(y_bound):
            if selection_array[x][y] and record_array[x][y]:
                records = []
                records.append((x, y))
                if _connected_analysis(selection_array, record_array, records, x, y, limit_area, 1) < limit_area:
                    for record in records:
                        row, col = record
                        selection_array[row][col] = False # 删除不满足最小面积的像素点
                else:
                    for record in records:
                        row, col = record
                        record_array[row][col] = 1 # 满足最小面积区域重新参与连通分析

def image_process(path: Path, RED: tuple, GREEN: tuple, BLUE: tuple, limit_area: int = 0) -> list:
    """传入路径 选色范围和最小面积 处理路径中的所有图像文件 返回列表 图像名称对应总面积和总强度"""

    print(f"开始分析文件夹中图像:\n路径: {path}\n选色范围: 红{RED} 绿{GREEN} 蓝{BLUE}")

    blk = 255.0
    red_proportion = (blk - RED[1] + RED[0]) / blk
    green_proportion = (blk - GREEN[1] + GREEN[0]) / blk
    blue_proportion = (blk - BLUE[1] + BLUE[0]) / blk
    total = red_proportion + green_proportion + blue_proportion
    try:
        red_coe = red_proportion / total
        green_coe = green_proportion / total
        blue_coe = blue_proportion / total
    except ZeroDivisionError:
        red_coe = green_coe = blue_coe = 1 / 3
        limit_area = 0 # 全选时选色矩阵全为真不需要排除最小面积

    image_names = _read_image_names(path)
    data = list()

    total_img = len(image_names)
    print(f"读取到{total_img}个图像文件")

    # 依次读取图像并处理
    count = 0
    for name in image_names:
        error_flag = ['None']
        rgb = _read_image(path, name, error_flag)

        if error_flag[0] != 'None':
            data.append([name, 'ERROR!', error_flag[0]])
            count += 1
            print(f"\r分析进度: {count}/{total_img}    ", end='')
            continue

        selection_array = _colors_selection(rgb, RED, GREEN, BLUE)
        _area_verify(selection_array, limit_area)

        area = selection_array.sum()
        gray = red_coe * rgb[:, :, 0] + green_coe * rgb[:, :, 1] + blue_coe * rgb[:, :, 2]
        intensity = (gray[selection_array].sum()) / blk

        data.append([name, area, intensity])

        count += 1
        print(f"\r分析进度: {count}/{total_img}    ", end='')

    print()

    return data

if __name__ == "__main__":
    pass