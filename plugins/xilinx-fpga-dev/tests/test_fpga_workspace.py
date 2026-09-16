from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SERVER = Path(__file__).resolve().parents[1] / "mcp" / "fpga_workspace_server.py"
SPEC = importlib.util.spec_from_file_location("fpga_workspace_server", SERVER)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class WorkspaceToolsTest(unittest.TestCase):
    def test_discovery_and_xdc(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "top.sv").write_text("module top; endmodule\n", encoding="utf-8")
            xdc = root / "top.xdc"
            xdc.write_text(
                "create_clock -name sys -period 10.0 [get_ports clk]\n"
                "set_property PACKAGE_PIN A1 [get_ports clk]\n"
                "set_property IOSTANDARD LVCMOS18 [get_ports clk]\n",
                encoding="utf-8",
            )
            inventory = MODULE.discover_project({"root": str(root)})
            self.assertEqual(inventory["kind_counts"]["systemverilog"], 1)
            self.assertIn("vivado", inventory["likely_flows"])
            analysis = MODULE.analyze_xdc({"path": str(xdc)})
            self.assertEqual(analysis["clocks"][0]["period_ns"], 10.0)
            self.assertFalse(analysis["diagnostics"])

    def test_timing_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / "timing.rpt"
            report.write_text(
                "WNS(ns): -0.125\nTNS(ns): -2.500\nFailing Endpoints: 8\n"
                "CRITICAL WARNING: unconstrained path\n",
                encoding="utf-8",
            )
            parsed = MODULE.parse_vivado_report({"path": str(report)})
            self.assertEqual(parsed["metrics"]["wns_ns"], -0.125)
            self.assertFalse(parsed["timing_met_inferred"])
            self.assertEqual(len(parsed["diagnostic_excerpt"]), 1)

    def test_vivado_table_timing_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            report = Path(temporary) / "timing_summary.rpt"
            report.write_text(
                "WNS(ns)  TNS(ns)  Failing Endpoints  Total Endpoints  WHS(ns)  THS(ns)\n"
                "-------  -------  -----------------  ---------------  -------  -------\n"
                "  0.142    0.000                  0             1024    0.021    0.000\n",
                encoding="utf-8",
            )
            parsed = MODULE.parse_vivado_report({"path": str(report)})
            self.assertEqual(parsed["metrics"]["wns_ns"], 0.142)
            self.assertEqual(parsed["metrics"]["total_endpoints"], 1024)
            self.assertTrue(parsed["timing_met_inferred"])

    def test_tool_list_is_read_only(self) -> None:
        names = {item["name"] for item in MODULE.tool_list()["tools"]}
        self.assertEqual(
            names,
            {"fpga_check_environment", "fpga_discover_project", "fpga_analyze_xdc", "fpga_parse_vivado_report"},
        )


if __name__ == "__main__":
    unittest.main()
