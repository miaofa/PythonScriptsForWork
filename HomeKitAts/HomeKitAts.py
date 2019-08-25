# -*- coding: utf-8 -*-
# Edited by Fa.Miao
# Connecting : Email-->fa.miao@goodwe.com

import tkinter as tk
from tkinter import scrolledtext
import tkinter.messagebox as msgbox
import time
import json
from tkinter import ttk
import os
import pymssql
from serialCommunicate import mySerial

# 全局变量
dirpath = os.path.dirname(__file__)
combobox_values = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7',
                   'COM8', 'COM9', 'COM10', 'COM11', 'COM12', 'COM13', 'COM14',
                   'COM15', 'COM16', 'COM17', 'COM18']

conn = pymssql.connect(u'192.168.60.18', u'sa', u'goodwe!@#123', u'chanxian')
cursor = conn.cursor(as_dict=True)


class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Tigosn2mac")
        frame_upLeft = tk.LabelFrame(self.master, text='扫描区')
        frame_upRight = tk.LabelFrame(self.master, text='配置区')
        frame_down = tk.LabelFrame(self.master, text='log区')

        frame_upLeft.grid(row=0, column=0, ipadx=5, ipady=5)
        frame_upRight.grid(row=0, column=1, ipadx=5, ipady=5)
        frame_down.grid(row=1, column=0, columnspan=2, ipadx=5, ipady=5)

        # 扫描区
        self.label_input = tk.Label(frame_upLeft, text='Input')
        self.label_pcba = tk.Label(frame_upLeft, text='Homekit sn:')
        self.label_mac = tk.Label(frame_upLeft, text='WifiLan sn:')

        self.contentinput = tk.StringVar()
        self.contentpcba = tk.StringVar()
        self.contentmac = tk.StringVar()
        self.e_input = tk.Entry(frame_upLeft, textvariable=self.contentinput)
        self.e_pcba = tk.Entry(frame_upLeft, textvariable=self.contentpcba)
        self.e_mac = tk.Entry(frame_upLeft, textvariable=self.contentmac)
        self.testbutton = tk.Button(
            frame_upLeft, text='测试', command=self.RunTest)

        self.label_input.grid(row=0, column=0)
        self.label_pcba.grid(row=1, column=0)
        self.label_mac.grid(row=2, column=0)
        self.e_input.grid(row=0, column=1)
        self.e_pcba.grid(row=1, column=1)
        self.e_mac.grid(row=2, column=1)
        self.testbutton.grid(row=3, column=1)

        # 绑定事件
        self.e_input.bind("<Return>", lambda event: self.RecordInput())

        # 配置区
        self.label_port = tk.Label(frame_upRight, text='串口号选择:')
        self.content_port = tk.StringVar()
        self.combobox_port = ttk.Combobox(
            frame_upRight, width=8, textvariable=self.content_port,
            values=combobox_values)
        self.configbutton = tk.Button(
            frame_upRight, text='配置', command=self.config_port)
        self.openbutton = tk.Button(
            frame_upRight, text='打开串口', command=self.OpenSerial)
        self.closebutton = tk.Button(
            frame_upRight, text='关闭串口', command=self.CloseSerial)

        self.label_port.grid(row=0, column=0)
        self.combobox_port.grid(row=0, column=1)
        self.configbutton.grid(row=0, column=2, sticky=tk.W + tk.E, ipadx=2)
        self.openbutton.grid(row=1, column=1, sticky=tk.W + tk.E, ipadx=2)
        self.closebutton.grid(row=1, column=2, sticky=tk.W + tk.E, ipadx=2)

        # log区
        self.scr = scrolledtext.ScrolledText(
            frame_down, width=40, height=10, wrap=tk.WORD)
        self.scr.pack()

        # 与下位机通信的serial端口
        self.myser = None
        self.InitCombobox()
#        if(self.content_port.get() in combobox_values and self.myser == None):
#            try:
#                self.myser = mySerial(self.content_port.get())
#            except:
#                self.myser = None
#                msgbox.showwarning('warnning','不能打开对应串口，请重新配置！')

        # 页面初始化操作
        # 1.初始化log区的欢迎页面
        # 2.初始化扫描区的焦点问题
        self.InitScrSayHello()
        self.InitFrame_upLeft()

    # 实现扫描进来的sn放置到不同的entry中去
    def RecordInput(self):
        '''
        根据输入进来的sn来判断究竟需要填到那个entry中
        再将本entry中的字符清零，并focus_set
        '''
        sn = self.contentinput.get()
        if(len(sn) == 17):
            self.contentmac.set(sn.upper())
        elif(len(sn) >= 40):
            self.contentpcba.set(sn[3:19].upper())
        else:
            msgbox.showwarning('warnning', '扫描输入的sn非12位或者40位，请检查！')
        self.e_input.delete(0, tk.END)
        self.e_input.focus_set()

    def RunTest(self):
        '''
        1.  扫描sn：HomeKit的Sn的长度是16位，另一个模块的SN的长度是12位；
            若不满足长度要求，则需要提示“长度不满足要求，重新扫描对应的sn”
        2.  Meter老化结果以及模块老化结果：分别是chanxian数据库中的[MeterTestResult]
            表中的[Result]字段（如果Result数值为PASS即表示老化成功）
            以及[WifiTestResult]表中[Result]字段（如果Result数值为PASS即表示老化成功）
        3.  读取HomeKit序列号指令（通过485方式进行读取）：
            读取HomeKit序列号，循环3，if得到序列号，就立即跳到下个步骤；
            else 60次都是失败的，则弹框提示没能读取到sn号，测试失败！
        4.  比对序列号：
            对比扫码得到的HomeKit Sn和通过485通信方式得到的HomeKit sn，
            若一致测试跳到下一步，若不一致则是测试失败。
        5.  读取Homekit成功指令如下：
            发送：AA 55 80 01 04 F0 00 02 74
            回复：AA 55 01 80 04 F0 01 XX cs1 cs0
            XX为01代表通信成功  00代表通信失败  cs1与cs0代表加和校验的高字节和低字节。
            每5s读一次，如果读到回复01则退出提示OK，如果读到00则循环，最多60次
        '''
        # 先检查两个sn是否有值
        if(self.contentpcba.get() == '' or self.contentmac.get() == ''):
            msgbox.showwarning('warnning', '存在标签没有扫入的情况，请检查！')

        # 第二步查询homekit老化结果
        self.homeKitOld = False
        strsql = "SELECT * FROM MeterTestResult WHERE MeterSN = '{0}' ORDER BY CalcTime DESC".format(
            self.contentpcba.get())
        cursor.execute(strsql)
#        rows = cursor.fetchall()
#        if(len(rows) == 0):
#            self.Recordlog('没有查到HomeKit的老化数据，测试失败！')
#            msgbox.showwarning('没有查到HomeKit的老化数据，测试失败！')
#            return
#        for row in rows:
#            if(str(row['Result']).upper() == 'PASS'):
#                self.homeKitOld = True
#            else:
#                continue
        row = cursor.fetchone()
        if row:
            if(str(row['Result']).upper() == 'PASS'):
                self.homeKitOld = True
        else:
            self.Recordlog('没有查到HomeKit的老化数据，测试失败！')
            msgbox.showwarning('warnning', '没有查到HomeKit的老化数据，测试失败！')
            return
        if(not self.homeKitOld):
            self.Recordlog('HomeKit没有通过老化，测试失败！')
            msgbox.showwarning('warnning', 'HomeKit没有通过老化，测试失败！')
            return
        else:
            self.Recordlog('HomeKit通过老化')
        # 第二步查询Wife模块老化结果
        self.WifimoduleOld = False
        # 模块sn需要有规则，就是去掉第一位和后四为去掉
        wifi_sn = self.contentmac.get()[1: -4]
        # print(wifi_sn)
        strsql = "SELECT * from WifiTestResult WHERE CCID = '{0}' ORDER BY CreationDate DESC".format(
            wifi_sn)
        cursor.execute(strsql)
#        rows = cursor.fetchall()
#        if(len(rows) == 0):
#            self.Recordlog('没有查到Wifi模块的老化数据，测试失败！')
#            msgbox.showwarning('没有查到Wifi模块的老化数据，测试失败！')
#            return
#        for row in rows:
#            if(str(row['Result']).upper() == 'PASS'):
#                self.WifimoduleOld = True
#            else:
#                continue
        row = cursor.fetchone()
        if row:
            if(str(row['TestResult']).upper() == 'PASS'):
                self.WifimoduleOld = True
        else:
            self.Recordlog('没有查到Wifi模块的老化数据，测试失败！')
            msgbox.showwarning('warnning', '没有查到Wifi模块的老化数据，测试失败！')
            return

        if(not self.WifimoduleOld):
            self.Recordlog('Wifi模块没有通过老化，测试失败！')
            msgbox.showwarning('warnning', 'Wifi模块没有通过老化，测试失败！')
            return
        else:
            self.Recordlog('Wifi模块通过老化')
        # 第三步，第四步
        if(self.myser == None):
            msgbox.showwarning('请先配置并打开串口，谢谢！')
            return
        metersn = ''
        self.metersnIssame = False
        for i in range(3):
            metersn = self.myser.ReadMeterSn()
            if(metersn):
                if(metersn == self.contentpcba.get()):
                    self.metersnIssame = True
                    break
            else:
                continue
        if(not self.metersnIssame):
            self.Recordlog('homekit序列号对比失败，测试失败！')
            msgbox.showwarning('warnning', 'homekit序列号对比失败，测试失败！')
            return
        else:
            print(metersn)
            self.Recordlog('homekit序列号对比成功')
        # 第六步
        self.meterConnectWeb = False
        for i in range(60):
            time.sleep(5)
            if(self.myser.ReadMeterNetWorkIsOk()):
                self.meterConnectWeb = True
                break
            else:
                print('Failed Connect service occurs {} times'.format(i))
                continue
        if(not self.meterConnectWeb):
            self.Recordlog('homekit不能连接到服务器，测试失败！')
            msgbox.showwarning('warnning', 'homekit不能连接到服务器，测试失败！')
            return
        else:
            self.Recordlog('homekit 连接服务成功')
            self.Recordlog('Ats站点测试成功')
            msgbox.showinfo('info', 'Ats站点测试成功！')
        # 再次初始化所有的上左框
        self.InitFrame_upLeft()

    def config_port(self):
        '''
        实现端口的配置，使用xml或者json来生成配置文件
        '''
        try:
            com_port = self.content_port.get()
            # print(com_port)
            with open('config.json', 'w', encoding='utf-8') as f:
                jsondict = {'Setting': {'Port': com_port}}
                json.dump(jsondict, f, ensure_ascii=False, indent=4)
                self.Recordlog('配置成功！')
        except:
            self.Recordlog('配置失败，请重新尝试！')
            msgbox.showwarning('配置失败，请重新尝试！')

    def OpenSerial(self):
        try:
            if(self.myser == None):
                self.myser = mySerial(self.content_port.get())
            else:
                self.myser.openAnotherSerial(self.content_port.get())
            self.Recordlog('打开串口成功！')
        except:
            self.Recordlog('打开串口失败！')

    def CloseSerial(self):
        try:
            self.myser.closeSerial()
            self.Recordlog('关闭串口成功！')
        except:
            self.Recordlog('关闭串口失败！')

    def InitFrame_upLeft(self):
        '''
        实现entry数据清空，并将焦点聚焦到e_input上面
        '''
        self.e_input.delete(0, tk.END)
        self.e_pcba.delete(0, tk.END)
        self.e_mac.delete(0, tk.END)
        self.e_input.focus_set()

    def Recordlog(self, strstr):
        '''
        private function to Record the log
        '''
        self.scr.insert(tk.END, strstr)
        self.scr.insert(tk.END, '\n')
        self.scr.see(tk.END)

    def InitScrSayHello(self):
        self.Recordlog('欢迎，欢迎!')
        # if any buy please send email to fa.miao@goodwe.com.cn.')
        self.Recordlog('Homekit ATS 版本 0.0.0.1')

    def InitCombobox(self):
        '''
        从文件中读取相应的值，若没有就算了
        '''
        try:
            strport = ''
            with open('config.json', 'r', encoding='utf-8') as f:
                jsontmp = json.load(f)
                print(jsontmp)
                strport = jsontmp['Setting']['Port']
            # 在进行combox框选中
            self.combobox_port.current(combobox_values.index(strport))
        except:
            self.Recordlog('无相关串口号配置信息，请先配置！')


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    conn.close()
    app.myser.closeSerial()
