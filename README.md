# Vload-xunyu

用于迅羽科技电子负载的上位机软件（PyQt6）。支持通过 **COM 串口** / **TCP** 与设备通信，实现实时监控、曲线绘制、数据记录与导出，并逐步完善高级测试（SHORT/LIST/DYNA/AUTO/BATT/LED/OCP/TIME 等）。

## 功能特性

- 实时测量：电压/电流/功率/内阻
- 曲线绘制：实时更新、跟随最新、暂停/继续（暂停时停止测量查询）
- 数据记录：会话式记录到磁盘，适合长时间测试
- 数据导入/导出：CSV / Excel（自动按行数分 Sheet）
- 高级测试：已实现 SHORT（短路）模式基础流程与 UI，其它模式逐步开发中

## 环境与依赖

- Python 3.10+（建议 3.10/3.11）
- Windows

安装依赖：

```bash
pip install -r requirements.txt
```

## 运行

在项目根目录执行：

```bash
python -m app
```

或：

```bash
python app/main.py
```

## 连接方式

- COM：选择串口与波特率后连接（默认打开软件即为 COM 模式）
- TCP：输入 `IP:端口`（端口默认 5025）

> 具体设备指令参考：`电子负载SCPI指令集.md`

## 数据与会话

软件会将采集会话写入到用户文档目录下（默认）：

- `Documents/VLoad/sessions/YYYYMMDD_HHMMSS_<device>/`

会话目录中包含：

- 采集数据 CSV
- 元数据 JSON（设备信息、采样周期等）

## 项目结构

- `app/`：程序源码
  - `core/`：通信/设备管理/录制管理
  - `ui/`：主窗口与各面板

## 截图

（待补充）

## License

暂未添加许可证。
