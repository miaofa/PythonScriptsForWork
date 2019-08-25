# -*- coding: utf-8 -*-

# 全部UI设计
# 默认的输出目录是桌面，针对Linux的还没有添加（最好是home目录）

import tkinter as tk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter import scrolledtext
import os
import conversion


class UI(object):
    def __init__(self, master):

        self.master = master
        self.master.title("bin2bin")
        self.frame_upper = tk.Frame(self.master)
        self.frame_upper.pack()

#        self.CheckVar = tk.IntVar()
#        self.Cb = tk.Checkbutton(self.frame_upper,
#                                 text="直接使用源文件进行转换",
#                                 variable=self.CheckVar,
#                                 onvalue=1, offvalue=0,
#                                 width=50, command=self.Changestatus)

        self.outDir = tk.Label(self.frame_upper, text='选择输出目录', width=20)
        self.dirtext = tk.StringVar()
        self.entrydir = tk.Entry(self.frame_upper,
                                 textvariable=self.dirtext,
                                 width=20)
#        img = Image.open(imgpath)
#        picture = ImageTk.PhotoImage(img)
        # ,command=self.Okfun)#image=picture)
        self.getdirbutton = tk.Button(
            self.frame_upper, text='打开', command=self.ChooseDir)

#        self.Cb.pack()
        self.outDir.pack(side='left')
        self.entrydir.pack(side='left')
        self.getdirbutton.pack(side='left')

        self.frame_down = tk.Frame(self.master)
        self.frame_down.pack(padx=10, pady=30)
        self.ButtonTransform = tk.Button(
            self.frame_down, text='转换', width=3,
            height=2, command=self.Transform)

        # log记录区
        # 滚动文本框
        # wrap=tk.WORD   这个值表示在行的末尾如果有一个单词跨行，会将该单词放到下一行显示,
        # 比如输入hello，he在第一行的行尾,llo在第二行的行首, 这时如果wrap=tk.WORD，
        # 则表示会将 hello 这个单词挪到下一行行首显示, wrap默认的值为tk.CHAR
#        self.logarea = tk.LabelFrame(self.frame_right, text='Log Area')
        self.scr = scrolledtext.ScrolledText(
            self.frame_down, width=30, height=5, wrap=tk.WORD)

        # 选择转换文件按钮
        self.ButtonSelectFile = tk.Button(
            self.frame_down, text='选择文件', width=6,
            height=2, command=self.ChooseFile)

        self.ButtonSelectFile.pack(side='left', padx=10)
        self.scr.pack(side='left', padx=10)
        self.ButtonTransform.pack(side='left', padx=10)

        # 设置欢迎界面
        self.InitScrSayHello()

        # 设置默认状态
        # 选中复选框，置灰下面一行控件
#        self.InitWidgetStatus()
        # 获取windows桌面
        if conversion.deskdir:
            self.dirtext.set(conversion.deskdir)

    def Recordlog(self, strstr):
        # private function to Record the log
        self.scr.insert(tk.END, strstr)
        self.scr.insert(tk.END, '\n')
        self.scr.see(tk.END)

    def InitScrSayHello(self):
        self.Recordlog('欢迎，欢迎!')
        # if any buy please send email to fa.miao@goodwe.com.cn.')
        self.Recordlog('Pytransform 版本 0.0.0.1')
#        self.Recordlog(
#            '若要自己选择输出目录，请取消勾选复选框')

#    active, , or normal
#    def InitWidgetStatus(self):
#        self.outDir['state'] = 'normal'
#        self.entrydir['state'] = 'normal'
#        self.getdirbutton['state'] = 'normal'
#
#        self.Cb.deselect()

#    def Changestatus(self):
#        if self.CheckVar.get() == 0:
#            self.outDir['state'] = 'normal'
#            self.entrydir['state'] = 'normal'
#            self.getdirbutton['state'] = 'normal'
#        elif self.CheckVar.get() == 1:
#            self.outDir['state'] = 'disabled'
#            self.entrydir['state'] = 'disabled'
#            self.getdirbutton['state'] = 'disabled'
#        else:
#            pass

    def ChooseDir(self):
        self.dirtext.set(askdirectory())

    def ChooseFile(self):
        self.infilename = askopenfilename()
        if self.infilename:
            self.Recordlog('已选中文件{}, 接着点击转换按钮'.format(self.infilename))

# 转化主逻辑,传递两个参数，输出文件和输入文件名
    def Transform(self):
        self.outfilename = os.path.join(
            self.dirtext.get(), os.path.basename(self.infilename))
        try:
            conversion.enginebuf(self.infilename, self.outfilename)
        except RuntimeError as e:
            self.Recordlog('文件不正确，请重新选择文件')
        else:     
           self.Recordlog('转化成功')


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("400x190")
    app = UI(root)
    root.mainloop()
