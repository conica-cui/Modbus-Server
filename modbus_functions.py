#!/bin/env python3

from math import ceil
from random import randint
from modbus_exception import modbus_exception

def have_modbus_exception(fcode, error):
    print("have_modbus_exception")
    res_fcode = fcode + 0x80
    res_data = error.to_bytes(length=1, byteorder='big')
    return res_fcode, res_data

def have_addr_cnt(data):
    print("have_addr_cnt")
    addr = int.from_bytes(data[0:2], byteorder='big')
    cnt = int.from_bytes(data[2:4], byteorder='big')
    print("- addr", addr)
    print("- cnt", cnt)
    return addr, cnt

def read_coils(fcode, data):
    print("read_coils")
    addr, cnt = have_addr_cnt(data)
    if cnt < 0 or cnt > 0x07D0:
        err = modbus_exception.ILLEGAL_DATA_VALUE
        print("Error: ILLEGAL_DATA_VALUE.")
        return have_modbus_exception(fcode, err)

    if addr > 0xFFFF or addr + cnt - 1 > 0xFFFF:
        err = modbus_exception.ILLEGAL_DATA_ADDRESS        
        print("Error: ILLEGAL_DATA_ADDRESS.")
        return have_modbus_exception(fcode, err)

    byte_cnt = ceil(cnt / 8)
    res_data = byte_cnt.to_bytes(length=1, byteorder='big')
    val = randint(0, pow(2, cnt) - 1)
    res_data += val.to_bytes(length=byte_cnt, byteorder='big')
    print(bin(val)[2:].zfill(cnt))
    
    return fcode, res_data

def read_discrete_inputs(fcode, data):
    print("read_discrete_inputs")
    return read_coils(fcode, data)

def read_holding_registers(fcode, data):
    print("read_holding_registers")

    addr, cnt = have_addr_cnt(data)
    if cnt < 0 or cnt > 125:
        err = modbus_exception.ILLEGAL_DATA_VALUE
        return have_modbus_exception(fcode)

    if addr > 0xFFFF or addr + cnt - 1 > 0xFFFF:
        err = modbus_exception.ILLEGAL_DATA_ADDRESS
        return have_modbus_exception(fcode, err)

    byte_cnt = cnt * 2
    res_data = byte_cnt.to_bytes(length=1, byteorder='big')
    for i in range(cnt):
        val = randint(0, pow(2, 16) - 1)
        print("[{}] {}".format(i,val))
        res_data += val.to_bytes(length=2, byteorder='big')

    return fcode, res_data

def read_input_registers(fcode, data):
    print("read_input_registers")
    return read_holding_registers(fcode, data)

def have_addr_val(data):
    print("have_addr_val")

    addr = int.from_bytes(data[0:2], byteorder='big')
    val = int.from_bytes(data[2:4], byteorder='big')
    print("address:", addr)
    print("val:", val)

    return addr, val

def write_single_coil(fcode, data):
    print("write_single_coil")

    addr, val = have_addr_val(data)
    if val != 0x0 and val != 0xFF00:
        err = modbus_exception.ILLEGAL_DATA_VALUE
        return have_modbus_exception(fcode, err)
    return fcode, data

def write_single_register(fcode, data):
    print("write_single_register")

    addr, val = have_addr_val(data)

    return fcode, data

def parse_multi_regs(data):
    print("parse_multi_regs")
    # print("data:", data)

    addr = int.from_bytes(data[0:2], byteorder='big')
    cnt = int.from_bytes(data[2:4], byteorder='big')
    byte_cnt = int.from_bytes(data[4:5], byteorder='big')
    print("cnt:", cnt)
    print("byte_cnt:", byte_cnt)
    vals = []
    for i in range(0, cnt):
        vals.append(int.from_bytes(data[i*2+5: i*2+7], byteorder='big'))
        print("[{}] {}".format(i, vals[i]))
    return addr, cnt, byte_cnt, vals

def parse_multi_coils(data):
    print("parse_multi_coils")
    print("data:", data)
    addr = int.from_bytes(data[0:2], byteorder='big')
    cnt = int.from_bytes(data[2:4], byteorder='big')
    byte_cnt = int.from_bytes(data[4:5], byteorder='big')
    print("cnt:", cnt)
    print("byte_cnt:", byte_cnt)
    vals = int.from_bytes(data[5: 7], byteorder='big')
    print("len(vals):", len(bin(vals))-2)
    print("val: ", bin(vals))
    return addr, cnt, byte_cnt, vals

def write_multiple_coils(fcode, data):
    print("write_multiple_coils")
    addr, cnt, byte_cnt, vals = parse_multi_coils(data)
    if cnt < 0 or cnt > 0x07B0 or \
       ceil(cnt / 8) != byte_cnt or \
       cnt != len(bin(vals))-2:
        err = modbus_exception.ILLEGAL_DATA_VALUE
        return have_modbus_exception(fcode, err)

    if addr > 0xFFFF or addr + cnt - 1 > 0xFFFF:
        err = modbus_exception.ILLEGAL_DATA_ADDRESS
        return have_modbus_exception(fcode, err)

    res_data = addr.to_bytes(length=2, byteorder='big')
    res_data += cnt.to_bytes(length=2, byteorder='big')
    return fcode, res_data

def write_multiple_registers(fcode, data):
    print("write_multiple_registers")
    addr, cnt, byte_cnt, vals = parse_multi_regs(data)
    print(addr, cnt, byte_cnt, vals)
    if cnt < 0 or cnt > 0x7B or \
       cnt * 2 != byte_cnt or \
       cnt != len(vals):
        err = modbus_exception.ILLEGAL_DATA_VALUE
        return have_modbus_exception(fcode, err)

    if addr > 0xFFFF or addr + cnt - 1 > 0xFFFF:
        err = modbus_exception.ILLEGAL_DATA_ADDRESS
        return have_modbus_exception(fcode, err)

    res_data = addr.to_bytes(length=2, byteorder='big')
    res_data += cnt.to_bytes(length=2, byteorder='big')
    return fcode, res_data

func_dict = {
    0x1:  read_coils,
    0x2:  read_discrete_inputs,
    0x3:  read_holding_registers,
    0x4:  read_input_registers, 
    0x5:  write_single_coil,
    0x6:  write_single_register,
    0xf:  write_multiple_coils,
    0x10: write_multiple_registers,
}
