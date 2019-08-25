# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 09:21:40 2018

@author: fa.miao
"""
import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import scrolledtext
from tkinter.filedialog import asksaveasfilename
from urllib import request
import json
from datetime import datetime, timedelta
import csv


# 全局变量
urlLogin = ['http://hk.goodwe-power.com/datasearch/api/UserSearch/Login',
            'http://eu.goodwe-power.com/datasearch/api/UserSearch/Login',
            'http://au.goodwe-power.com/datasearch/api/UserSearch/Login'
            ]

urlQuery = ['http://hk.goodwe-power.com/datasearch/api/UserSearch/QueryData',
            'http://eu.goodwe-power.com/datasearch/api/UserSearch/QueryData',
            'http://au.goodwe-power.com/datasearch/api/UserSearch/QueryData'
            ]

dirpath = os.path.dirname(__file__)


class App(object):
    def __init__(self, master):

        self.token = ''
        self.AllDataList = []
        self.listkey = []

        self.master = master
        self.master.title("Datasearch")
        self.frame_left = tk.Frame(self.master)
        self.frame_left.pack(expand=1, fill='both')
        # 将这个改编为展示二维数据
        self.tree = ttk.Treeview(self.frame_left, show='headings')
        self.ysb = ttk.Scrollbar(
            self.frame_left, orient='vertical', command=self.tree.yview)
        self.xsb = ttk.Scrollbar(
            self.frame_left, orient='horizontal', command=self.tree.xview)

        # left-side widget layout
        self.tree.grid(row=0, column=0, sticky='NSEW')
        self.ysb.grid(row=0, column=1, sticky='ns')
        self.xsb.grid(row=1, column=0, sticky='ew')
        # left-side frame's grid config
        self.frame_left.columnconfigure(0, weight=1)
        self.frame_left.rowconfigure(0, weight=1)
        self.tree.configure(yscrollcommand=self.ysb.set,
                            xscrollcommand=self.xsb.set)

        # right-side
        self.frame_right = tk.Frame(self.master)
        self.frame_right.pack()
#        self.frame_right.grid(row=1, column=0, sticky='e')

        self.config = tk.LabelFrame(self.frame_right, text='config Account')
        self.User = tk.Label(self.config, text='Name:')
        self.Password = tk.Label(self.config, text='password:')
        self.contentname = tk.StringVar()
        self.contentpassword = tk.StringVar()
        self.EntryUser = tk.Entry(self.config, textvariable=self.contentname)
        self.EntryPassword = tk.Entry(
            self.config, show='*', textvariable=self.contentpassword)
        self.Buttonok = tk.Button(self.config, text='Ok', command=self.Okfun)
        self.Buttoncancel = tk.Button(
            self.config, text='Cancel', command=self.Cancelfun)

#        config.pack(expand=1,fill='x')
        self.config.grid(row=0, column=0, sticky='NS', padx=5)

        self.User.grid(row=0, column=1, sticky='e')
        self.Password.grid(row=1, column=1, sticky='e')
        self.EntryUser.grid(row=0, column=2)
        self.EntryPassword.grid(row=1, column=2)
        self.Buttonok.grid(row=2, column=1)
        self.Buttoncancel.grid(row=2, column=2)

        # right side Query condiction
        self.condiction = tk.LabelFrame(
            self.frame_right, text='Query Condiction')
        # HkConnect  0 AuConnect    1 EuConnect 2
        self.locale = tk.IntVar()
        self.HKRadiobutton = tk.Radiobutton(
            self.condiction, text='HongKong', variable=self.locale, value=0)
        self.EURadiobutton = tk.Radiobutton(
            self.condiction, text='Europe', variable=self.locale, value=1)
        self.AURadiobutton = tk.Radiobutton(
            self.condiction, text='Australia', variable=self.locale, value=2)

        self.Snlabel = tk.Label(self.condiction, text='SN:')
        self.Sn = tk.StringVar()
        self.SnEntry = tk.Entry(self.condiction, textvariable=self.Sn)

        # 时间设定(没有时间控件)
        self.StartTimeLabel = tk.Label(self.condiction, text='StartTime:')
        self.StartTime = tk.StringVar()
        self.startTimeEntry = tk.Entry(
            self.condiction, textvariable=self.StartTime)
        # 获取当前时间并保存到变量之中
        self.EndTimeLabel = tk.Label(self.condiction, text='EndTime:')
        self.EndTime = tk.StringVar()
        self.EndTimeEntry = tk.Entry(
            self.condiction, textvariable=self.EndTime)
        # 设置默认时间
        self.StartTime.set(datetime.now().strftime('%Y-%m-%d'))
        self.EndTime.set(datetime.now().strftime('%Y-%m-%d'))

        # 正常数据或者脏数据
        # 0为正常数据，1为脏数据
        self.Valuetype = tk.IntVar()
        self.NomalTypeRadioButton = tk.Radiobutton(
            self.condiction, text='Nomal data',
            variable=self.Valuetype, value=0)
        self.DirtyTypeRadioButton = tk.Radiobutton(
            self.condiction, text='Dirty data',
            variable=self.Valuetype, value=1)

        # Query condiction layout
        self.condiction.grid(row=0, column=1, sticky='NS', padx=5)

        self.HKRadiobutton.grid(row=0, column=0)
        self.EURadiobutton.grid(row=0, column=1)
        self.AURadiobutton.grid(row=0, column=2)

        self.Snlabel.grid(row=1, column=0)
        self.SnEntry.grid(row=1, column=1, columnspan=2)

        self.StartTimeLabel.grid(row=2, column=0)
        self.startTimeEntry.grid(row=2, column=1, columnspan=2)

        self.EndTimeLabel.grid(row=3, column=0)
        self.EndTimeEntry.grid(row=3, column=1, columnspan=2)

        self.NomalTypeRadioButton.grid(row=4, column=0)
        self.DirtyTypeRadioButton.grid(row=4, column=1)

        # log记录区
        # 滚动文本框
        # wrap=tk.WORD   这个值表示在行的末尾如果有一个单词跨行，会将该单词放到下一行显示,
        # 比如输入hello，he在第一行的行尾,llo在第二行的行首, 这时如果wrap=tk.WORD，
        # 则表示会将 hello 这个单词挪到下一行行首显示, wrap默认的值为tk.CHAR
#        self.logarea = tk.LabelFrame(self.frame_right, text='Log Area')
        self.scr = scrolledtext.ScrolledText(
            self.frame_right, width=30, height=3, wrap=tk.WORD)
        self.scr.grid(row=0, column=2, sticky='NS', padx=5)
#        self.logarea.grid(row=0, column=2,  sticky='NS', padx=5)

        # 行动区
        self.actioneArea = tk.LabelFrame(self.frame_right, text='Action Area')
        self.TotalNumLabel = tk.Label(self.actioneArea, text='Total Number:')
        self.TotalNum = tk.StringVar()
        self.TotalNumEntry = tk.Entry(
            self.actioneArea, state='readonly', textvariable=self.TotalNum)

        self.QueryButton = tk.Button(
            self.actioneArea, text='Query', command=self.startQuery)
        self.TerminalButton = tk.Button(
            self.actioneArea, text='Terminal Query', command=self.endQuery)
        self.SaveButton = tk.Button(
            self.actioneArea, text='Save data', command=self.SaveExcel)

        self.actioneArea.grid(row=0, column=3, sticky='NS', padx=5)
        self.TotalNumLabel.grid(row=0, column=0)
        self.TotalNumEntry.grid(row=0, column=1)
        self.QueryButton.grid(row=1, column=0)
        self.TerminalButton.grid(row=1, column=1)
        self.SaveButton.grid(row=2, column=0, columnspan=2,
                             sticky='WE', pady=5, padx=10)

        # 设置欢迎界面
        self.InitScrSayHello()

    def Okfun(self):

        textmod = {"Account": self.contentname.get(
        ), "PassWord": self.contentpassword.get()}
        # json串数据使用
        textmod = json.dumps(textmod).encode(encoding='utf-8')
        # print(textmod)
        header_dict = {"Content-Type": "application/json"}

        req = request.Request(
            url=urlLogin[self.locale.get()], data=textmod, headers=header_dict)
        res = request.urlopen(req)
        rjson = json.loads(res.read())
        # Get the Result
        # 'msg': '操作成功'
        # 记录到log中
        msg = rjson['msg']
        self.Recordlog(msg)

        self.token = rjson["data"]["token"]

    def Cancelfun(self):
        self.Recordlog('Clear the content in entry')
        self.contentname.set('')
        self.contentpassword.set('')

    def startQuery(self):
        # 检查时间是否满足
        if not self.CheckTimeInRange():
            # 记录信息，弹窗警告
            self.Recordlog('Make sure the Query in 31 days')
            return

        if not self.token:
            # 提醒登录信息要完善，并按了OK按钮
            self.Recordlog('Did you gorget enter your identity information?')
            self.Recordlog('Please enter id information, and try again.')
            return

        # 清空数据
        self.AllDataList = []
        self.delAllItem()
        self.TotalNum.set('')

        # example Formation
        #
        # {
        #  "Sn": "sample string 1",
        #  "StartTime": "2018-07-16",
        #  "EndTime": "2018-07-16T11:45:17.6420834+08:00",
        #  "Area": 0,
        #  "Type": 4,
        #  "page_index": 5,
        #  "page_size": 6
        # }
        Querybody = {"Sn": self.Sn.get(),
                     "StartTime": self.StartTime.get(),
                     "EndTime": self.EndTime.get(),
                     "Area": self.locale.get(),
                     "Type": self.Valuetype.get(),  # 0为正常数据，1为脏数据
                     "page_index": 1,  # index从1开始
                     "page_size": 200000}  # 直接定义到200000
        Querybody = json.dumps(Querybody).encode(encoding='utf-8')
        header_dict1 = {"token": self.token,
                        "Content-Type": "application/json"}
        # print(header_dict1)
        req = request.Request(
            url=urlQuery[self.locale.get()],
            data=Querybody,
            headers=header_dict1)
        res = request.urlopen(req)
        rejson = json.loads(res.read())
        # Todo:这边查不到数据的时候，会为空
        sndata = rejson['data']['Data']
        if not sndata:
            self.Recordlog(
                'There is no data with this SN, Please check the SN.')
            return
        msg = rejson['msg']
        self.Recordlog(msg)
        # 设置TotalNum的值
        self.TotalNum.set(rejson["data"]["Total"])
        # print(sndata)
        myQueryData = json.loads(sndata)
        # 获取除了num之后的所有节点
        self.listkey = list(myQueryData[0].keys())[1:]
        # 计算数组的维度
        row = len(myQueryData)
        col = len(self.listkey)
        # print(row, col)
        # 组织二维数组
        for i in range(row):
            listOneRow = []
            for j in range(col):
                listOneRow.append(str(myQueryData[i][self.listkey[j]]))
            self.AllDataList.append(listOneRow)

        self.refreshRes()

    def endQuery(self):
        self.Recordlog("This function didn't complete !!!")

    def SaveExcel(self):

        # self.file_opt = options = {}
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('all files', '.*'), ('csv files', '.csv')]
        options['initialdir'] = dirpath
        options['initialfile'] = self.Sn.get() + '.csv'
        options['parent'] = self.master
        options['title'] = 'Save the Query data to a file'
        # get filename
        filename = asksaveasfilename(**options)

        # open file on your own
        if filename:
            # 使用csv模块写入数据
            # todo: 可以使用openxls来实现Excel写入
            with open(filename, 'w', newline='') as f:      # 采用b的方式处理可以省去很多问题
                writer = csv.writer(f, dialect='excel')
                writer.writerow(self.listkey)
                writer.writerows(self.AllDataList)

    def refreshRes(self):
        # Show The all data in the Gui application
        self.tree["columns"] = self.listkey
        for onekey in self.listkey:
            self.tree.heading(onekey, text=onekey)
            self.tree.column(onekey, width=70, stretch=True)
        # 前三行设置不一样的宽度
        self.tree.column(self.listkey[0], width=100)
        self.tree.column(self.listkey[1], width=120)
        self.tree.column(self.listkey[2], width=124)

        # 直接一行行的插入
        for i in range(len(self.listkey)):
            self.tree.insert('', i, values=self.AllDataList[i])

    def CheckTimeInRange(self):
        startday = datetime.strptime(self.StartTime.get(), '%Y-%m-%d')
        endday = datetime.strptime(self.EndTime.get(), '%Y-%m-%d')

        return (timedelta(days=31) >= endday - startday)

    def Recordlog(self, strstr):
        # private function to Record the log
        self.scr.insert(tk.END, strstr)
        self.scr.insert(tk.END, '\n')
        self.scr.see(tk.END)

    def InitScrSayHello(self):
        self.Recordlog('Welcome, welcome, welcome!')
        # if any buy please send email to fa.miao@goodwe.com.cn.')
        self.Recordlog('DataSearch Version 0.0.0.1')
        self.Recordlog(
            'Note: You should make sure your Query time in 31 days, thx.')

    def delAllItem(self):
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)


if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("1000x600")
    app = App(root)
    root.mainloop()
