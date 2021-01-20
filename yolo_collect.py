import win32gui, win32ui, win32con
from ctypes import windll
from PIL import Image
import cv2
import numpy
import mss
import os
import sys
import io
import zipfile
import time
import signal
import datetime

import tqdm

'''
对后台窗口截图
'''

def GetXY(): #获得模拟器的窗口位置
    hwnd=win32gui.FindWindow('Qt5QWindowIcon','夜神模拟器')#是文件句柄，通过使用visual studio自带的spy++获得的。在工具栏中的 工具->spy++中,Qt5QWindowIcon是窗口类名，夜神模拟器 是窗口标题(窗口标题不一定是你窗口左上角显示的标题)
    # print(hwnd)
    #可操作窗口一般不是主窗口，一般是子窗口，子窗口必须使用FindWindowEx()函数来进行搜索
    hwnd = win32gui.FindWindowEx(hwnd, 0, 'Qt5QWindowIcon', 'ScreenBoardClassWindow');#在窗口句柄为hwnd的窗口中，（本例是 夜神模拟器），寻找子窗口，同样是在spy++工具中看到的窗口信息。Qt5QWindowIcon是窗口类名，ScreenBoardClassWindow是窗口标题
    # hwnd = win32gui.FindWindowEx(hwnd, 0, 'Qt5QWindowIcon', 'QWidgetClassWindow');#在窗口句柄为hwnd的窗口中，（本例是 ScreenBoardClassWindow），寻找子窗口，同样是在spy++工具中看到的窗口信息。Qt5QWindowIcon是窗口类名，ScreenBoardClassWindow是窗口标题
    # print('hwnd=',hwnd)
    text = win32gui.GetWindowText(hwnd)                      #返回的是窗口的名字（不一定是窗口左上角显示的名字）
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)  #(left,top)是左上角的座标，(right,bottom)是右下角的座标
    #win32gui.SetForegroundWindow(hwnd)
    return (left,top,hwnd) #返回模拟器的左上角(x,y)座标（即left,top），以及模拟器窗口的句柄
    #mouseX, mouseY = win32gui.GetCursorPos() # 返回当前鼠标位置，注意座标系统中左上方是(0, 0)
    #print('mouseX=',mouseX,'mouseY=',mouseY)

if __name__ == "__main__":
    dir_path = "./yolo_data"
    pics = []

    def exit(signum, frame):
        print('saving data...')
        # 保存
        for each_data in tqdm.tqdm(iterable=pics):
            file_path = each_data[0]
            file_name = os.path.basename(file_path)
            data = each_data[1]

            with open(file_path, 'wb') as f:
                f.write(data.getvalue())
        sys.exit(0)

    signal.signal(signal.SIGINT, exit)

    airplay_mode = True

    while True:
        # 计时开始
        time_start=time.time()
        if airplay_mode:
            pos = (0, 40)
            width = 1280
            height = 720
        else:
            pos = GetXY()
            width = 960
            height = 540
        
        # The simplest use, save a screen shot of the 1st monitor
        with mss.mss() as sct:
            if airplay_mode:
                grab_mon_index = 0
            else:
                grab_mon_index = 1
            mon = sct.monitors[grab_mon_index]
            monitor = {
                "top": mon["top"] + pos[1],
                "left": mon["left"] + pos[0],
                "width": width,
                "height": height,
                "mon": grab_mon_index,
            }
            image = numpy.array(sct.grab(monitor))
            image = numpy.flip(image[:, :, :3], 2)

        im = Image.fromarray(image)

        now_datetime = datetime.datetime.now()
        file_name = now_datetime.strftime('%Y-%m-%d %H-%M-%S.%f') + '.jpg'
        file_path = os.path.join(dir_path, file_name)
        data = io.BytesIO()
        im.save(data, format='jpeg', quality=85)
        # im.save(data, format='png')
        pics.append((file_path, data))

        # 计时结束
        time_end=time.time()
        print(f'每帧时间：{time_end - time_start}s')

        time.sleep(0.2)

        