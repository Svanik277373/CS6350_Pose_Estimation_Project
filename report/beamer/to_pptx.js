// Packs the Beamer slides (rendered to PNG) into report/beamer/slides.pptx, one full-slide image per slide,
// so the PowerPoint looks exactly like slides.pdf.
//   pdftoppm -r 220 -png slides.pdf <dir>/s
//   NODE_PATH=<folder with pptxgenjs> node report/beamer/to_pptx.js <dir>
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const dir = process.argv[2];
const files = fs.readdirSync(dir).filter((f) => /^s-\d+\.png$/.test(f)).sort();
const titles = [
  "Title", "Problem statement", "Proposed pipeline", "Step 1: focal length", "Step 2a: SAM 2.1",
  "Step 2b: which candidate moved", "Step 3: crop and MASt3R", "Step 4: H and E", "Step 5: GRIC and decomposition",
  "Step 6: refinement and outputs", "Evaluation data and preprocessing", "Evaluation metrics", "Score comparison",
  "Worked example", "Roll, pitch and yaw", "Where each method wins", "References", "Thank you",
];

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in, 16:9 like the Beamer slides
pres.title = "Compute change in pose (3D) of small objects";
pres.author = "Sai Svanik Chiramana, Sathwik Chanduluri";
files.forEach((f, i) => {
  const s = pres.addSlide();
  s.background = { color: "FFFFFF" };
  s.addImage({ path: path.join(dir, f), x: 0, y: 0, w: 13.333, h: 7.5, altText: titles[i] || `Slide ${i + 1}` });
  s.addNotes(titles[i] || "");
});
pres.writeFile({ fileName: path.join(__dirname, "slides.pptx") }).then((f) => console.log("written", f, files.length, "slides"));
