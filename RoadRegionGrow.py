import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt
from Point import Point
from typing import List
import copy


class RoadImg:
    def __init__(self, path: str):
        self.img = cv2.imread(path)  # 读取图片
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)  # cv2读取时默认是BGR色彩空间， 需进行转换
        self.height, self.weight, self.channel = self.img.shape

        self.region = np.zeros(self.img.shape)  # 空的道路区域
        self.check = np.zeros((self.height, self.weight))  # 道路提取时用于检查像素是否被处理，0为未被处理

        self.seeds = []
        self.leak_detect_targets = []

    def add_seeds(self, seeds: List[List[int]]):
        for point in seeds:
            self.seeds.append(Point(point, self.img[point[0], point[1]]))

    '''
    label: 为识别出的像素设置标记颜色
    seeds: 种子点列表，种子点为一个Point类
    em_thershold: 欧式距离阈值
    g_thershold：绿叶指数阈值
    l_thershold: 亮度值阈值
    '''
    def region_grow(self, label: List[int], em_threshold: float, g_thershold: float, l_thershold: float):
        while len(self.seeds) > 0:  # 当seeds里还有种子点时
            point = self.seeds.pop(0)

            if self.check[point.x, point.y] == 0:  # 检查像素是否已处理
                self.region[point.x, point.y] = label  # 种子点属于道路区域，设置标记颜色
                self.check[point.x, point.y] = 1
            else:
                continue

            for i in range(len(point.connects)):  # 对于种子点的每一个相邻像素
                next_point_cord = point.next_point(i, self.height, self.weight)  # 获取相邻像素坐标
                if next_point_cord:  # 检查是否超出边界
                    next_point = Point(next_point_cord, self.img[next_point_cord[0], next_point_cord[1]])
                    if self.check[next_point.x, next_point.y] == 0:  # 检查是否被处理
                        pass
                    else:
                        continue
                else:
                    continue

                euclidean_metric = point.get_euclidean_metric(next_point)  # 相邻像素和种子点的欧式距离
                if euclidean_metric < em_threshold and next_point.is_not_leaf(g_thershold) \
                        and next_point.is_not_shadow(l_thershold):
                    # 欧式距离小于阈值、不是树叶、不是阴影时将像素加入seeds列表
                    self.seeds.append(next_point)
                else:
                    self.leak_detect_targets.append(next_point)  # 不属于道路区域时加入遗漏检测目标列表，将会再检测一次

    def leak_detect(self, label: List[int], g_thershold: float, l_thershold: float):  # 遗漏检测
        for point in self.leak_detect_targets:
            x = point.x
            y = point.y

            if (self.region[x, y] == label).all():
                # 如果该像素已经在区域内，跳过
                continue

            around = 0
            shadow_around = 0
            leaf_around = 0

            for i in range(len(point.connects)):
                next_point_cord = point.next_point(i, self.height, self.weight)  # 获取相邻像素坐标
                if next_point_cord:  # 判断是否超出边界
                    next_point = Point(next_point_cord, self.img[next_point_cord[0], next_point_cord[1]])
                    if (self.region[next_point.x, next_point.y] == label).all():
                        around = around + 1
                    if not next_point.is_not_leaf(g_thershold):
                        leaf_around = leaf_around + 1
                    if not next_point.is_not_shadow(l_thershold):
                        shadow_around = shadow_around + 1

            if leaf_around == 0 and shadow_around == 0 and around >= 4:
                # 如果周围像素小于1个是叶子或阴影，只要周围有4个像素都属于区域，那么这个像素也属于区域
                self.region[x, y] = label
            if around >= 5:
                self.region[x, y] = label

    def add_mask(self, transparency):  # 为图像添加mask，设定透明度
        mask = np.asarray(self.region, np.uint8)  # 调整mask格式和原图一致
        return cv2.addWeighted(self.img, 1, mask, transparency, 0)

    def gli_hist(self):  # 输出直方图用以确定阈值
        y = self.__gli_compute()
        xlabel = 'GLI'
        self.__hist(y, xlabel)

    def lightness_hist(self):  # 输出直方图用以确定阈值
        y = self.__lightness_compute()
        xlabel = 'Lightness'
        self.__hist(y, xlabel)

    def __gli_compute(self):  # 统计直方图所需数据
        gli_list = []
        for x in range(self.height):
            for y in range(self.weight):
                point = self.img[x, y]
                gli = (2*point[1]-point[0]-point[2])/(2*point[1]+point[0]+point[2])
                gli_list.append(gli)

        return gli_list

    def __lightness_compute(self):  # 统计直方图所需数据
        lightness_list = []
        for x in range(self.height):
            for y in range(self.weight):
                point = self.img[x, y]
                hsl_point = cv2.cvtColor(np.uint8([[point]]), cv2.COLOR_RGB2HLS)
                lightness_list.append(hsl_point[0, 0, 1])

        return lightness_list

    def __hist(self, y: List, xlabel: str):  # 绘制直方图
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False
        # plt.figure(figsize=(6.4, 5.4), dpi=100)
        plt.rcParams['ytick.direction'] = 'in'

        plt.hist(y, bins=40, facecolor='forestgreen', edgecolor='darkgreen', linewidth=0.8)
        plt.xlabel(xlabel)
        plt.ylabel('Frequency')
        plt.show()
