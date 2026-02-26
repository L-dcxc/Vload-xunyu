"""电子负载设备业务层"""
from __future__ import annotations

from ..scpi import SCPIClient


class ElectronicLoad:
    """电子负载设备封装，提供高级业务方法"""

    def __init__(self, scpi: SCPIClient):
        self._scpi = scpi

    # ========== 系统命令 ==========

    def get_idn(self) -> str:
        """查询设备信息 (*IDN?)"""
        return self._scpi.query("*IDN?")

    def reset(self) -> None:
        """复位设备 (*RST)"""
        self._scpi.send("*RST")

    def clear_status(self) -> None:
        """清除状态 (*CLS)"""
        self._scpi.send("*CLS")

    def set_remote(self) -> None:
        """进入远程模式 (SYST:REM)"""
        self._scpi.send("SYST:REM")

    def set_local(self) -> None:
        """进入本地模式 (SYST:LOC)"""
        self._scpi.send("SYST:LOC")

    def set_rwlock(self) -> None:
        """进入远程锁定模式 (SYST:RWL)"""
        self._scpi.send("SYST:RWL")

    def set_beeper(self, enabled: bool) -> None:
        """设置蜂鸣器 (SYST:BEEP:STAT)"""
        self._scpi.send(f"SYST:BEEP:STAT {'ON' if enabled else 'OFF'}")

    def get_beeper(self) -> bool:
        """查询蜂鸣器状态"""
        resp = self._scpi.query("SYST:BEEP:STAT?")
        return resp.strip() == "1"

    def set_sense(self, enabled: bool) -> None:
        """设置远端补偿 (SYST:SENS)"""
        self._scpi.send(f"SYST:SENS {'ON' if enabled else 'OFF'}")

    def get_sense(self) -> bool:
        """查询远端补偿状态"""
        resp = self._scpi.query("SYST:SENS?")
        return resp.strip() == "1"

    # ========== 模式控制 ==========

    def set_mode(self, mode: str) -> None:
        """设置工作模式 (MODE)
        
        Args:
            mode: 'CURR'(CC), 'VOLT'(CV), 'POW'(CP), 'RES'(CR)
        """
        self._scpi.send(f"MODE {mode}")

    def get_mode(self) -> str:
        """查询当前工作模式"""
        return self._scpi.query("MODE?").strip()

    # ========== 参数设定 ==========

    def set_current(self, value: float) -> None:
        """设置电流 (CURR)"""
        self._scpi.send(f"CURR {value}")

    def get_current(self) -> float:
        """查询电流设定值"""
        return float(self._scpi.query("CURR?"))

    def set_voltage(self, value: float) -> None:
        """设置电压 (VOLT)"""
        self._scpi.send(f"VOLT {value}")

    def get_voltage(self) -> float:
        """查询电压设定值"""
        return float(self._scpi.query("VOLT?"))

    def set_power(self, value: float) -> None:
        """设置功率 (POW)"""
        self._scpi.send(f"POW {value}")

    def get_power(self) -> float:
        """查询功率设定值"""
        return float(self._scpi.query("POW?"))

    def set_resistance(self, value: float) -> None:
        """设置电阻 (RES)"""
        self._scpi.send(f"RES {value}")

    def get_resistance(self) -> float:
        """查询电阻设定值"""
        return float(self._scpi.query("RES?"))

    # ========== 保护设置 ==========

    def set_current_protection(self, value: float) -> None:
        """设置过流保护 (CURR:PROT)"""
        self._scpi.send(f"CURR:PROT {value}")

    def get_current_protection(self) -> float:
        """查询过流保护值"""
        return float(self._scpi.query("CURR:PROT?"))

    def set_power_protection(self, value: float) -> None:
        """设置过功率保护 (POW:PROT)"""
        self._scpi.send(f"POW:PROT {value}")

    def get_power_protection(self) -> float:
        """查询过功率保护值"""
        return float(self._scpi.query("POW:PROT?"))

    def set_voltage_on(self, value: float) -> None:
        """设置 Von (VOLT:ON)"""
        self._scpi.send(f"VOLT:ON {value}")

    def get_voltage_on(self) -> float:
        """查询 Von"""
        return float(self._scpi.query("VOLT:ON?"))

    def set_voltage_off(self, value: float) -> None:
        """设置 Voff (VOLT:OFF)"""
        self._scpi.send(f"VOLT:OFF {value}")

    def get_voltage_off(self) -> float:
        """查询 Voff"""
        return float(self._scpi.query("VOLT:OFF?"))

    # ========== 量程设置 ==========

    def set_current_range(self, value: float | str) -> None:
        """设置电流档位 (CURR:RANG)"""
        self._scpi.send(f"CURR:RANG {value}")

    def get_current_range(self) -> float:
        """查询电流档位"""
        return float(self._scpi.query("CURR:RANG?"))

    def set_voltage_range(self, value: float | str) -> None:
        """设置电压档位 (VOLT:RANG)"""
        self._scpi.send(f"VOLT:RANG {value}")

    def get_voltage_range(self) -> float:
        """查询电压档位"""
        return float(self._scpi.query("VOLT:RANG?"))

    # ========== 速率设置 ==========

    def set_current_slew(self, value: float) -> None:
        """设置电流上升率及下降率 (CURR:SLEW)"""
        self._scpi.send(f"CURR:SLEW {value}")

    def get_current_slew(self) -> float:
        """查询电流速率"""
        return float(self._scpi.query("CURR:SLEW?"))

    def set_voltage_slew(self, value: float) -> None:
        """设置电压上升率及下降率 (VOLT:SLEW)"""
        self._scpi.send(f"VOLT:SLEW {value}")

    def get_voltage_slew(self) -> float:
        """查询电压速率"""
        return float(self._scpi.query("VOLT:SLEW?"))

    # ========== 测量命令 ==========

    def measure_voltage(self) -> float:
        """测量电压平均值 (MEAS:VOLT?)"""
        return float(self._scpi.query("MEAS:VOLT?"))

    def measure_current(self) -> float:
        """测量电流平均值 (MEAS:CURR?)"""
        return float(self._scpi.query("MEAS:CURR?"))

    def measure_power(self) -> float:
        """测量功率平均值 (MEAS:POW?)"""
        return float(self._scpi.query("MEAS:POW?"))

    def measure_resistance(self) -> float:
        """测量等效阻抗 (MEAS:RES?)"""
        return float(self._scpi.query("MEAS:RES?"))

    def measure_voltage_max(self) -> float:
        """测量电压峰值 (MEAS:VOLT:MAX?)"""
        return float(self._scpi.query("MEAS:VOLT:MAX?"))

    def measure_voltage_min(self) -> float:
        """测量电压最小值 (MEAS:VOLT:MIN?)"""
        return float(self._scpi.query("MEAS:VOLT:MIN?"))

    def measure_current_max(self) -> float:
        """测量电流峰值 (MEAS:CURR:MAX?)"""
        return float(self._scpi.query("MEAS:CURR:MAX?"))

    def measure_current_min(self) -> float:
        """测量电流最小值 (MEAS:CURR:MIN?)"""
        return float(self._scpi.query("MEAS:CURR:MIN?"))

    # ========== 输入控制 ==========

    def set_input(self, enabled: bool) -> None:
        """设置输入开关 (INPUT)"""
        self._scpi.send(f"INPUT {'ON' if enabled else 'OFF'}")

    def get_input(self) -> bool:
        """查询输入开关状态"""
        resp = self._scpi.query("INPUT?")
        return resp.strip() == "1"

    def set_input_short(self, enabled: bool) -> None:
        """使能/禁止输入短路状态 (INPUT:SHORT)

        注：进入短路界面后，配合 INPUT ON/OFF 开始/停止短路测试。
        """
        self._scpi.send(f"INPUT:SHORT {'ON' if enabled else 'OFF'}")
