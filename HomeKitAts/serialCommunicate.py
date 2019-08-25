# -*- coding: utf-8 -*-
# 串口的读取延时和写入延时均为5秒钟
#serial.Serial() as ser:
#    ser.baudrate = 19200
#    ser.port = 'COM1'
#    ser.open()
#    ser.write(b'hello')
# (port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE, 
# stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False, 
# write_timeout=None, dsrdtr=False, inter_byte_timeout=None)
import serial
    
'''
接受到byte(128位)检查函数：
1.先查找AA55，找到AA55是从此处开始截断数据包，（此处后面的字节数组为有效字节）
2.检查一开始是否为AA55（明显这不不需要，在上步时已经可以100%确认）
3.检查收到的字节数组和发送的字节数组的源地址和目的地址是否对应
if( ( pSendDataPacket[2] != ReceiveData[3] )||(pSendDataPacket[3] != ReceiveData[2])) continue;
4.控制吗是否一致pSendDataPacket[4] != ReceiveData[4]
5.功能码是否匹配（即满足发送的功能码 + 0x80 是否等于收到的功能码）
6.ReceiveData[6]是数据长度位，ReceiveData[7]是返回指令位，0x06为成功，0x15为失败。
就是表明当长度为1，并且数据位为0x15的时候，表明下位机回复的是失败。
若已经达到第三遍时，取消注册，重新注册，（显然代码中）没有完成此步骤
7.判断校验和是否相等
'''
def CheckReceviceBytes(sendData, receviceData):
    try:
        #第一步
        for i in range(len(receviceData)):
            if(receviceData[i] == 0xaa and receviceData[i + 1] == 0x55):
                receviceData = receviceData[i:]
                break
            else:
                return False
                #第三步
        if(sendData[2] == receviceData[3] and sendData[3] == receviceData[2]):
            #第四部
            if(sendData[4] == receviceData[4]):
                #第五步
                #if(sendData[5] + 0x80 == receviceData[5]):
                if(sendData[5]  == receviceData[5]):
                    #第六步
                    if(not (receviceData[6] == 1 and receviceData[7] == 0x15)):
                        return True
        else:
            return False
    except:
        return False
                        
'''
data为bytearray类型
返回为bytearray(2),高字节在前，低字节在后
'''
def checkSum(data):
    resbytes = bytearray(2)
    for i in range(len(data)):
        sum1 = sum(data)
    resbytes[0] = (sum1 >> 8 ) & 0xff
    resbytes[1] = sum1 & 0xff
    return resbytes

'''
使用装饰器实现单例模式
'''
def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton
    
'''
mySerial实现单例模式
'''
@Singleton
class mySerial(object):
    def __init__(self, port, timeout=5, write_timeout=5):
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.ser = serial.Serial(port,timeout=timeout, write_timeout=write_timeout)
    
    # 使用这个函数的函数使用try...catch，捕捉异常，以循环三次
    def ReadMeterSn(self):
        meterReadSnBytes = bytearray(10)
        meterReadSnBytes[0] = 0xaa
        meterReadSnBytes[1] = 0x55
        meterReadSnBytes[2] = 0x80 #Source Address
        meterReadSnBytes[3] = 0x01 #destion Address
        meterReadSnBytes[4] = 0x04 #control code
        meterReadSnBytes[5] = 0x83 #function code
        meterReadSnBytes[6] = 0x01 #data length
        meterReadSnBytes[7] = 0x00 #data
        checksumArray = checkSum(meterReadSnBytes[:-2])
        meterReadSnBytes[8] = checksumArray[0]
        meterReadSnBytes[9] = checksumArray[1]
        
        # 直接写入
        self.ser.write(meterReadSnBytes)
        receviceData = self.ser.read(128)
        #print(receviceData)
        if(CheckReceviceBytes(meterReadSnBytes, bytearray(receviceData))):
            metersn = receviceData[7 : 7 + 16].decode('utf-8')
            return metersn
        else:
            return False
        
    
    def ReadMeterNetWorkIsOk(self):
        MeterNetWorkIsOk = bytearray(9)
        MeterNetWorkIsOk[0] = 0xaa
        MeterNetWorkIsOk[1] = 0x55
        MeterNetWorkIsOk[2] = 0x80 #Source Address
        MeterNetWorkIsOk[3] = 0x01 #destion Address
        MeterNetWorkIsOk[4] = 0x04 #control code
        MeterNetWorkIsOk[5] = 0xf0 #function code
        MeterNetWorkIsOk[6] = 0x00
        checksumArray = checkSum(MeterNetWorkIsOk[:-2])
        MeterNetWorkIsOk[7] = checksumArray[0]
        MeterNetWorkIsOk[8] = checksumArray[1]
        
        # 直接写入
        self.ser.write(MeterNetWorkIsOk)
        receviceData = self.ser.read(128)
        #print(receviceData)
        if(CheckReceviceBytes(MeterNetWorkIsOk, bytearray(receviceData))):
            print(receviceData[7])
            if(receviceData[7] == 0x01):
                return True
            else:
                return False

    
    def openAnotherSerial(self, port1):
        self.ser.close()
        self.ser = serial.Serial(port1,timeout=self.
                                 timeout, write_timeout=self.write_timeout)
    
    def closeSerial(self):
        self.ser.close()
        
    
    
    
