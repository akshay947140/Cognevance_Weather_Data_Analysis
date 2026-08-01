const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun,
  Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  BorderStyle, PageOrientation
} = require("docx");

const CHART_DIR = "/home/claude/weather_project/charts";
const OUT = "/home/claude/weather_project/Weather_Data_Analysis_Report.docx";

function img(path, width, height) {
  return new ImageRun({
    data: fs.readFileSync(path),
    transformation: { width, height },
    type: "png",
  });
}

function heading(text, level = HeadingLevel.HEADING_1) {
  return new Paragraph({ text, heading: level, spacing: { before: 300, after: 150 } });
}

function body(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, ...opts })],
    spacing: { after: 150 },
  });
}

function bullet(text) {
  return new Paragraph({
    text,
    bullet: { level: 0 },
    spacing: { after: 80 },
  });
}

// ---- Monthly summary table data ----
const monthly = [
  ["Month", "Avg Temp (°C)", "Avg Humidity (%)", "Total Rainfall (mm)"],
  ["January", "7.04", "76.66", "236.0"],
  ["February", "11.63", "74.97", "189.0"],
  ["March", "17.28", "71.22", "122.7"],
  ["April", "23.49", "65.55", "141.4"],
  ["May", "27.47", "63.86", "115.0"],
  ["June", "30.35", "62.72", "100.0"],
  ["July", "28.30", "63.98", "94.8"],
  ["August", "24.64", "64.07", "132.4"],
  ["September", "18.72", "67.57", "136.5"],
  ["October", "13.16", "73.78", "88.3"],
  ["November", "7.86", "75.90", "104.1"],
  ["December", "5.93", "78.16", "247.1"],
];

const colWidths = [2200, 2400, 2400, 2400];
const tableRows = monthly.map((row, i) =>
  new TableRow({
    children: row.map((cell, j) =>
      new TableCell({
        width: { size: colWidths[j], type: WidthType.DXA },
        shading: i === 0 ? { type: ShadingType.CLEAR, fill: "2E5395" } : undefined,
        children: [new Paragraph({
          children: [new TextRun({
            text: cell,
            bold: i === 0,
            color: i === 0 ? "FFFFFF" : "000000",
          })],
        })],
      })
    ),
  })
);

const doc = new Document({
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 } }, // US Letter
    },
    children: [
      new Paragraph({
        children: [new TextRun({ text: "Weather Data Analysis", bold: true, size: 56, color: "2E5395" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 100 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Insights Report — 2-Year Daily Weather Dataset (2023–2024)", size: 26, color: "555555" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
      }),

      heading("1. Project Overview"),
      body("This project analyzes a two-year daily weather dataset (730 records) covering temperature, humidity, and rainfall. The workflow follows the standard data-analysis pipeline: data collection, cleaning, exploratory analysis, visualization, and reporting, using Python (Pandas, Matplotlib, and Seaborn)."),

      heading("2. Data Collection & Cleaning"),
      body("The raw dataset (740 rows including intentional data-quality issues, as is typical of real-world sources) was cleaned as follows:"),
      bullet("Removed 10 exact duplicate rows."),
      bullet("Identified and nulled out physically impossible readings: 32 invalid temperature values (e.g. sensor glitches reading 999°C), 24 invalid humidity values (e.g. negative percentages), and 3 negative rainfall values."),
      bullet("Standardized inconsistent text casing in the month field."),
      bullet("Filled missing temperature and humidity readings using linear interpolation across the date axis, since both are continuous physical quantities that change smoothly day to day."),
      bullet("Filled missing rainfall readings using the median rainfall for that calendar month, since rainfall is highly variable and a monthly median is more representative than interpolation or assuming zero."),
      body("Result: a clean dataset of 730 daily records with zero missing or invalid values, saved to weather_clean.csv.", { italics: true }),

      heading("3. Monthly Summary Statistics"),
      new Table({
        width: { size: 9400, type: WidthType.DXA },
        columnWidths: colWidths,
        rows: tableRows,
      }),
      new Paragraph({ text: "", spacing: { after: 200 } }),

      heading("4. Key Insights"),
      bullet("Seasonal temperature swing: average monthly temperature ranges from about 5.9°C in December to 30.4°C in June — a clear, smooth seasonal cycle typical of a mid-latitude climate."),
      bullet("Humidity moves opposite to temperature: the warmest months (June–August) show the lowest average humidity (~63%), while the coldest months (December–January) show the highest (~77%)."),
      bullet("Rainfall is concentrated in winter: December and January together account for roughly a third of total annual rainfall, while mid-summer (June–October) is comparatively dry."),
      bullet("Temperature and humidity are negatively correlated, confirming the visual pattern in the scatter plot and heatmap — as temperature rises, relative humidity tends to fall."),
      bullet("Spring and Autumn act as transition seasons, with wide temperature spread (visible in the seasonal boxplot) as the climate shifts between summer and winter regimes."),

      heading("5. Visualizations"),

      new Paragraph({ text: "Average Monthly Temperature", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      new Paragraph({ children: [img(`${CHART_DIR}/01_monthly_avg_temperature.png`, 550, 275)] }),

      new Paragraph({ text: "Average Monthly Humidity", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      new Paragraph({ children: [img(`${CHART_DIR}/02_monthly_avg_humidity.png`, 550, 275)] }),

      new Paragraph({ text: "Total Monthly Rainfall", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      new Paragraph({ children: [img(`${CHART_DIR}/03_monthly_total_rainfall.png`, 550, 275)] }),

      new Paragraph({ text: "Temperature Distribution by Season", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      new Paragraph({ children: [img(`${CHART_DIR}/04_seasonal_temperature_boxplot.png`, 460, 288)] }),

      new Paragraph({ text: "Temperature vs Humidity Relationship", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      new Paragraph({ children: [img(`${CHART_DIR}/05_temp_vs_humidity_scatter.png`, 420, 360)] }),

      new Paragraph({ text: "Correlation Between Variables", heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 } }),
      new Paragraph({ children: [img(`${CHART_DIR}/06_correlation_heatmap.png`, 350, 280)] }),

      heading("6. Conclusion"),
      body("The dataset shows a well-defined seasonal pattern: hot, relatively dry summers; cold, wetter winters; and humidity that consistently moves opposite to temperature. This kind of pipeline — clean, analyze, visualize — generalizes directly to real datasets pulled from sources like Kaggle's 'Historical Weather Data' or NOAA archives; only the data-loading step would change."),

      heading("7. Project Files"),
      bullet("src/generate_dataset.py — generates the raw dataset (replace with your own Kaggle CSV loader if using real data)"),
      bullet("src/clean_analyze.py — cleaning, analysis, and chart generation"),
      bullet("data/weather_raw.csv — raw dataset"),
      bullet("data/weather_clean.csv — cleaned dataset"),
      bullet("data/monthly_summary.csv — monthly aggregated statistics"),
      bullet("charts/ — six PNG visualizations"),
      bullet("README.md — setup and GitHub instructions"),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log("Report written to", OUT);
});
