#实现pcba以及Mac序列号存储到数据库中
#并实现可供查询的窗口
#数据库的连接方式：service:192.168.60.18;
#                 uid=sa;
#                 pwd=goodwe!@#123;
#                 database=chanxian;
#table:SDTigoSN
#字段：ID    PCBA_Serial    MAC    CreateTime

# -*- coding: utf8 -*-
import tkinter as tk
from tkinter import scrolledtext
import tkinter.messagebox as msgbox
from tkinter.filedialog import asksaveasfilename
from datetime import datetime
import csv
import os
import pymssql


# 全局变量
dirpath = os.path.dirname(__file__)

conn = pymssql.connect(u'192.168.60.18', u'sa', u'goodwe!@#123', u'chanxian')
cursor = conn.cursor(as_dict=True)

class App:
    def __init__(self,master):
        self.master = master
        self.master.title("Tigosn2mac")
        frame_upLeft = tk.LabelFrame(self.master, text='扫描区')
        frame_upRight = tk.LabelFrame(self.master, text='查询区')
        frame_down = tk.LabelFrame(self.master, text='log区')
        
#        frame_up.pack(expand=1)
#        frame_down.pack(expand=1)
        
        frame_upLeft.grid(row=0, column=0, ipadx=5, ipady=5)
        frame_upRight.grid(row=0, column=1, ipadx=5, ipady=5)
        frame_down.grid(row=1, column=0, columnspan=2, ipadx=5, ipady=5)
        
        # 扫描区
        self.label_pcba = tk.Label(frame_upLeft, text='PCBA sn:')
        self.label_mac= tk.Label(frame_upLeft, text='MAC:')
        
        self.contentpcba = tk.StringVar()
        self.contentmac = tk.StringVar()
        self.e_pcba = tk.Entry(frame_upLeft, width=30, textvariable=self.contentpcba) 
        self.e_mac = tk.Entry(frame_upLeft, width=30, textvariable=self.contentmac)

        
        self.label_pcba.grid(row=0, column=0)  
        self.label_mac.grid(row=1, column=0)
        self.e_pcba.grid(row=0, column=1)  
        self.e_mac.grid(row=1, column=1)
        
        # 绑定事件
        self.e_pcba.bind("<Return>", lambda event, e=self.e_mac : e.focus_set())
        self.e_mac.bind("<Return>", lambda event : self.save2database())
        
        # 查询区
        # 者查询按钮
        self.search_label_pcba = tk.Label(frame_upRight, text='PCBA sn:')
        self.search_label_mac= tk.Label(frame_upRight, text='MAC:')
        
        self.contentsearch_pcba = tk.StringVar()
        self.contentsearch_mac = tk.StringVar()
        self.search_e_pcba = tk.Entry(frame_upRight, textvariable=self.contentsearch_pcba) 
        self.search_e_mac = tk.Entry(frame_upRight, textvariable=self.contentsearch_mac)
        self.search_button1 = tk.Button(frame_upRight, text='查询', command=
                                        self.searchInfo)
        self.search_button2 = tk.Button(frame_upRight, text='导出', command=
                                        self.exportdata)

        self.search_label_pcba.grid(row=0, column=0)  
        self.search_label_mac.grid(row=1, column=0)
        self.search_e_pcba.grid(row=0, column=1)
        self.search_e_mac.grid(row=1, column=1)
        self.search_button1.grid(row=2, column=1, padx=2, pady=2)
        self.search_button2.grid(row=3, column=1, padx=2, pady=2)
        
        #log区
        self.scr = scrolledtext.ScrolledText(
            frame_down, width=40, height=10, wrap=tk.WORD)
        self.scr.pack()
        
        # 页面初始化操作
        # 1.初始化log区的欢迎页面
        # 2.初始化扫描区的焦点问题
        self.InitScrSayHello()
        self.InitFrame_upLeft()
    
    #table:SDTigoSN
    # 存储数据库
    #字段：ID    PCBA_Serial    MAC    CreateTime
    def save2database(self):
#        cursor.executemany(
#            "INSERT INTO persons VALUES (%d, %s, %s)",
#            [(1, 'John Smith', 'John Doe'),
#             (2, 'Jane Doe', 'Joe Dog'),
#             (3, 'Mike T.', 'Sarah H.')])
        try:
            strsql = "INSERT INTO SDTigoSN (PCBA_Serial, MAC, CreateTime) VALUES ('{0}', '{1}', getdate())".format(self.contentpcba.get(), self.contentmac.get())
            print(strsql)
            cursor.execute(strsql)
            conn.commit()
            self.Recordlog('插入数据库成功')
        except:
            self.Recordlog('插入数据库出现异常')
            msgbox.showwarning('异常', '插入数据库出现异常，请重新尝试！')
            
    def searchInfo(self):
        # 都有值则报错
        if len(self.contentsearch_pcba.get().strip()) == 0 and len(self.contentsearch_mac.get().strip()) == 0:
            msgbox.showwarning('没有值', '请检查是否输入PCBA sn或者MAC')
        strinfo = self.contentsearch_pcba.get()
        if len(strinfo.strip()) == 0:
            strinfo = self.contentsearch_mac.get()
            self.getpcbaBymac(strinfo)
        else:
            self.getmacBypcba(strinfo)
            
    # 根据pcba number查询mac数据
    def getpcbaBymac(self, mac):
        strsql = "SELECT * FROM SDTigoSN WHERE MAC='{0}'".format(mac)
        cursor.execute(strsql)
        row = cursor.fetchone()
        if row:
            # 查询到数据
            strtmp = "查到数据PCBA_Serial=%s, MAC=%s" % (row['PCBA_Serial'], row['MAC'])
            self.Recordlog(strtmp)
            self.contentsearch_pcba.set(row['PCBA_Serial'])
        else:
            # 没有查询到数据
            self.Recordlog('没有查到数据，请检查或者再试下！')

    # 根据pcba number查询mac数据
    def getmacBypcba(self, strpcba):
        strsql = "SELECT * FROM SDTigoSN WHERE PCBA_Serial='{0}'".format(strpcba)
        cursor.execute(strsql)
        row = cursor.fetchone()
        if row:
            # 查询到数据
            strtmp = "查到数据PCBA_Serial=%s, MAC=%s" % (row['PCBA_Serial'], row['MAC'])
            self.Recordlog(strtmp)
            self.contentsearch_mac.set(row['MAC'])
        else:
            # 没有查询到数据
            self.Recordlog('没有查到数据，请检查或者再试下！')
            
    def exportdata(self):
        now = datetime.now()
        # self.file_opt = options = {}
        options = {}
        options['defaultextension'] = '.csv'
        options['filetypes'] = [('all files', '.*'), ('csv files', '.csv')]
        options['initialdir'] = dirpath
        options['initialfile'] = 'Tigosn2mac' +now.strftime('%y%m%d') + '.csv'
        options['parent'] = self.master
        options['title'] = 'Save the Query data to a file'
        # get filename
        filename = asksaveasfilename(**options)
        # open file on your own
        try:
            if filename:
                # 使用csv模块写入数据
                with open(filename, 'w', newline='') as csvfile:                
                    fieldnames = ['ID', 'PCBA_Serial', 'MAC', 'CreateTime']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    cursor.execute('SELECT * FROM SDTigoSN')
                    for row in cursor:
                        writer.writerow(row)
            self.Recordlog('导出数据成功')
        except:
            self.Recordlog('导出数据失败')
    
    # 实现entry数据清空，并将焦点聚焦到pcba上面
    def InitFrame_upLeft(self):
        self.e_pcba.delete(0, tk.END)
        self.e_mac.delete(0, tk.END)
        self.e_pcba.focus_set()
        
    def Recordlog(self, strstr):
        # private function to Record the log
        self.scr.insert(tk.END, strstr)
        self.scr.insert(tk.END, '\n')
        self.scr.see(tk.END)
        
    def InitScrSayHello(self):
        self.Recordlog('欢迎，欢迎!')
        # if any buy please send email to fa.miao@goodwe.com.cn.')
        self.Recordlog('Tigosn2mac 版本 0.0.0.1')
 

if __name__ == '__main__':
    root = tk.Tk()
    app=App(root)
    root.mainloop()
    conn.close()

    