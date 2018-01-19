#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 12:02:50 2018

@author: ajaver
"""
divergent_set = '''
CB4856
CX11314
DL238
ED3017
EG4725
JT11398
JU258
JU775
LKC34
MY16
MY23
N2
'''


set1 = '''
BRC20067
ECA246
ECA251
CX11271
CX11276
CX11285
DL200
DL226
ECA36
ED3040
ED3048
ED3049
ED3052
JU1088
JU1172
JU1213
JU1242
JU1409
JU1440
JU1568
JU1581
JU2007
JU2466
JU2519
JU311
JU323
JU346
JU360
JU440
JU774
JU830
KR314
MY1
NIC1
NIC199
NIC2
NIC252
NIC256
NIC260
NIC261
NIC274
NIC275
NIC277
NIC3
PB303
QG2075
QX1794
WN2002
'''

set2 = '''
AB1
ECA243
CB4854
ECA248
CB4932
ED3005
ED3046
ED3073
ED3077
EG4349
JU1200
JU1212
JU1246
JU1400
JU1530
JU1580
JU1586
JU2001
JU2464
JU2513
JU2522
JU310
JU367
JU393
JU394
JU406
JU778
JU792
JU847
MY10
MY18
NIC166
NIC195
NIC207
NIC236
NIC242
NIC251
NIC255
NIC265
NIC266
NIC271
NIC272
NIC276
ECA259
PX179
QG557
QW947
QX1212
'''

set3 = '''
CB4852
ECA250
ECA252
CX11254
CX11262
CX11264
CX11292
CX11307
CX11315
ED3011
ED3012
EG4347
EG4724
EG4946
GXW1
JU1395
JU1491
JU1652
JU1896
JU2316
JU2526
JU397
JU561
JU642
JU751
JU782
LSJ1
NIC231
NIC258
NIC259
NIC262
NIC267
NIC268
NIC269
PS2025
QG536
QG556
QX1211
QX1233
QX1791
QX1792
QX1793
RC301
WN2001
'''

set4='''
ECA348
ECA349
ECA363
ECA372
ECA396
JU1543
JU1793
JU1808
JU2131
JU2141
JU2234
JU2534
JU2565
JU2566
JU2578
JU2587
JU2593
JU2600
JU2800
JU2862
JU2866
JU2878
JU2879
JU2906
JU3125
JU3127
JU3134
JU3135
JU3137
JU3140
MY2212
MY2453
MY2530
MY2535
MY2573
MY2693
MY2741
MY679
MY920
NIC1107
NIC513
NIC514
NIC522
NIC523
WN2033
XZ1513
XZ1514
XZ1516
'''

strains_codes = '''
ECA348 3F
ECA349 2B
ECA363 56
ECA372 4A
ECA396 48
JU1543 59
JU1793 60
JU1808 52
JU2131 2E
JU2141 54
JU2234 26
JU2534 5E
JU2565 57
JU2566 2C
JU2578 3D
JU2587 02
JU2593 23
JU2600 4B
JU2800 25
JU2862 24
JU2866 05
JU2878 34
JU2879 50
JU2906 17
JU3125 04
JU3127 32
JU3134 5F
JU3135 18
JU3137 76
JU3140 61
MY2212 07
MY2453 0F
MY2530 2A
MY2535 12
MY2573 30
MY2693 5A
MY2741 55
MY679 22
MY920 14
NIC1107 08
NIC513 49
NIC514 16
NIC522 4D
NIC523 58
WN2033 65
XZ1513 20
XZ1514 1B
XZ1516 29
AB1 78
BRC20067 9D
CB4852 FF
CB4854 EE
CB4856 00
CB4932 FD
CX11254 EF
CX11262 FE
CX11264 DD
CX11271 CB
CX11276 D9
CX11285 DB
CX11292 DC
CX11307 CC
CX11314 DA
CX11315 CE
DL200 D3
DL226 C5
DL238 D2
ECA243 99
ECA246 8F
ECA248 A0
ECA250 A2
ECA251 9B
ECA252 9C
ECA259 A1
ECA348 3F
ECA349 2B
ECA36 9A
ECA363 56
ECA372 4A
ECA396 48
ED3005 C2
ED3011 BE
ED3012 CD
ED3017 C1
ED3040 D0
ED3046 D1
ED3048 C4
ED3049 C3
ED3052 BF
ED3073 C0
ED3077 BD
EG4347 71
EG4349 69
EG4724 72
EG4725 6A
EG4946 70
GXW1 C7
JT11398 77
JU1088 80
JU1172 7D
JU1200 BA
JU1212 7E
JU1213 98
JU1242 89
JU1246 A5
JU1395 86
JU1400 9F
JU1409 85
JU1440 A3
JU1491 90
JU1530 7F
JU1543 59
JU1568 91
JU1580 A8
JU1581 87
JU1586 B4
JU1652 B3
JU1793 60
JU1808 52
JU1896 A7
JU2001 9E
JU2007 AB
JU2131 2E
JU2141 54
JU2234 26
JU2316 B7
JU2464 B2
JU2466 B1
JU2513 8A
JU2519 93
JU2522 94
JU2526 8B
JU2534 5E
JU2565 57
JU2566 2C
JU2578 3D
JU258 95
JU2587 02
JU2593 23
JU2600 4B
JU2800 25
JU2862 24
JU2866 05
JU2878 34
JU2879 50
JU2906 17
JU310 A9
JU311 79
JU3125 04
JU3127 32
JU3134 5F
JU3135 18
JU3137 76
JU3140 61
JU323 AC
JU346 81
JU360 B6
JU367 AA
JU393 B8
JU394 B9
JU397 AD
JU406 A4
JU440 B0
JU561 92
JU642 A6
JU751 88
JU774 82
JU775 7A
JU778 7B
JU782 84
JU792 7C
JU830 B5
JU847 83
KR314 BC
LKC34 AE
LSJ1 6F
MY1 6E
MY10 6D
MY16 74
MY18 75
MY2212 07
MY23 6C
MY2453 0F
MY2530 2A
MY2535 12
MY2573 30
MY2693 5A
MY2741 55
MY679 22
MY920 14
N2 6B
NIC1 E1
NIC1107 08
NIC166 CF
NIC195 F0
NIC199 DE
NIC2 F1
NIC207 F4
NIC231 EA
NIC236 E7
NIC242 EC
NIC251 F9
NIC252 E2
NIC255 E4
NIC256 F3
NIC258 F7
NIC259 E8
NIC260 E5
NIC261 F6
NIC262 FB
NIC265 E6
NIC266 F5
NIC267 EB
NIC268 FC
NIC269 ED
NIC271 F8
NIC272 E9
NIC274 E0
NIC275 F2
NIC276 FA
NIC277 E3
NIC3 DF
NIC513 49
NIC514 16
NIC522 4D
NIC523 58
PB303 BB
PS2025 8C
PX179 D5
QG2075 96
QG536 8E
QG556 97
QG557 8D
QW947 68
QX1211 D8
QX1212 CA
QX1233 73
QX1791 D6
QX1792 D7
QX1793 C9
QX1794 C8
RC301 AF
WN2001 D4
WN2002 C6
WN2033 65
XZ1513 20
XZ1514 1B
XZ1516 29
'''

groups = dict(
     divergent_set = divergent_set,
     set1=set1,
     set2=set2,
     set3=set3,
     set4=set4
       )


if __name__ == '__main__':
    strains_codes = {x.split(' ')[0]:x for x in strains_codes.split('\n') if x}
    
    strain_groups = {}
    for k,v in groups.items():
        strain_groups[k] = [strains_codes[x] for x in v.split('\n') if x]
    
    with open('codes_CeNDR.csv', 'w') as fid:
        for k,v in strain_groups.items():    
            fid.write('\n'.join([k + ',' + x for x in v]) + '\n')
        
    
    
    
    

