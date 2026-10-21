import fs from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputPath = fileURLToPath(new URL("../templates/company-import-template.xlsx", import.meta.url));
const workbook = Workbook.create();
const input = workbook.worksheets.add("企业导入");
const guide = workbook.worksheets.add("字段说明");

input.showGridLines = false;
input.getRange("A1:J1").values = [["企业名称", "一级行业", "province", "city", "软件/嵌入式研发规模(估)", "icp_tier", "crm_status", "sales_owner", "aliases", "数据说明"]];
input.getRange("A2:J2").values = [["示例企业（模拟，请删除）", "半导体与集成电路", "上海", "上海", "100+", "A", "未建档", "", "示例简称", "模拟数据，不代表真实企业情报"]];
input.getRange("A1:J1").format.fill = "#1E4936";
input.getRange("A1:J1").format.font = { bold: true, color: "#FFFFFF" };
input.getRange("A1:J2").format.verticalAlignment = "center";
input.getRange("A1:J2").format.borders = { preset: "inside", style: "thin", color: "#DCE3DC" };
input.getRange("A1:J2").format.autofitColumns();
input.getRange("A:A").format.columnWidth = 30;
input.getRange("B:B").format.columnWidth = 26;
input.getRange("J:J").format.columnWidth = 36;
input.freezePanes.freezeRows(1);
input.tables.add("A1:J2", true, "CompanyImportTable").style = "TableStyleMedium4";

guide.showGridLines = false;
guide.getRange("A1:D1").values = [["字段", "是否必填", "示例", "说明"]];
guide.getRange("A2:D11").values = [
  ["企业名称", "是", "示例企业（模拟）", "同名企业会跳过，不覆盖既有记录"],
  ["一级行业", "是", "半导体与集成电路", "也兼容字段名 industry"],
  ["province", "是", "上海", "上海、江苏、浙江、安徽、湖北"],
  ["city", "否", "上海", "可填写多个研发地的主要城市"],
  ["软件/嵌入式研发规模(估)", "否", "100+", "区间值取下限用于筛选，待核可留空"],
  ["icp_tier", "否", "A", "A/B/C/待评估"],
  ["crm_status", "否", "未建档", "CRM 当前状态"],
  ["sales_owner", "否", "张三", "销售负责人"],
  ["aliases", "否", "简称A;简称B", "M1 模板预留，API 可逐条维护别名"],
  ["数据说明", "建议", "待公开证据核验", "不得把估算或模拟数据表述为已核验事实"],
];
guide.getRange("A1:D1").format.fill = "#1E4936";
guide.getRange("A1:D1").format.font = { bold: true, color: "#FFFFFF" };
guide.getRange("A1:D11").format.verticalAlignment = "center";
guide.getRange("A1:D11").format.borders = { preset: "inside", style: "thin", color: "#DCE3DC" };
guide.getRange("A1:D11").format.autofitColumns();
guide.getRange("A:A").format.columnWidth = 30;
guide.getRange("D:D").format.columnWidth = 50;
guide.freezePanes.freezeRows(1);

workbook.recalculate();
const check = await workbook.inspect({ kind: "table", range: "企业导入!A1:J2", include: "values,formulas", tableMaxRows: 5, tableMaxCols: 12 });
console.log(check.ndjson);
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 50 }, summary: "final formula error scan" });
console.log(errors.ndjson);
await fs.mkdir(new URL("../templates/", import.meta.url), { recursive: true });
for (const sheetName of ["企业导入", "字段说明"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1.5, format: "png" });
  await fs.writeFile(`/tmp/radar-template-${sheetName}.png`, new Uint8Array(await preview.arrayBuffer()));
}
const file = await SpreadsheetFile.exportXlsx(workbook);
await file.save(outputPath);
console.log(outputPath);

