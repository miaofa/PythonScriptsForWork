# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 11:12:14 2019

@author: fa.miao
"""

import crcmod.predefined
# from bitstring import BitStream, BitArray
import os
import mmap
# from struct import unpack

# CRC模块网址：
# http://crcmod.sourceforge.net/crcmod.predefined.html

# 这次python脚本犯得两个错误：
# 1.切片运算时，不计入end
# 2.切片运算的符号市’：‘

# 获取windows桌面
deskdir = os.path.join(os.path.expanduser('~'), 'Desktop')

InverterModel = ['105_grid_connect',
                 '105or205_Energy_storage', 'MT_Costdown', '205_grid_connect']

InverterModelAndAddress = {
    '105_grid_connect': 0x00012000,
    '105or205_Energy_storage': 0x00012000,
    'MT_Costdown': 0x00013000,
    '205_grid_connect': 0x0000a000
}

value = [0x55AA0100, 0x55AA0200, 0x55AA0100, 0x55AA0300]


def read_into_buffer(filename):
    buf = bytearray(os.path.getsize(filename))
    with open(filename, 'rb') as f:
        f.readinto(buf)
    return buf


def configDataHead(length, crc_value, Modelname):
    # 增加数据头
    bufHead = bytearray(32)
    for i in range(32):
        bufHead[i] = 0xff
    bufHead[0] = ord('A')
    bufHead[1] = ord('R')
    bufHead[2] = ord('M')
    if Modelname == InverterModel[1]:
        bufHead[3] = ord('H')
    # 字节倒过来呈现
    bufHead[16] = length & (0xFF)
    bufHead[17] = length >> 8 & (0xFF)
    bufHead[18] = length >> 16 & (0xFF)
    bufHead[19] = length >> 24 & (0xFF)

    bufHead[20] = crc_value & (0xFF)
    bufHead[21] = crc_value >> 8 & (0xFF)

    return bufHead

# 此处需要考虑不符合以上四种情况的时候throw一个异常


def ComfirmTheModelWithBuf(buf):
    print(len(buf))
    for i in range(len(InverterModel)):
        address = InverterModelAndAddress[InverterModel[i]]
#        print(buf[address])
#        print(buf[address + 1])
#        print(buf[address + 2])
#        print(buf[address + 3])
#
#        print(buf[address : address + 4])

        # if(BitArray(m[address, address+3]) == BitArray(value[i])):
#        tmp = unpack('i',  buf[address : address + 4])
#        print(tmp)
        tmpvalue = buf[address] << 24 | buf[address +
                                            1] << 16 | buf[address + 2] << 8 | buf[address + 3]
        # print(tmpvalue)
        if(tmpvalue == value[i]):
            return InverterModel[i]
    # 跳出循环时，抛出异常
    raise RuntimeError('文件不符合规定')


# 对于情形1,2,3，转换规则为去掉前64K文件部分，然后增加32个字节文件头，对于情形4，转换规则为去掉前32K文件部分，增加32字节文件头。
# 32字节文件头规则如下：
# 前3个字节为ascii格式的“ARM”，第17,18,19,20字节为Bin文件除头之外的长度，21,22为Bin文件CRC大小（具体可参考BinCreate软件）
def ClipTheHeadWithBuf(buf, Modelname):

    crc16_func = crcmod.predefined.mkCrcFun('modbus')

    print(len(buf))
    if Modelname in InverterModel[0:3]:

        del buf[0: 64 * 1024 - 32]
        print(len(buf))
        # CRC 校验位
        crc_value = crc16_func(buf[32:])
        print(crc_value)
        bufHead = configDataHead(len(buf) - 32, crc_value, Modelname)

        buf[0:32] = bufHead

    elif Modelname == InverterModel[3]:
        del buf[0: 32 * 1024 - 32]
        print(len(buf))
        # CRC 校验位
        crc_value = crc16_func(buf[32:])
        bufHead = configDataHead(len(buf) - 32, crc_value)

        buf[0:32] = bufHead
    else:
        pass

# 仿照引擎的写法，把所有逻辑层面的都放在这边


def enginebuf(infilename, outfilename):
    # 并网105时文件都会更改文件名，410-02033-xx改为410-00033-xx
    resbuf = read_into_buffer(infilename)
    Modelname = ComfirmTheModelWithBuf(resbuf)
    if Modelname == InverterModel[0]:
        outfilename = outfilename.replace('410-02033', '410-00033', 1)
    ClipTheHeadWithBuf(resbuf, Modelname)
    with open(outfilename, 'wb') as f:
        f.write(resbuf)


def memory_map(filename, access=mmap.ACCESS_WRITE):
    size = os.path.getsize(filename)
    fd = os.open(filename, os.O_RDWR)
    return mmap.mmap(fd, size, access=access)

# 另外有一个有趣特性就是 memoryview ， 它可以通过零复制的方式对已存在的缓冲区执行切片操作，甚至还能修改它的内容。


# 以下为测试
if __name__ == '__main__':
    testbuf = read_into_buffer('410-02033-07(190).bin')
    ClipTheHeadWithBuf(testbuf, ComfirmTheModelWithBuf(testbuf))
    with open('out.bin', 'wb') as f:
        f.write(testbuf)
