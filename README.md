# ZCode FPGA Dev Plugin

面向 AMD/Xilinx FPGA 开发的 ZCode 插件市场。由 Codex 版 `Codex-FPGA-Dev-Plugin` 移植，Windows 与 Linux/macOS/WSL 双平台适配。它把经过筛选的工作流知识、一个零依赖只读 MCP，以及可选的社区 Vivado MCP 组合为可通过 GitHub 安装的 marketplace。

## 包含内容

- `xilinx-vivado-flow`：Vivado 工程、Tcl/XDC、综合、实现、时序收敛和 bitstream gate。
- `xilinx-vitis-hls`：C/C++ HLS、接口综合、II/延迟/资源优化和 C/RTL 协同仿真。
- `fpga-rtl-verification`：Verilator/Verible/Icarus/cocotb/Yosys/SymbiYosys 验证闭环。
- `xilinx-alveo-acceleration`：Alveo U250/V80、XRT、Vitis kernel、PCIe/XDMA/QDMA 与 host/runtime 协同。
- `xilinx-hardware-debug`：Hardware Manager、ILA/VIO、JTAG、证据化 bring-up。
- `xilinx-embedded-platform`：Zynq/Zynq UltraScale+ MPSoC/Versal、XSA、Vitis、PetaLinux、启动镜像。
- `fpga-workspace` MCP：无需第三方包即可做环境体检、工程盘点、XDC 静态分析和 Vivado 报告解析；不会修改工程或烧写器件。
- `vivado` MCP：优先运行已安装的 `vivado-mcp==0.3.25`；未安装时提供可查询的 setup 状态工具，不拖垮插件加载。

## 安装

### 1. 添加市场并安装插件

在 ZCode 的插件市场（Discover → `+`）中添加本 GitHub 仓库：

```
https://github.com/dx3906999/zcode-plugin-fpga-dev
```

然后安装 `xilinx-fpga-dev`。重新打开一个 ZCode 线程，使 Skills 和 MCP 工具进入新会话。

### 2. 选择 Python 解释器（平台差异唯一的一步）

插件 MCP 通过 Python 启动，仓库默认配置为 `python3`：

- **Linux / macOS / WSL**：开箱即用，无需任何操作（要求 Python ≥ 3.10）。
- **Windows**：`python3` 通常不存在。安装插件后执行一次（每次插件更新后重跑）：

  ```bat
  py "%USERPROFILE%\.zcode\cli\plugins\cache\zcode-plugin-fpga-dev\xilinx-fpga-dev\<version>\scripts\setup_windows.py"
  ```

  脚本会自动探测 `py` → `python` 并就地改写已安装副本的 `.mcp.json`，然后重启 ZCode 生效。支持 `--command <路径>` 强制指定解释器、`--revert` 恢复默认。

内置只读 MCP 无需安装任何依赖。若要让 ZCode 直接控制本机 Vivado，再执行：

```bash
python3 plugins/xilinx-fpga-dev/scripts/setup_vivado_mcp.py
```

该命令在用户缓存目录（Linux `~/.cache/zcode-fpga-dev/`，Windows `%LOCALAPPDATA%\zcode-fpga-dev\`）创建隔离虚拟环境并安装固定版本 `vivado-mcp==0.3.25`。它不会修改 Vivado 初始化文件。若需要 GUI attach 模式，再显式运行该工具自身的 `install` 或 `doctor --fix`，并先检查其计划与备份位置。

常见环境变量：

```bash
export VIVADO_PATH=/tools/Xilinx/Vivado/2024.2/bin/vivado
export VITIS_PATH=/tools/Xilinx/Vitis/2024.2/bin/vitis
```

- Vivado MCP 的安装位置可通过 `ZCODE_FPGA_VIVADO_MCP_PYTHON` 覆盖（兼容旧名 `CODEX_FPGA_VIVADO_MCP_PYTHON`）。
- 缓存目录可通过 `ZCODE_FPGA_CACHE_DIR` 覆盖。
- 版本可在安装时使用 `--version` 覆盖。默认版本经过验证，升级前应先查看上游 changelog 并运行测试。

## Windows + WSL 混合开发建议

- Windows 侧保留 Vivado GUI（综合/实现/烧写/Hardware Manager）；WSL 侧装 `verilator verible iverilog yosys cocotb` 做快速 lint/仿真。
- WSL 里可以直接调用 Windows 的 Vivado：`/mnt/c/Xilinx/Vivado/<ver>/bin/vivado.bat -mode batch -source xxx.tcl`，构建流水线可统一在 WSL 编写。
- 仓库放 NTFS 盘、WSL 经 `/mnt/` 访问可共用源码；但 fuzzer 等重型编译请在 WSL 自身文件系统（`~/`）中进行。
- 注意：WSL2 不支持 PCIe 直通——Alveo/XRT、XDMA 类卡需要原生 Linux（双系统或独立机器）；JTAG/USB 设备可用 usbipd-win 挂入 WSL；以太网接口的板卡不受影响。

## 验证

```bash
python3 plugins/xilinx-fpga-dev/scripts/validate_bundle.py
```

校验清单/市场一致性、MCP schema 合法性（ZCode 会丢弃含未知键的服务器）、全部 Python 脚本可编译、两个 stdio 服务器回环握手，并运行单元测试。不依赖 ZCode 或 Vivado 安装。

## 安全边界

- 生成 bitstream、编程 FPGA、写寄存器/内存、运行无边界 Tcl、重建工程和修改 Vivado init 文件均不是隐式授权。
- Skills 要求先保留基线报告，再逐阶段验证；不会用"综合通过"替代仿真、CDC、DRC 或时序证据。
- 内置 MCP 只读文件；它最多执行短时 `--version` 探针，不运行综合或实现。
- 外部 MCP 由其 Apache-2.0 上游独立分发，本仓库没有复制其源码。

调研与取舍详见 [docs/research-landscape.md](docs/research-landscape.md)，架构说明见 [docs/architecture.md](docs/architecture.md)。
