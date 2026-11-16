// Builds report/slides.pptx (16:9) for the TPA-12 presentation.
//   set NODE_PATH=<folder with node_modules containing pptxgenjs>
//   node report\slides.js
const path = require("path");
const pptxgen = require("pptxgenjs");

const SKILL = process.env.PPTX_SKILL || "";
const FIG = path.join(__dirname, "figures");
const OUT = path.join(__dirname, "slides.pptx");

const THEME = {
  name: "Pose TPA12",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1F2430", lt1: "FFFFFF", dk2: "16324A", lt2: "EEF3F8",
    accent1: "2F6F9F", accent2: "B5651D", accent3: "2E7D4F", accent4: "8A93A6",
    accent5: "C9DDEE", accent6: "F6E3CF", hlink: "2F6F9F", folHlink: "5B6170",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Compute change in pose (3D) of small objects";
const C = pres.SchemeColor;
const W = 13.333;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.8, fontSize: 44,
      bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.0, w: 11.7, h: 2.2, fontSize: 20,
      color: C.accent5, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 32,
      bold: true, color: C.text1, fontFace: THEME.headFontFace, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "CS6350 · TPA-12 · change in pose of small objects",
      options: { x: 0.6, y: 7.0, w: 8, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
});

let n = 0;
const sec = (title) => pres.addSection({ title });
let current = "";
function slide(title, section) {
  if (section && section !== current) { sec(section); current = section; }
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: current });
  s.addText(title, { placeholder: "title" });
  n += 1;
  return s;
}
const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontSize: 16, color: C.text1,
  valign: "top", margin: 0 }, o));

// numbered circle: the deck's motif
function badge(s, x, y, label, color) {
  s.addShape(pres.shapes.OVAL, { x, y, w: 0.5, h: 0.5, fill: { color: color || C.accent1 }, line: { color: color || C.accent1 },
    objectName: `badge ${label}` });
  s.addText(String(label), { isTextBox: true, x, y, w: 0.5, h: 0.5, fontSize: 16, bold: true, color: C.background1,
    align: "center", valign: "middle", margin: 0 });
}
function card(s, x, y, w, h, fill) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: fill || C.background2 },
    line: { color: fill || C.background2 } });
}
function bullets(items, o) {
  return items.map((t, i) => ({ text: t, options: Object.assign({ bullet: true, breakLine: i < items.length - 1,
    paraSpaceAfter: 6 }, o || {}) }));
}
const tableOpts = (o) => Object.assign({ fontSize: 13, color: C.text1, border: { type: "solid", pt: 0.5, color: HEX.accent5 },
  fill: { color: C.background1 }, margin: [3, 6, 3, 6], valign: "middle" }, o);
const head = (cells) => cells.map((t) => ({ text: t, options: { bold: true, fill: { color: C.accent1 }, color: C.background1 } }));

// ------------------------------------------------------------------ 1 title
sec("Introduction"); current = "Introduction";
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: current });
  s.addText("Compute change in pose (3D) of small objects", { placeholder: "title" });
  s.addText([
    { text: "CS6350 Computer Vision · TPA-12 · Prof. Sukhendu Das", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Sai Svanik Chiramana (ME23B195)  ·  Sathwik Chanduluri (ME23B238)", options: { color: C.background1 } },
  ], { placeholder: "body" });
  s.addNotes("Title. Introduce the team and the task: relative 3D pose of a small object from two RGB photos.");
}

// ------------------------------------------------------------------ 2 task
{
  const s = slide("What the project asks", "Introduction");
  T(s, "Given two RGB photos of the same small object, estimate:", { x: 0.6, y: 1.45, w: 6.2, h: 0.5, fontSize: 18 });
  const rows = [
    ["R", "the 3D rotation between the views"],
    ["t", "the translation direction (scale is not observable from two views)"],
    ["px", "the reprojection error of the matched points"],
  ];
  rows.forEach(([k, v], i) => {
    const y = 2.15 + i * 0.95;
    card(s, 0.6, y, 6.2, 0.8);
    s.addText(k, { isTextBox: true, x: 0.75, y, w: 0.8, h: 0.8, fontSize: 22, bold: true, color: C.accent1,
      fontFace: THEME.headFontFace, valign: "middle", margin: 0 });
    T(s, v, { x: 1.6, y, w: 5.1, h: 0.8, valign: "middle" });
  });
  T(s, [{ text: "X₂ = R X₁ + t", options: { bold: true, breakLine: true } },
    { text: "camera-1 coordinates → camera-2 coordinates (OpenCV axes: x right, y down, z forward)", options: { fontSize: 13, color: C.accent4 } }],
  { x: 0.6, y: 5.1, w: 6.2, h: 0.9, fontSize: 20 });
  T(s, "Our rules: real images only · laptop CPU only · every number on pairs never used for tuning",
    { x: 0.6, y: 6.15, w: 6.2, h: 0.6, fontSize: 14, color: C.accent2, italic: true });
  s.addImage({ path: path.join(FIG, "coin_accurate.jpg"), x: 7.2, y: 1.6, w: 5.5, h: 3.667, altText: "Coin photographed before and after a turn, with matches" });
  T(s, "A coin turned by about 45° on a table: our pipeline matches only points on the coin and recovers 47.2°.",
    { x: 7.2, y: 5.4, w: 5.5, h: 0.8, fontSize: 12, color: C.accent4 });
  s.addNotes("The task: two images in, relative rotation, translation direction and reprojection error out. If the camera is still, R and t are the object's motion; if the object is still, they are the camera's motion. Two views fix t only up to scale.");
}

// ------------------------------------------------------------------ 3 hard
{
  const s = slide("Why small objects are hard", "Introduction");
  const items = [
    ["Small", "The object fills a small part of the image. The background gives most matches, and they describe the background."],
    ["Little texture", "Phone backs, watch faces and dark wallets give keypoint detectors almost nothing."],
    ["Near-planar", "Flat objects make the essential matrix ill-conditioned, and a plane has two valid poses."],
    ["Large viewpoint change", "At 30–60° the object's appearance changes and 2D matchers break down."],
    ["Unknown camera", "Photos handed over at a demo come with no intrinsics and no object annotation."],
  ];
  items.forEach(([h, b], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.6 + col * 4.1, y = 1.55 + row * 2.65;
    card(s, x, y, 3.8, 2.35);
    badge(s, x + 0.25, y + 0.25, i + 1);
    T(s, h, { x: x + 0.9, y: y + 0.25, w: 2.75, h: 0.5, fontSize: 18, bold: true, valign: "middle" });
    T(s, b, { x: x + 0.25, y: y + 0.95, w: 3.35, h: 1.3, fontSize: 14 });
  });
  card(s, 0.6 + 2 * 4.1, 1.55 + 2.65, 3.8, 2.35, C.accent6);
  T(s, "Each problem gets its own fix in the pipeline: cropping, learned matchers, GRIC + planar-twin check, MASt3R, and an automatic front end.",
    { x: 0.6 + 2 * 4.1 + 0.25, y: 1.55 + 2.65 + 0.3, w: 3.35, h: 1.8, fontSize: 14, color: C.text1, italic: true });
  s.addNotes("Five reasons the problem is hard; each maps to a part of the pipeline shown next.");
}

// ------------------------------------------------------------------ 4 pipeline
{
  const s = slide("The pipeline", "Method");
  s.addImage({ path: path.join(FIG, "pipeline.png"), x: 0.6, y: 1.45, w: 12.1, h: 12.1 * 994 / 2675, altText: "Pipeline diagram" });
  T(s, "Blue: the core pipeline behind every benchmark number. Orange: the automatic front end, used only when K and the object region are unknown.",
    { x: 0.6, y: 6.15, w: 12.1, h: 0.6, fontSize: 14, color: C.accent4 });
  s.addNotes("Walk through left to right: crop around the object with a 20% margin and resize to 800 px; match; fit H and E with MAGSAC++; GRIC chooses; decompose with cheirality and the planar-twin check; Levenberg-Marquardt refinement; output R, t direction, reprojection error. The orange boxes fill in K and masks for unknown photos.");
}

// ------------------------------------------------------------------ 5 datasets
{
  const s = slide("Four public real-image datasets", "Data");
  const rows = [
    head(["dataset", "objects", "ground truth", "raw format", "test pairs"]),
    ["TUM RGB-D fr3", "textured posters, checkerboard", "motion capture (metric)", "640×480 frames", "142"],
    ["Objectron", "book, cereal box, laptop", "ARKit poses + 3D boxes (metric)", "phone video (.MOV)", "189"],
    ["CO3Dv2", "cellphone, handbag", "COLMAP poses + masks", "image sequence", "210"],
    ["MVImgNet", "key, watch", "COLMAP poses + cut-out masks", "image sequence", "210"],
  ];
  s.addTable(rows, tableOpts({ x: 0.6, y: 1.5, w: 12.1, colW: [2.2, 3.1, 3.4, 2.2, 1.2], fontSize: 14, rowH: 0.5 }));
  const stats = [["751", "test pairs"], ["339", "tuning pairs"], ["10", "sequences per object (MVImgNet, CO3D, Objectron)"]];
  stats.forEach(([v, l], i) => {
    const x = 0.6 + i * 4.1;
    s.addText(v, { isTextBox: true, x, y: 4.6, w: 3.8, h: 0.9, fontSize: 48, bold: true, color: C.accent1, fontFace: THEME.headFontFace, margin: 0 });
    T(s, l, { x, y: 5.5, w: 3.8, h: 0.6, fontSize: 14, color: C.accent4 });
  });
  T(s, "CO3D and MVImgNet are 90–140 GB per category, so only the needed files were read out of the remote zips with HTTP range requests.",
    { x: 0.6, y: 6.25, w: 12.1, h: 0.5, fontSize: 13, color: C.accent4, italic: true });
  s.addNotes("Four datasets, all real images with ground-truth poses. Small objects: keys, watches, phones. We downloaded only the needed sequences.");
}

// ------------------------------------------------------------------ 6 preprocessing
{
  const s = slide("Preprocessing: raw data to frames with poses", "Data");
  const cols = [
    ["TUM", ["Mocap gives poses at ~100 Hz, RGB comes at ~30 Hz", "Pose interpolated at each frame's timestamp: linear position, slerp rotation", "Whole image is the region (the poster is the scene)"]],
    ["Objectron (video)", ["Parse per-frame ARKit poses, pick pairs first", "Decode the .MOV once; save only chosen frames (JPEG 95)", "Rotate portrait → landscape; ARKit axes → OpenCV", "Mask = hull of the projected 3D box"]],
    ["CO3D", ["10 best sequences per category (viewpoint score)", "PyTorch3D NDC cameras → OpenCV pixel K and R, t", "Dataset masks used as the region"]],
    ["MVImgNet", ["COLMAP model with one radial distortion term", "Images and masks undistorted on load", "Alpha channel of the cut-out = mask"]],
  ];
  cols.forEach(([h, items], i) => {
    const x = 0.6 + i * 3.075, w = 2.85;
    card(s, x, 1.5, w, 4.55);
    badge(s, x + 0.2, 1.7, i + 1);
    T(s, h, { x: x + 0.8, y: 1.7, w: w - 0.9, h: 0.5, fontSize: 17, bold: true, valign: "middle" });
    T(s, bullets(items), { x: x + 0.2, y: 2.4, w: w - 0.35, h: 3.5, fontSize: 14 });
  });
  T(s, "At run time every image is cropped to the object's box + 20% and resized to ≤ 800 px; K is adjusted to match.",
    { x: 0.6, y: 6.25, w: 12.1, h: 0.5, fontSize: 14, color: C.accent2, italic: true });
  s.addNotes("Every dataset is converted to the same form: frames with a world-to-camera pose in OpenCV convention, pixel K and a mask. Objectron is video: we parse the annotation, choose the pairs, then decode the video once and write only the frames we need, rotated back to landscape.");
}

// ------------------------------------------------------------------ 7 protocol
{
  const s = slide("Pairs, split and metric", "Data");
  const items = [
    ["Pairs", ["Fixed seed, stratified by rotation: 5–15°, 15–30°, 30–60°", "R_gt = R₂R₁ᵀ,  t_gt = t₂ − R_gt t₁", "TUM: frames ≤ 3 s apart", "Loader check: matches lie 0.2–3.6 px from GT epipolar lines"]],
    ["Split", ["Tuning: sequences 01–03 (TUM: first 30%)", "All thresholds, cascades and the confidence model fitted there", "Test: everything else, used once"]],
    ["Metric", ["Pose error = max(rotation error, t-direction error)", "AUC@5/10/20: area under the share-solved curve", "Failed pairs count as infinite error", "Also: reprojection error, seconds per pair"]],
  ];
  items.forEach(([h, b], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.5, 3.8, 4.9);
    badge(s, x + 0.25, 1.75, i + 1);
    T(s, h, { x: x + 0.9, y: 1.75, w: 2.7, h: 0.5, fontSize: 18, bold: true, valign: "middle" });
    T(s, bullets(b), { x: x + 0.25, y: 2.5, w: 3.35, h: 3.8, fontSize: 14 });
  });
  s.addNotes("Pairs are stratified by viewpoint change. All tuning on sequences 01-03; all reported numbers on the test pairs. AUC counts failures as infinite error, so refusing hard pairs does not help.");
}

// ------------------------------------------------------------------ 8 matchers
{
  const s = slide("The matchers we compared", "Method");
  const items = [
    ["SIFT", "classical", "Difference-of-Gaussians keypoints, 128-D gradient histograms. Scale and rotation invariant; needs texture."],
    ["XFeat", "learned sparse", "Very light CNN for keypoints and 64-D descriptors, built for CPUs."],
    ["LightGlue", "learned matcher", "Transformer with self- and cross-attention over two keypoint sets; paired with XFeat, ALIKED and DISK."],
    ["LoFTR", "learned dense", "No detector: matches coarse feature maps everywhere with attention, then refines. Works on weak texture."],
    ["MASt3R", "3D foundation model", "ViT-Large regresses a 3D point map for both views and matches in 3D. Most accurate, ~20 s/pair."],
    ["Shape", "outline only", "Fits a quadrilateral to each mask's outline: a homography from 4 corners, for textureless rectangles."],
  ];
  items.forEach(([h, k, b], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.6 + col * 4.1, y = 1.5 + row * 2.6;
    card(s, x, y, 3.8, 2.35);
    T(s, h, { x: x + 0.25, y: y + 0.2, w: 2.0, h: 0.5, fontSize: 20, bold: true, fontFace: THEME.headFontFace, valign: "middle" });
    T(s, k, { x: x + 2.0, y: y + 0.2, w: 1.6, h: 0.5, fontSize: 11, color: C.accent2, align: "right", valign: "middle" });
    T(s, b, { x: x + 0.25, y: y + 0.85, w: 3.35, h: 1.4, fontSize: 14 });
  });
  s.addNotes("SIFT is the classical baseline. XFeat, ALIKED, DISK with LightGlue are learned sparse matchers. LoFTR is dense and detector-free. MASt3R reasons in 3D. Shape handles textureless rectangles from the outline.");
}

// ------------------------------------------------------------------ 9 geometry
{
  const s = slide("From matches to a pose", "Method");
  const steps = [
    ["MAGSAC++", "Fits both a homography H (planar) and an essential matrix E (3D) robustly, without a fixed inlier threshold."],
    ["GRIC", "Torr's criterion scores H and E on the same matches: fit rewarded, complexity penalised. Lower wins."],
    ["Decompose", "Candidates from H or E; cheirality keeps points in front of both cameras; the planar-twin check fixes E's plane ambiguity."],
    ["Refine", "Levenberg–Marquardt on Sampson (E) or transfer error (H); then triangulate and report the RMS reprojection error."],
  ];
  steps.forEach(([h, b], i) => {
    const y = 1.5 + i * 1.2;
    badge(s, 0.6, y + 0.15, i + 1);
    T(s, h, { x: 1.3, y: y + 0.1, w: 2.2, h: 0.6, fontSize: 18, bold: true, valign: "middle" });
    T(s, b, { x: 3.5, y: y + 0.05, w: 4.4, h: 1.05, fontSize: 14 });
  });
  card(s, 8.3, 1.5, 4.4, 4.75);
  T(s, "Which model? (ALIKED+LG, AUC@10)", { x: 8.55, y: 1.7, w: 3.9, h: 0.5, fontSize: 15, bold: true });
  s.addTable([
    head(["model", "all pairs", "far flat posters"]),
    ["H only", "29.9", "55.5"], ["E only", "44.3", "18.6"], [{ text: "GRIC", options: { bold: true } }, { text: "44.9", options: { bold: true } }, "55.5"],
  ], tableOpts({ x: 8.55, y: 2.3, w: 3.9, colW: [1.3, 1.2, 1.4], fontSize: 14, rowH: 0.45 }));
  T(s, "The planar-twin check raised every matcher by 1–3 points, and XFeat+LG on Objectron by 9 (49.3 → 58.2).",
    { x: 8.55, y: 4.5, w: 3.9, h: 1.5, fontSize: 14, italic: true, color: C.text1 });
  s.addNotes("H suits flat objects, E suits 3D objects; GRIC picks per pair and beats both. The planar-twin check fixed E returning the wrong one of the plane's two valid poses.");
}

// ------------------------------------------------------------------ 10 presets
{
  const s = slide("Three presets: fast, accurate, confident", "Method");
  s.addImage({ path: path.join(FIG, "cascades.png"), x: 0.6, y: 1.45, w: 12.1, h: 12.1 * 594 / 2174, altText: "Cascade presets" });
  const items = [
    ["fast", "Stop at the first matcher with enough inliers.", "0.8 s"],
    ["accurate", "Higher inlier bars; LoFTR only when cheaper stages fail.", "1.1 s median, 3.0 s mean"],
    ["confident", "A learned classifier predicts P(error < 10°); below 0.45 the pair goes to MASt3R.", "0.7 s median, 7.8 s mean"],
  ];
  items.forEach(([h, b, t], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 4.95, 3.8, 1.85);
    T(s, h, { x: x + 0.25, y: 5.05, w: 3.3, h: 0.45, fontSize: 18, bold: true, color: C.accent1, fontFace: "Courier New" });
    T(s, b, { x: x + 0.25, y: 5.5, w: 3.35, h: 0.85, fontSize: 14 });
    T(s, t, { x: x + 0.25, y: 6.35, w: 3.35, h: 0.35, fontSize: 12, color: C.accent2 });
  });
  s.addNotes("No matcher wins everywhere, so cascades try methods in order. Order and thresholds were searched exhaustively on the tuning split only (268k designs). Confident uses a gradient-boosted classifier on match statistics to decide when MASt3R is needed; about a quarter of pairs go to it.");
}

// ------------------------------------------------------------------ 11 main result
{
  const s = slide("MASt3R most accurate, confident best trade-off", "Results");
  const labels = ["SIFT", "XFeat+LG", "LoFTR", "fast", "accurate", "confident", "MASt3R"];
  const vals = [35.8, 46.4, 47.5, 48.1, 50.0, 64.0, 73.0];
  s.addChart(pres.charts.BAR, [{ name: "mean AUC@10 (%)", labels, values: vals }], {
    x: 0.6, y: 1.45, w: 7.4, h: 5.3, barDir: "bar", chartColors: [HEX.accent1],
    showTitle: true, title: "Mean AUC@10 over the 4 datasets (%), 751 test pairs", titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 13, catAxisLabelColor: HEX.dk1, catAxisLabelFontFace: "+mn-lt",
    valAxisHidden: true, valAxisMaxVal: 85, valAxisMinVal: 0, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: false, barGapWidthPct: 45,
  });
  const stats = [["73.0", "MASt3R: median rotation error 0.90°, no failures, ~20 s/pair"],
    ["64.0", "confident cascade at a median 0.7 s/pair; only 7% of pairs > 20° off"],
    ["0.29 px", "MASt3R's median reprojection error (others 0.4–0.6 px)"]];
  stats.forEach(([v, l], i) => {
    const y = 1.55 + i * 1.75;
    s.addText(v, { isTextBox: true, x: 8.4, y, w: 4.3, h: 0.85, fontSize: 44, bold: true, color: i === 1 ? C.accent2 : C.accent1, fontFace: THEME.headFontFace, margin: 0 });
    T(s, l, { x: 8.4, y: y + 0.85, w: 4.3, h: 0.8, fontSize: 14 });
  });
  s.addNotes("Per-dataset numbers are in the report. Cascades beat every single 2D matcher; accurate beats LoFTR at a sixth of its time. MASt3R's gain on MVImgNet, which it never saw, is as large as on CO3D, so it is not memorisation.");
}

// ------------------------------------------------------------------ 12 viewpoint
{
  const s = slide("Large viewpoint changes break 2D matchers, not MASt3R", "Results");
  const labels = ["5–15°", "15–30°", "30–60°"];
  s.addChart(pres.charts.BAR, [
    { name: "SIFT", labels, values: [40.2, 35.7, 19.2] },
    { name: "XFeat+LG", labels, values: [47.1, 52.6, 30.3] },
    { name: "LoFTR", labels, values: [53.4, 52.3, 26.1] },
    { name: "MASt3R", labels, values: [68.3, 76.5, 72.4] },
  ], {
    x: 0.6, y: 1.45, w: 7.6, h: 5.3, barDir: "col", barGrouping: "clustered",
    chartColors: [HEX.accent4, HEX.accent5, HEX.accent1, HEX.accent2],
    showTitle: true, title: "AUC@10 (%) by true rotation between the views", titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 13, catAxisLabelColor: HEX.dk1, catAxisLabelFontFace: "+mn-lt",
    valAxisLabelFontSize: 11, valAxisLabelColor: HEX.accent4, valAxisLabelFontFace: "+mn-lt", valAxisMaxVal: 90,
    valGridLine: { color: "E3E7EE", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
  });
  card(s, 8.6, 1.5, 4.1, 5.2);
  T(s, [
    { text: "Object only vs whole image", options: { bold: true, breakLine: true, fontSize: 16 } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "Using the whole image raises ALIKED+LG on MVImgNet from 33 to 75 AUC.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true, fontSize: 8 } },
    { text: "But that measures the camera against a static background, not the object. If the object is moved by hand, it fails. All main results are therefore object only.", options: {} },
  ], { x: 8.85, y: 1.75, w: 3.6, h: 4.8, fontSize: 14 });
  s.addNotes("Between 30 and 60 degrees every 2D matcher drops to 19-32 AUC; MASt3R stays at 72 because it reasons in 3D.");
}

// ------------------------------------------------------------------ 13 sensitivity
{
  const s = slide("How exact must the camera intrinsics be?", "Results");
  const stats = [
    ["−1", "AUC point for a ±2% focal-length error"],
    ["−6", "AUC points for a ±10% focal-length error"],
    ["−8", "AUC points for a principal point off by 5% of the image"],
    ["2.3%", "focal error of our Zhang calibration on TUM's checkerboard"],
  ];
  stats.forEach(([v, l], i) => {
    const x = 0.6 + (i % 2) * 3.2, y = 1.55 + Math.floor(i / 2) * 2.3;
    card(s, x, y, 3.0, 2.05);
    s.addText(v, { isTextBox: true, x: x + 0.2, y: y + 0.15, w: 2.6, h: 0.9, fontSize: 40, bold: true, color: i === 3 ? C.accent3 : C.accent2, fontFace: THEME.headFontFace, margin: 0 });
    T(s, l, { x: x + 0.2, y: y + 1.05, w: 2.6, h: 0.9, fontSize: 14 });
  });
  s.addImage({ path: path.join(FIG, "focal_sens.png"), x: 7.2, y: 1.55, w: 5.5, h: 5.5 * 600 / 900, altText: "AUC against focal error" });
  T(s, "Metric scale: with a known object length, |t| comes out with a median error of 18% (Objectron).",
    { x: 7.2, y: 5.4, w: 5.5, h: 0.9, fontSize: 14, italic: true });
  s.addNotes("Same matches, deliberately wrong K. Focal errors of a few percent are cheap; principal-point errors cost more. A low calibration reprojection error alone does not prove a good K: a K 28% off reprojected almost as well, because the board was seen face-on.");
}

// ------------------------------------------------------------------ 14 blind
{
  const s = slide("Blind setting: photos with no K and no mask", "Results");
  T(s, "For a live demo: focal length estimated from MASt3R's 3D point map, the object found by SAM 2.1 segments plus motion and change rules.",
    { x: 0.6, y: 1.45, w: 12.1, h: 0.7, fontSize: 16 });
  s.addTable([
    head(["version (MASt3R pose, AUC@10 %)", "TUM (20)", "Objectron (15)", "CO3D (16)"]),
    ["A  dataset K, dataset region", "76.4", "84.8", "67.9"],
    ["B  estimated focal, dataset region", "71.7", "80.3", "61.0"],
    [{ text: "D  estimated focal, automatic region", options: { bold: true } }, { text: "71.7", options: { bold: true } }, { text: "80.4", options: { bold: true } }, { text: "74.8", options: { bold: true } }],
    ["focal estimate: median |error|", "4.4%", "3.2%", "3.0%"],
  ], tableOpts({ x: 0.6, y: 2.35, w: 12.1, colW: [5.5, 2.2, 2.2, 2.2], fontSize: 15, rowH: 0.55 }));
  card(s, 0.6, 5.5, 12.1, 1.2, C.accent6);
  T(s, "Fully automatic costs only 4–5 AUC points on TUM and Objectron. On CO3D it gains, because the found region includes surroundings that move with the camera.",
    { x: 0.85, y: 5.65, w: 11.6, h: 0.95, fontSize: 15 });
  s.addNotes("A uses everything the dataset provides. B only estimates the focal length. D also finds the object automatically, with no name given. These runs used the region finder before the change rule was added.");
}

// ------------------------------------------------------------------ 15 own photos
{
  const s = slide("Our own photos: SIFT wins on large in-plane turns", "Results");
  s.addImage({ path: path.join(FIG, "key_accurate.jpg"), x: 0.6, y: 1.5, w: 5.4, h: 3.6, altText: "Key before and after a turn with matches" });
  T(s, "Key turned ~55–60°: found by the change rule; accurate gives 50°.", { x: 0.6, y: 5.15, w: 5.4, h: 0.6, fontSize: 12, color: C.accent4 });
  s.addTable([
    head(["object", "true turn", "accurate", "mast3r"]),
    ["coin", "≈ 45°", { text: "47.2°", options: { bold: true, color: C.accent3 } }, "18.1°"],
    ["key", "≈ 55–60°", { text: "50°", options: { bold: true, color: C.accent3 } }, "16.8°"],
    ["wallet", "≈ 45°", "–", { text: "40.6°", options: { bold: true, color: C.accent3 } }],
    ["mouse", "≈ 60°", "7°", "13°"],
  ], tableOpts({ x: 6.4, y: 1.5, w: 6.3, colW: [1.5, 1.7, 1.55, 1.55], fontSize: 15, rowH: 0.5 }));
  T(s, bullets([
    "MASt3R pairs points as if the object barely turned; rotation-invariant SIFT follows the turn.",
    "Both answers have sub-pixel reprojection error, so that number cannot tell them apart.",
    "The rotation axis can: the coin's SIFT axis (0.00, −0.49, −0.87) is the table's normal; MASt3R's is the camera x axis.",
    "Mouse: region not found, so the whole image measured the camera's motion.",
  ]), { x: 6.4, y: 4.2, w: 6.3, h: 2.6, fontSize: 14 });
  s.addNotes("iPhone photos without EXIF; focal from the 35 mm equivalent (about 1110 px) or the MASt3R estimate. Ground truth is only the approximate angle we turned the object by hand.");
}

// ------------------------------------------------------------------ 16 conclusion
sec("Conclusion"); current = "Conclusion";
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: current });
  s.addText("Conclusion", { placeholder: "title" });
  s.addText([
    { text: "MASt3R: AUC@10 73.0, 0.90° median rotation error; confident cascade: 64.0 at 0.7 s", options: { bullet: true, breakLine: true } },
    { text: "GRIC + planar-twin check handles flat and 3D objects", options: { bullet: true, breakLine: true } },
    { text: "Unknown photos: automatic focal and region cost only 4–5 points", options: { bullet: true, breakLine: true } },
    { text: "Limits: no scale without object size; textureless objects; MASt3R misses large in-plane turns", options: { bullet: true } },
  ], { placeholder: "body", fontSize: 18, paraSpaceAfter: 8 });
  s.addNotes("Summary and limitations. Next step: run both a rotation-invariant matcher and MASt3R and keep the answer whose rotation axis matches the supporting surface.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  if (SKILL) {
    const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));
    await applyTheme(OUT, THEME);
  }
  console.log("written", OUT, n + 2, "slides");
})();
