# 电子负载SCPI指令集

## 一、SCPI 协议概述

该系列仪器的 SCPI 协议所有下行编程数据及上行返回数据均为 ASCII 字符，以换行符`<NL>(0x0A)`作为一帧数据的结束标志。

### 支持的数据格式

1. `<NR1>`：整数，例如`285`

2. `<NR2>`：含小数点的数字，例如`0.285`

3. `<NR3>`：科学计数法表示的数字，例如`2.85E+2`

4. `<Nrf>`：扩展格式，包含`<NR1>`、`<NR2>`、`<NR3>`，例如`285`、`0.285`、`2.85E2`

5. `<Nrf+>`：包含`<Nrf>`、`MIN`、`MAX`，`MIN`表示负载可设定最小值，`MAX`表示最大值

6. `<Bool>`：布尔值，例如`0/1`或`ON/OFF`

### 数据单位说明

数据单位需跟随在数据之后，若为默认单位可省略：

|数据类型|默认单位|支持单位|
|---|---|---|
|电压|V|mV|
|电流|A|mA|
|功率|W|mW|
|电阻|ohm|-|
|压摆率|A/uS|-|
|时间|S|ms|
### 助记符说明

|助记符|意义||
|---|---|---|
|`<>`|尖括号内为参数缩写||
|`|`|竖线分隔可替代的参数|
|`[]`|方括号内为可选项目||
## 二、共同命令

|命令|功能|语法|返回参数 / 说明|
|---|---|---|---|
|`*IDN?`|查询仪器相关信息|`*IDN?`|返回格式：`产品型号,序列号,软件版本号`，例如`XXXXxx,xxxx,V1.01.20`|
|`*CLS`|清除寄存器（标准事件、查询事件、操作状态、位组寄存器及错误代码）|`*CLS`|无参数，无返回值|
|`*RST`|将负载复位到工厂设定状态|`*RST`|无参数，无返回值|
|`*TRG`|给仪器发送触发信号|`*TRG`|无参数，无返回值|
## 三、系统命令

|命令|功能|语法|参数|复位值|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|---|
|`SYSTem:VERSion?`|查询负载遵循的 SCPI 版本号|`SYST:VERS?`|-|-|-|`SYSTEM:VERSION?`|`<NR1>,<SRD>`，格式为`VXX.XX`|
|`SYSTem:SENSe:STATe`|开启 / 关闭远端补偿功能|`SYST:SENS <bool>`|`0/1`或`OFF/ON`|`OFF`|`SYST:SENS ON`|`SYSTEM:SENSel:STATel?`|`0/1`|
|`SYSTem:BEEPer:STATe`|使能 / 禁止蜂鸣器|`SYST:BEEP:STAT <bool>`|`0/1`或`OFF/ON`|`OFF`|`SYST:BEEP:STAT ON`|`SYSTEM:BEEPer:STATE?`|`0/1`|
|`SYSTem:LOCal`|进入本地模式，面板所有按键可操作|`SYST:LOC`|-|-|-|-|-|
|`SYSTem:REMote`|进入远程模式，除 LOCK 外面板按键被禁止，按 LOCK 可退出|`SYST:REM`|-|-|-|-|-|
|`SYSTem:RWLock`|进入远程模式，面板所有按键被禁止|`SYST:RWL`|-|-|-|-|-|
|`INPut:SHORt`|使能 / 禁止输入短路状态（不改变 on/off 状态）|`INPUT:SHORt <bool>`|`0/1`或`OFF/ON`|-|-|-|-|
|`CURRent:RANGe`|设置电流档位|`CURR:RANG <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`A`|`MAXimum(大量程)`|`CURR:RANG MIN`|`CURRent:RANGe?`|`<NR2>`|
|`VOLTage:RANGe`|设置电压档位，参数落在小档范围则选小档，否则选大档|`VOLT:RANG <Nrf++>`|`0~MAX`、`MINimum`、`MAXimum`，单位`V`|`MAXimum(大量程)`|`SOUR:VOLT:RANG MIN`|`VOLTage:RANGe?`|`<NR2>`|
## 四、档位与保护设置命令

|命令|功能|语法|参数|复位值|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|---|
|`CURRent:SLEW[:BOTH]`|设置电流上升率及下降率|`CURR:SLEW <Nrf+>`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`A/uS`|`1`|`CURR:SLEW 1`或`CURR:SLEW 1A/uS`|`CURRent:SLEW?`|`<NR2>`|
|`CURRent:SLEW:RISE`|设置电流上升率|`CURR:SLEW:RISE <Nrf+>`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`A/uS`|`1`|`CURR:SLEW:RISE 1`|`CURRent:SLEW:RISE?`|`<NR2>`|
|`CURRent:SLEW:FALL`|设置电流下降率|`CURR:SLEW:FALL <Nrf+>`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`A/uS`|`1`|`CURR:SLEW:FALL 1`|`CURRent:SLEW:FALL?`|`<NR2>`|
|`CURRent:PROTection[:LEVEL]`|设置电流保护值|`CURR:PROT <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`A`|`MAXimum`|`CURR:PROT 30`|`CURRent:PROTection[:LEVEL]?`|`<NR2>`|
|`POWer:PROTection[:LEVEL]`|设置功率保护值|`POW:PROT <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`W`|`MAXimum(大量程)`|`POW:PROT 100`|`POWER:PROTection[:LEVEL]?`|`<NR2>`|
|`VOLTage:LEVel:ON`|设置负载开始带载电压值 (Von)|`VOLT:ON <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`V`|`0`|`VOLT:ON 3`|`VOLTage:LEVel:ON?`|`<NR2>`|
|`VOLTage:LEVel:OFF`|设置负载开始卸载电压值 (Voff)|`VOLT:OFF <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`V`|`0.5`|`VOLT:OFF 2`|`VOLTage:LEVel:OFF?`|`<NR2>`|
|`VOLTage:SLEW[:BOTH]`|设置电压上升率及下降率|`VOLT:SLEW <Nrf+>`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`V/ms`|`0.5`|`VOLT:SLEW 0.3`或`VOLT:SLEW 0.3V/MS`|`VOLTage:SLEW?`|`<NR2>`|
## 五、工作模式控制命令

### 模式选择

`FUNCtion`/`MODE`命令等效，用于选择负载输入模式：

|模式参数|工作模式|
|---|---|
|`CURRent`|定电流操作模式|
|`VOLTage`|定电压操作模式|
|`POWer`|定功率操作模式|
|`RESistance`|定电阻操作模式|
|`DYNamic`|动态操作模式|
|`LED`|LED 模式|
|`LIST`|List 模式|
|`OCP`|OCP 过流模式|
|`BATTERY`|BATT 电池测试模式|
|`AUTO`|AUTO 模式|
|命令|语法|参数|复位值|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|
|`FUNCtion`/`MODE`|`FUNC <function>`或`MODE <function>`|上述模式参数|`CURRent`|`MODE CURR`|`FUNCTION?`或`MODE?`|`<NR2>`|
## 六、工作参数设定命令

|命令|功能|语法|参数|复位值|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|---|
|`CURRent[:LEVel[:IMMediate][:AMPLitude]]`|设置 CC 模式下的设定电流|`CURR <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`A`|`MINimum`|`CURR 5`|`CURRent[:LEVel[:IMMediate][:AMPLitude]]?`|`<NR2>`|
|`VOLTage[:LEVel[:IMMediate][:AMPLitude]]`|设置 CV 模式下的设定电压|`VOLT <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`V`|`MAXimum`|`VOLT 100`|`VOLTage[:LEVel[:IMMediate][:AMPLitude]]?`|`<NR2>`|
|`POWer[:LEVel[:IMMediate][:AMPLitude]]`|设置 CP 模式下的设定功率|`POW <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`W`|`MINimum`|`POW 10`|`POWer[:LEVel[:IMMediate][:AMPLitude]]?`|`<NR2>`|
|`RESistance[:LEVel[:IMMediate][:AMPLitude]]`|设置 CR 模式下的设定电阻|`RES <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`Ohm`|`MAXimum`|`RES 150`|`RESistance[:LEVel[:IMMediate][:AMPLitude]]?`|`<NR2>`|
## 七、测量命令

|命令|功能|语法|例子|返回参数|
|---|---|---|---|---|
|`MEASure:VOLTage?`|读取电压平均值|`MEAS:VOLT?`|`MEAS:VOLT?`|`<NR2>`|
|`MEASure:VOLTage:MAXimum?`|读取电压峰值 Vp+|`MEAS:VOLT:MAX?`|`MEAS:VOLT:MAX?`|`<NR2>`|
|`MEASure:VOLTage:MINimum?`|读取电压最小值 Vp-|`MEAS:VOLT:MIN?`|`MEAS:VOLT:MIN?`|`<NR2>`|
|`MEASure:VOLTage:PTPeak?`|读取电压峰峰值 Vpp|`MEAS:VOLT:PTP?`|`MEAS:VOLT:PTP?`|`<NR2>`|
|`MEASure:CURRent?`|读取电流平均值|`MEAS:CURR?`|`MEAS:CURR?`|`<NR2>`|
|`MEASure:CURRent:MAXimum?`|读取电流峰值 Ip+|`MEAS:CURR:MAX?`|`MEAS:CURR:MAX?`|`<NR2>`|
|`MEASure:CURRent:MINimum?`|读取电流最小值 Ip-|`MEAS:CURR:MIN?`|`MEAS:CURR:MIN?`|`<NR2>`|
|`MEASure:CURRent:PTPeak?`|读取电流峰峰值 Ipp|`MEAS:CURR:PTP?`|`MEAS:CURR:PTP?`|`<NR2>`|
|`MEASure:POWer?`|读取功率平均值|`MEAS:POWER?`|`MEAS:POWER?`|`<NR2>`|
|`MEAS:RESistance?`|读取等效阻抗|`MEAS:RESistance?`|`MEAS:RESistance?`|`<NR2>`|
## 八、DYNA 动态模式指令

|命令|功能|语法|参数|复位值|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|---|
|`DYNamic:HIGH[:LEVEL]`|设置动态模式的高准位拉载电流|`DYN:HIGH <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`A`|`0`|`DYN:HIGH 1`|`DYNamic:HIGH[:LEVEL]?`|`<NR2>`|
|`DYNamic:HIGH:DWELL`|设置动态模式高准位拉载电流持续时间|`DYN:HIGH:DWELL <Nrf+>`|`0.00001~50`、`MINimum`、`MAXimum`，单位`S`|`0.00001`|`DYN:HIGH:DWELL 0.01`|`DYNamic:HIGH:DWELL?`|`<NR2>`|
|`DYNamic:LOW[:LEVEL]`|设置动态模式的低准位拉载电流|`DYN:LOW <Nrf+>`|`0~MAX`、`MINimum`、`MAXimum`，单位`A`|`0`|`DYN:LOW 1`|`DYNamic:LOW[:LEVEL]?`|`<NR2>`|
|`DYNamic:LOW:DWELL`|设置动态模式低准位拉载电流持续时间|`DYN:LOW:DWELL <Nrf+>`|`0.00001~50`、`MINimum`、`MAXimum`，单位`S`|`0.00001`|`DYN:LOW:DWELL 1`|`DYNamic:LOW:DWELL?`|`<NR2>`|
|`DYNamic:SLEW`|设置动态模式的电流斜率|`DYN:SLEW <Nrf+>`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`A/uS`|`MAX`|`DYN:SLEW 3`|`DYNamic:SLEW?`|`<NR2>`|
|`DYNamic:SLEW:RISE`|设置动态模式电流上升率|`DYN:SLEW:RISE <Nrf+>`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`A/uS`|`MAX`|`DYN:SLEW:RISE 3`|`DYNamic:SLEW:RISE?`|`<NR2>`|
|`DYNamic:SLEW:FALL`|设置动态模式电流下降率|`DYN:SLEW:FALL <Nrf+>`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`A/uS`|`MAX`|`DYN:SLEW:FALL 3`|`DYNamic:SLEW:FALL?`|`<NR2>`|
|`DYNamic:MODE`|设置动态模式下的工作模式|`DYN:MODE <mode>`|-|-|`DYN:MODE PULS`|`DYNamic:MODE?`|-|
## 九、LED 模式指令

|命令|功能|语法|例子|查询语法|返回参数|
|---|---|---|---|---|---|
|`LED:VOLTage`|设置 LED Vo|`LED:VOLT <Nrf+>`|`LED:VOLT 18`|`LED:VOLT?`|-|
|`LED:CURRent`|设置 LED Io|`LED:CURR <Nrf+>`|`LED:CURR 0.5`|`LED:CURR?`|-|
|`LED:RCOeff`|设置 LED Rd Coeff.|`LED:RCO <Nrf+>`|`LED:RCO 0.1`|`LED:RCO?`|-|
## 十、LIST 模式指令

|命令|功能|语法|参数|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|
|`LIST:COUNt`|设置 List 执行次数，1~99999 为指定次数，超过则为连续模式|`LIST:COUNT <Nrf+>`|`1~99999`、`MINimum`、`MAXimum`|`LIST:COUN 1`|`LIST:COUN?`|-|
|`LIST:CURRent[:LEVEL]`|设置 List 每步的电流|`LIST:CURR <Nrf+>{,<Nrf+>}`|`0~MAX`、`MINimum`、`MAXimum`|`LIST:CURR 0.5,1.0,1.5`|`LIST:CURRent[:LEVEL]?`|`<NR2>`|
|`LIST:CURRent:SLEW`|设置 List 每步的电流变化率|`LIST:CURR:SLEW <Nrf+>{,<Nrf+>}`|`MIN~MAX`、`MINimum`、`MAXimum`，单位`A/uS`|`LIST:CURR:SLEW 1.0,0.1,MAX`|`LIST:CURRent:SLEW?`|`<NR2>{,<NR2>}`|
|`LIST:DWELL`|设置 List 每步的停留时间|`LIST:DWELL <Nrf+>{,<Nrf+>}`|`0.00001~9999`、`MINimum`、`MAXimum`|`LIST:DWELL 0.1,0.05,0.2`|`LIST:DWELL?`|`<NR2>{,<NR2>}`|
|`LIST:STEP`|设置 List 如何响应触发信号：`ONCE`触发一次执行一步，`AUTO`触发一次执行完整 LIST|`LIST:STEP <step>`|`ONCE`、`AUTO`|`LIST:STEP AUTO`|`LIST:STEP?`|`<CRD>`|
|`INITiate:NAME:LIST`|加载设置的 List 参数|`INIT:NAME LIST`|-|-|-|-|
|`LIST:RCL <FILE>`|打开文件|`LIST:RCL <FILE>`|-|`LIST:RCL 1`|`LIST:RCL?`|`<FILE>`|
|`LIST:SAVE <FILE>`|将设置存储到文件|`LIST:SAV <FILE>`|-|`LIST:SAV 2`|-|-|
## 十一、AUTO 自动测试模式指令

|命令|功能|语法|参数|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|
|`AUTO:FILE`|设置所需设置的文件和序号|`AUTO:FILE <NR1>,<NR1>`|`<文件号>,<序号>`|`AUTO:FILE 1,1`|`AUTO:FILE?`|-|
## 十二、OCP 模式指令

|命令|功能|语法|参数|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|
|`OCP:STATe`|启动 / 停止 OCP 测试|`OCP <bool>`|`0/1`或`OFF/ON`|`OCP ON`|`OCP:STATe?`|`0/1`|
|`OCP:ISTart`|设置 OCP 起始电流|`OCP:IST <Nrf+>`|`0~MAX`，单位`A`|`OCP:IST 3`|`OCP:ISTart?`|`<NR2>`|
|`OCP:IEND`|设置 OCP 截止电流|`OCP:IEND <Nrf+>`|`0~MAX`，单位`A`|`OCP:IEND 6`|`OCP:IEND?`|`<NR2>`|
|`OCP:STEP`|设置 OCP 电流上升步数|`OCP:STEP <NR1>`|`1~1000`|-|`OCP:STEP?`|`<NR2>`|
|`OCP:DWELL`|设置 OCP 单步驻留时间|`OCP:DWELL <Nrf+>`|单位`S`/`ms`|`OCP:DWELL 0.01`或`OCP:DWELL 10ms`|`OCP:DWELL?`|-|
|`OCP:VTRig`|设置 OCP 触发电平|`OCP:VTR <Nrf+>`|`0~MAX`，单位`V`|`OCP:VTR 11.8`|`OCP:VTRig?`|`<NR2>`|
|`OCP:RESult:OCP?`|查询 OCP 点电流值|`OCP:RES?`|-|-|`OCP:RESULT:OCP?`|`-1`：测试未结束；`-2`：被测电源电压未跌至 Vtrig；`-3`：未开始测试；正常返回电流值，如`1.23`|
|`OCP:RESult:PMAX?`|查询 PMAX 点|-|-|-|`OCP:RES:PMAX?`|`<NR2>,<NR2>,<NR2>`，单位`W,V,A`，例如`20.00,10.0,2.00`|
## 十三、Timing 模式指令

|命令|功能|语法|参数|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|
|`TIMing:STATe`|启动 / 停止 Timing 测试|`TIM <bool>`|`0/1`或`OFF/ON`|`TIM ON`|`TIMing:STATe?`|`0/1`|
|`TIMing:LOAD:MODE`|设置 Timing 测试时的带载模式|`TIM:LOAD:MODE <mode>`|`CURR`、`VOLT`、`POW`、`RES`|`TIM:LOAD:MODE CURR`|`TIMing:LOAD:MODE?`|`<mode>`|
|`TIMing:LOAD:VALue`|设置 Timing 测试时的带载参数|`TIM:LOAD:VAL <Nrf+>`|单位`A/V/W/ohm`，取决于带载模式|`TIM:LOAD:VAL 1`|`TIMing:LOAD:VALUE?`|`<NR2>`|
|`TIMing:TSTart:SOURce`|设置启动测试的触发源|`TIM:TST:SOUR <source>`|`VOLT`、`CURR`、`EXT`|`TIM:TST:SOUR VOLT`|`TIMing:TSTart:SOURce?`|`<source>`|
|`TIMing:TSTart:EDGE`|设置启动测试的触发沿|`TIM:TST:EDGE <edge>`|`RISE`、`FALL`|`TIM:TST:EDGE RISE`|`TIMing:TSTart:EDGE?`|`<edge>`|
|`TIMing:TSTart:LEVel`|设置启动测试的触发电平|`TIM:TST:LEV <Nrf+>`|取决于启动触发源|`TIM:TST:LEV 1`|`TIMing:TSTart:LEVEL?`|`<NR2>`|
|`TIMing:TEND:SOURce`|设置结束测试的触发源|`TIM:TEND:SOUR <source>`|`VOLT`、`CURR`、`EXT`|`TIM:TEND:SOUR VOLT`|`TIMing:TEND:SOURce?`|`<source>`|
|`TIMing:TEND:EDGE`|设置结束测试的触发沿|`TIM:TEND:EDGE <edge>`|`RISE`、`FALL`|`TIM:TEND:EDGE RISE`|`TIMing:TEND:EDGE?`|`<edge>`|
|`TIMing:TEND:LEVel`|设置结束测试的触发电平|`TIM:TEND:LEV <Nrf+>`|取决于结束触发源|-|`TIMing:TEND:LEVEL?`|`<NR2>`|
|`TIMing:RESult?`|查询 Timing 测试结果|`TIM:RES?`|-|-|`TIMing:RESult?`|`<NR2>`，单位`S`|
## 十四、LOAD EFFEct 模式指令

|命令|功能|语法|参数|复位值|例子|查询语法|返回参数|
|---|---|---|---|---|---|---|---|
|`LEFFect:IMIN`|设置低准位拉载电流|`LEFF:IMIN <NR2>`|`0~I-Normal`、`MINimum`、`MAXimum`，单位`A`|-|`LEFF:IMIN 2`|`LEFF:IMIN?`|`<NR2>`|
|`LEFFect:IMAX`|设置高准位拉载电流|`LEFF:IMAX <NR2>`|`I-Normal~MAX`、`MINimum`、`MAXimum`，单位`A`|-|`LEFF:IMAX 5`|`LEFF:IMAX?`|`<NR2>`|
|`LEFFect:INORMal`|设置正常拉载电流|`LEFF:INORM <NR2>`|`MIN~IMAX`、`MINimum`、`MAXimum`，单位`A`|-|`LEFF:INORM 2`|`LEFF:INORM?`|`<NR2>`|
|`LEFFect:DELay`|设置每步电流拉载时间|`LEFF:DEL <NR2>`|`0.1~MAX`、`MINimum`、`MAXimum`，单位`S`|-|`LEFF:DEL 1`|`LEFF:DEL?`|`<NR2>`|
|`LEFFect:RESult:VOLTage?`|查询最大电压和最小电压之差|`LEFF:RES:VOLT?`|-|-|-|`LEFFect:RESult:VOLTage?`|`<NR2>`|
|`LEFFect:RESult:RESistance?`|查询内阻|`LEFF:RES:RES?`|-|-|-|`LEFFect:RESult:RESistance?`|`<NR2>`|
|`LEFFect:RESult:REGulation?`|查询负载调整率|`LEFF:RES:REG?`|-|-|-|`LEFFect:RESult:REGulation?`|`<NR2>`|
> （注：文档部分内容可能由 AI 生成）