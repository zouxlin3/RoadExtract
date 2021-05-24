# 1 介绍

1、区域生长使用欧式距离判断像素差异

2、区分树叶使用GLI（gli = (2 * g - r - b) / (2 * g + r + b)）

3、区分阴影使用亮度值

4、如果周围像素小于1个是叶子或阴影，只要周围有4个像素都属于区域，那么这个像素也属于区域

5、如果有5个像素都属于区域，那么这个像素也属于区域

# 2 源代码
https://github.com/zouxlin3/RoadExtract

# 3 使用方法

## 3.1 导入图片


```python
from RoadRegionGrow import RoadImg  # 从源代码下载RoadRegionGrow.py和Point.py
import matplotlib.pyplot as plt
import numpy as np
```


```python
roadimg = RoadImg('test_pic.png')  # 输入图片路径
```


```python
plt.imshow(roadimg.img)
```
    
![image](https://img2020.cnblogs.com/blog/2389253/202105/2389253-20210524174003904-343304199.png)
    


*图片来源（http://www.zhongkezhihang.com/html/news/579.html#lg=1&slide=2）*

## 3.2 选取种子点
选取种子点[400, 600]和[300,1000]（x、y值和图片上是相反的）


```python
seeds = [[400, 600], [300,1000]]
roadimg.add_seeds(seeds)
```

## 3.3 确定区分树木和阴影的阈值

1、绘制gli的直方图


```python
roadimg.gli_hist()
```


    
![image](https://img2020.cnblogs.com/blog/2389253/202105/2389253-20210524174028769-1636328770.png)
    


选取gli阈值为0.01

----

2、绘制亮度值的直方图


```python
roadimg.lightness_hist()
```


    
![image](https://img2020.cnblogs.com/blog/2389253/202105/2389253-20210524174045974-1148448009.png)
    


选取亮度值阈值为140.0

## 3.4 区域生长


```python
label = [255, 0, 0]
em_threshold = 9  # 阈值可以根据多次试验确定，不同的图片不一样
g_thershold = 0.01
l_thershold = 140.0
transparency = 0.5
roadimg.region_grow(label, em_threshold, g_thershold, l_thershold)
plt.imshow(roadimg.add_mask(transparency))
```
    
![image](https://img2020.cnblogs.com/blog/2389253/202105/2389253-20210524174104363-1306458266.png)
    



```python
plt.imshow(np.uint8(roadimg.region))
```
    
![image](https://img2020.cnblogs.com/blog/2389253/202105/2389253-20210524174113625-1380550516.png)
    
```python
for i in range(6):  # 进行多次遗漏检测
    roadimg.leak_detect(label, g_thershold, l_thershold)
plt.imshow(roadimg.add_mask(transparency))
```
    
![image](https://img2020.cnblogs.com/blog/2389253/202105/2389253-20210524174122513-1178849695.png)
    
```python
plt.imshow(np.uint8(roadimg.region))
```
    
![image](https://img2020.cnblogs.com/blog/2389253/202105/2389253-20210524174130195-1737836026.png)
    
# 4 [本文最新版本](https://www.cnblogs.com/zouxlin3/p/14805446.html)
