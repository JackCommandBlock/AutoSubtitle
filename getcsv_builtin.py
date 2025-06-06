#coding=utf-8
import cv2
import os
import sys
import numpy as np

# 定义窗口名称
winName = 'Colors of the rainbow'

# 定义滑动条回调函数，此处pass用作占位语句保持程序结构的完整性
def nothing(x):
    pass

def getcsv(path):
    # mixed
    # img_original = cv2.imread("demo/mixed/hisa.jpg")[970:1070, 360:1540]

    # flag
    abs_path = os.path.abspath(path)
    abs_path = abs_path.encode(sys.getfilesystemencoding())
    img_original = cv2.imdecode(np.fromfile(abs_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)[915:1070, 360:1540]
    # 颜色空间的转换
    try:
        img_hsv = cv2.cvtColor(img_original, cv2.COLOR_BGR2HSV)
    except cv2.error:
        return ";打开文件错误，可能是因为图片分辨率不是1920*1080"
    # 新建窗口
    cv2.namedWindow(winName)
    # 新建6个滑动条，表示颜色范围的上下边界，这里滑动条的初始化位置即为黄色的颜色范围
    cv2.createTrackbar('LowerbH', winName, 0, 255, nothing)
    cv2.createTrackbar('UpperbH', winName, 255, 255, nothing)
    cv2.createTrackbar('LowerbS', winName, 0, 255, nothing)
    cv2.createTrackbar('UpperbS', winName, 255, 255, nothing)
    cv2.createTrackbar('LowerbV', winName, 0, 255, nothing)
    cv2.createTrackbar('UpperbV', winName, 255, 255, nothing)
    try:
        while 1:
            # 函数cv2.getTrackbarPos()范围当前滑块对应的值
            lowerbH = cv2.getTrackbarPos('LowerbH', winName)
            upperbH = cv2.getTrackbarPos('UpperbH', winName)
            lowerbS = cv2.getTrackbarPos('LowerbS', winName)
            upperbS = cv2.getTrackbarPos('UpperbS', winName)
            lowerbV = cv2.getTrackbarPos('LowerbV', winName)
            upperbV = cv2.getTrackbarPos('UpperbV', winName)
            # 得到目标颜色的二值图像，用作cv2.bitwise_and()的掩模
            img_target = cv2.inRange(img_hsv, (lowerbH, lowerbS, lowerbV), (upperbH, upperbS, upperbV))
            # 输入图像与输入图像在掩模条件下按位与，得到掩模范围内的原图像
            img_specifiedColor = cv2.bitwise_and(img_original, img_original, mask=img_target)
            cv2.imshow(winName, img_specifiedColor)
            if cv2.waitKey(1) > 0:
                cv2.destroyAllWindows()
                return "filter_lower = {},{},{}\nfilter_upper = {},{},{}".format(lowerbH, lowerbS, lowerbV,
                                                                            upperbH, upperbS, upperbV)
    except cv2.error:
        return "filter_lower = {},{},{}\nfilter_upper = {},{},{}".format(lowerbH, lowerbS, lowerbV,
                                                                         upperbH, upperbS, upperbV)