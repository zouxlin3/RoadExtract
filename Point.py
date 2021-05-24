import numpy as np
import cv2
from typing import List


class Point:
    def __init__(self, cord: List[int], rgb: List[int]):
        self.x = cord[0]
        self.y = cord[1]
        self.rgb = rgb
        self.connects = [[-1, -1], [0, -1], [1, -1], [-1, 1], [1, 1], [0, 1], [1, 0], [-1, 0]]  # 用于计算相邻像素的坐标

    def next_point(self, i, height, weight):  # 计算一个相邻像素的坐标并返回该像素点坐标
        next_x = self.x+self.connects[i][0]
        next_y = self.y+self.connects[i][1]
        if next_x < 0 or next_y < 0 or next_x >= height or next_y >= weight:  # 判断是否超出图像边界
            return False
        return [next_x, next_y]

    def get_euclidean_metric(self, point):  # 计算两个像素的欧式距离，需要强制转化为整型计算
        r = int(self.rgb[0])
        g = int(self.rgb[1])
        b = int(self.rgb[2])
        nr = int(point.rgb[0])
        ng = int(point.rgb[1])
        nb = int(point.rgb[2])

        euclidean_metric = ((r - nr) ** 2 + (g - ng) ** 2 + (b - nb) ** 2) ** 0.5
        return euclidean_metric

    def is_not_leaf(self, thershold: float):  # 判断该像素是否为叶子
        r = self.rgb[0]
        g = self.rgb[1]
        b = self.rgb[2]

        gli = (2 * g - r - b) / (2 * g + r + b)  # 计算该像元的GLI指数（绿叶指数）
        if gli < thershold:
            return True
        return False

    def is_not_shadow(self, thershold: float):  # 检测该像素是否为阴影
        hsl_point = cv2.cvtColor(np.uint8([[self.rgb]]), cv2.COLOR_RGB2HLS)  # 将像素转化为hls色彩空间
        if hsl_point[0, 0, 1] < thershold:  # 亮度小于阈值时
            return False
        return True
