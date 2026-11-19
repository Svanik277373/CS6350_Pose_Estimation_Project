// Builds report/final/slides.pptx (16:9): presentation of the two-image pipeline (report/final/main.pdf).
//   NODE_PATH=<folder with node_modules containing pptxgenjs> PPTX_SKILL=<pptx skill dir> node report/final/slides.js
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
pres.author = "Sai Svanik Chiramana, Sathwik Chanduluri";
const C = pres.SchemeColor;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.9, w: 11.7, h: 1.9, fontSize: 42,
      bold: true, color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.0, w: 11.7, h: 2.6, fontSize: 20,
      color: C.accent5, valign: "top" }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 30,
      bold: true, color: C.text1, fontFace: THEME.headFontFace, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "CS6350 Computer Vision · TPA-12 · Compute change in pose (3D) of small objects",
      options: { x: 0.6, y: 7.0, w: 9, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
});

let n = 0;
let current = "";
function slide(title, section) {
  if (section !== current) { pres.addSection({ title: section }); current = section; }
  const s = pres.addSlide({ masterName: "CONTENT", sectionTitle: current });
  s.addText(title, { placeholder: "title" });
  n += 1;
  return s;
}
const T = (s, text, o) => s.addText(text, Object.assign({ isTextBox: true, fontSize: 16, color: C.text1,
  valign: "top", margin: 0 }, o));
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
const img = (s, file, x, y, w, aspect, alt) => s.addImage({ path: path.join(FIG, file), x, y, w, h: w / aspect, altText: alt });
const stat = (s, x, y, w, value, label, color) => {
  s.addText(value, { isTextBox: true, x, y, w, h: 0.8, fontSize: 38, bold: true, color: color || C.accent1,
    fontFace: THEME.headFontFace, margin: 0 });
  T(s, label, { x, y: y + 0.8, w, h: 0.75, fontSize: 13 });
};

// ------------------------------------------------------------------ 1 title
pres.addSection({ title: "Introduction" }); current = "Introduction";
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: current });
  s.addText("Compute change in pose (3D) of small objects", { placeholder: "title" });
  s.addText([
    { text: "CS6350 Computer Vision · TPA-12 · Prof. Sukhendu Das", options: { breakLine: true } },
    { text: "Indian Institute of Technology Madras", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Sai Svanik Chiramana (ME23B195)  ·  Sathwik Chanduluri (ME23B238)", options: { color: C.background1 } },
  ], { placeholder: "body" });
  s.addNotes("Title. The task is to estimate the change in 3D pose of a small object from two images, with nothing else given.");
}

// ------------------------------------------------------------------ 2 problem
{
  const s = slide("Problem statement", "Introduction");
  T(s, "Input: two RGB images of a small object from arbitrary viewpoints. Nothing else: no camera intrinsics, no mask, no object name.",
    { x: 0.6, y: 1.45, w: 6.3, h: 0.9, fontSize: 17 });
  const rows = [["R", "relative rotation between the two views"], ["t", "relative translation (direction; scale needs the object's size)"],
    ["ε", "reprojection error metrics indicating accuracy"]];
  rows.forEach(([k, v], i) => {
    const y = 2.5 + i * 0.95;
    card(s, 0.6, y, 6.3, 0.8);
    s.addText(k, { isTextBox: true, x: 0.75, y, w: 0.8, h: 0.8, fontSize: 24, bold: true, color: C.accent1,
      fontFace: THEME.headFontFace, valign: "middle", margin: 0 });
    T(s, v, { x: 1.6, y, w: 5.2, h: 0.8, valign: "middle" });
  });
  T(s, [{ text: "X₂ = R X₁ + t", options: { bold: true, breakLine: true } },
    { text: "a point in camera-1 coordinates mapped to camera-2 coordinates", options: { fontSize: 13, color: C.accent4 } }],
  { x: 0.6, y: 5.45, w: 6.3, h: 0.9, fontSize: 20 });
  img(s, "datasets.png", 7.2, 1.6, 5.5, 2244 / 944, "One test pair from each of the four datasets");
  T(s, "Objects named in the task (key, mobile phone, purse, clock, checkerboard) are evaluated on four public datasets with ground-truth poses.",
    { x: 7.2, y: 4.1, w: 5.5, h: 0.9, fontSize: 13, color: C.accent4 });
  s.addNotes("The outputs required by TPA-12: rotation, translation and reprojection error metrics. From two views translation is known only up to scale, so its direction is estimated. Only the two images are available, which is the setting of this work.");
}

// ------------------------------------------------------------------ 3 hard
{
  const s = slide("Why the problem is difficult", "Introduction");
  const items = [
    ["Small object", "Most correspondences lie on the background and describe its motion, not the object's."],
    ["Weak texture", "Phone backs, watch faces and metal keys give keypoint detectors little to work with."],
    ["Near-planar", "The essential matrix is ill-conditioned on a plane, and a plane admits two valid poses."],
    ["Large viewpoint change", "Beyond 30–60° local appearance changes and 2D matchers break down."],
    ["Nothing else given", "The focal length and the object's location must be estimated from the images."],
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
  T(s, "Each difficulty is addressed by one stage: region finding, a 3D-aware matcher, GRIC with a planar-twin check, and focal estimation.",
    { x: 0.6 + 2 * 4.1 + 0.25, y: 1.55 + 2.65 + 0.3, w: 3.35, h: 1.8, fontSize: 14, italic: true });
  s.addNotes("Five sources of difficulty; the following slides show the stage that addresses each.");
}

// ------------------------------------------------------------------ 4 pipeline
{
  const s = slide("The two-image pipeline", "Method");
  img(s, "pipeline.png", 0.6, 1.6, 12.1, 2772 / 823, "Pipeline diagram");
  T(s, bullets([
    "Front end (orange): estimate what is not given, the focal length and the object region.",
    "Pose estimation (blue): correspondences on the object → H and E → GRIC → decomposition → refinement.",
    "Output: R, the direction of t, the RMS reprojection error and a verdict.",
  ]), { x: 0.6, y: 5.35, w: 12.1, h: 1.5, fontSize: 15 });
  s.addNotes("Overview of the pipeline, left to right and then along the second row. Each stage is explained on the next slides.");
}

// ------------------------------------------------------------------ 5 focal + region
{
  const s = slide("Front end: focal length and object region", "Method");
  const cols = [
    ["Focal length", ["MASt3R predicts a 3D point for every pixel", "Pinhole model: u − cₓ = f·X/Z, so every pixel votes for f", "Robust combination by Weiszfeld's algorithm", "Median error on the test pairs: 6%"]],
    ["SAM 2.1 segments", ["Hiera encoder once per image; two-way decoder per prompt", "12 × 12 grid of point prompts, no class name", "Drop segments touching the border or of the wrong size"]],
    ["Which segment moved?", ["Motion rule: its matches break the background's epipolar geometry (F, MAGSAC++)", "Change rule: after warping out the background's motion it no longer aligns (NCC)", "Otherwise: static scene, use the whole images"]],
  ];
  cols.forEach(([h, items], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 1.5, 3.8, 4.55);
    badge(s, x + 0.25, 1.7, i + 1);
    T(s, h, { x: x + 0.9, y: 1.7, w: 2.8, h: 0.5, fontSize: 17, bold: true, valign: "middle" });
    T(s, bullets(items), { x: x + 0.25, y: 2.4, w: 3.35, h: 3.55, fontSize: 14 });
  });
  T(s, "The change rule alone is accepted only for segments ≥ 0.5% of the image (chosen on the tuning split: AUC@10 65.8 → 77.6).",
    { x: 0.6, y: 6.25, w: 12.1, h: 0.5, fontSize: 14, color: C.accent2, italic: true });
  s.addNotes("The focal length comes from MASt3R's point map with a robust fit. SAM 2.1 proposes class-free segments; the motion rule and the change rule identify the segment that moved relative to the background. If nothing moved, the camera's motion relative to the scene equals its motion relative to the object, so the whole images are used.");
}

// ------------------------------------------------------------------ 6 matching
{
  const s = slide("Correspondences on the object", "Method");
  const items = [
    ["MASt3R", "3D foundation model", "Shared ViT encoder, cross-attending decoders; a 3D point and a descriptor per pixel, matched as mutual nearest neighbours. Default."],
    ["SIFT", "classical", "Difference-of-Gaussians keypoints, 128 gradient histograms; scale- and rotation-invariant."],
    ["XFeat + LightGlue", "learned sparse", "Light CNN keypoints matched by a transformer with self- and cross-attention."],
    ["LoFTR", "learned dense", "No detector: coarse cells matched with attention and dual softmax, refined to sub-pixel."],
    ["accurate", "cascade", "XFeat+LG → outline → SIFT → LoFTR, accepting the first with enough inliers."],
    ["confident", "cascade", "Cheap stages accepted only if a learned P(error < 10°) ≥ 0.45, otherwise MASt3R."],
  ];
  items.forEach(([h, k, b], i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const x = 0.6 + col * 4.1, y = 1.5 + row * 2.6;
    card(s, x, y, 3.8, 2.35, i === 0 ? C.accent5 : undefined);
    T(s, h, { x: x + 0.25, y: y + 0.2, w: 2.3, h: 0.5, fontSize: 19, bold: true, fontFace: THEME.headFontFace, valign: "middle" });
    T(s, k, { x: x + 2.4, y: y + 0.2, w: 1.2, h: 0.5, fontSize: 11, color: C.accent2, align: "right", valign: "middle" });
    T(s, b, { x: x + 0.25, y: y + 0.85, w: 3.35, h: 1.4, fontSize: 14 });
  });
  s.addNotes("Images are cropped to the object's box plus 20% before matching, so the object fills the matcher's input. MASt3R is the default; the other matchers and the two cascades are compared in the results.");
}

// ------------------------------------------------------------------ 7 geometry
{
  const s = slide("From correspondences to the pose", "Method");
  const steps = [
    ["MAGSAC++", "Fits a homography H (planar, 4-point) and an essential matrix E (any rigid object, Nistér 5-point) without a fixed inlier threshold."],
    ["GRIC", "E always fits at least as well as H; GRIC penalises each model's freedom, so E is chosen only if it fits clearly better."],
    ["Decompose", "Four candidates from E, the cheirality test keeps one; H's two plane solutions separated by off-plane points; planar-twin check on E."],
    ["Refine", "Levenberg–Marquardt on all inliers (Sampson or transfer error), then inlier re-selection; RMS reprojection error reported."],
  ];
  steps.forEach(([h, b], i) => {
    const y = 1.5 + i * 1.2;
    badge(s, 0.6, y + 0.15, i + 1);
    T(s, h, { x: 1.3, y: y + 0.1, w: 2.0, h: 0.6, fontSize: 18, bold: true, valign: "middle" });
    T(s, b, { x: 3.3, y: y + 0.05, w: 4.7, h: 1.05, fontSize: 14 });
  });
  card(s, 8.4, 1.5, 4.3, 4.75);
  T(s, "Model choice (fixed correspondences, AUC@10)", { x: 8.65, y: 1.7, w: 3.8, h: 0.5, fontSize: 14, bold: true });
  s.addTable([
    head(["model", "all pairs", "far flat posters"]),
    ["H only", "29.9", "55.5"], ["E only", "44.3", "18.6"], [{ text: "GRIC", options: { bold: true } }, { text: "44.9", options: { bold: true } }, "55.5"],
  ], tableOpts({ x: 8.65, y: 2.3, w: 3.8, colW: [1.2, 1.2, 1.4], fontSize: 14, rowH: 0.45 }));
  T(s, "The planar-twin check raised every matcher's AUC@10 by 1–3 points.", { x: 8.65, y: 4.5, w: 3.8, h: 1.2, fontSize: 14, italic: true });
  s.addNotes("The homography suits flat objects and the essential matrix suits 3D objects; GRIC chooses per pair. The decomposition resolves the two-fold ambiguity of a plane, which matters for the coins, keys, phones and checkerboards named in the task.");
}

// ------------------------------------------------------------------ 8 data
{
  const s = slide("Datasets and test design", "Evaluation");
  s.addTable([
    head(["dataset", "objects / scenes", "ground truth"]),
    ["TUM RGB-D", "2 poster scenes, 2 3D structures, checkerboard", "motion capture"],
    ["Objectron", "book, laptop, cereal box", "AR-tracked phone video"],
    ["CO3D", "mobile phone, handbag", "structure from motion"],
    ["MVImgNet", "key, watch", "structure from motion"],
  ], tableOpts({ x: 0.6, y: 1.5, w: 7.4, colW: [1.7, 3.6, 2.1], fontSize: 14, rowH: 0.5 }));
  stat(s, 0.6, 4.4, 2.3, "56", "held-out test pairs");
  stat(s, 3.1, 4.4, 2.3, "12", "objects and scenes, 7 near-planar");
  stat(s, 5.6, 4.4, 2.4, "<1–90°", "viewpoint change");
  card(s, 8.4, 1.5, 4.3, 4.9);
  T(s, [{ text: "Test groups", options: { bold: true, breakLine: true, fontSize: 16 } }, { text: " ", options: { breakLine: true, fontSize: 6 } }]
    .concat(bullets(["32 pairs: one per object and bin (5–15°, 15–30°, 30–60°)", "10 consecutive TUM frames (< 1°)", "14 pairs at 60–90°",
      "Every threshold set on tuning sequences only", "Metric: max(rotation error, translation-direction error); AUC@5/10/20 with failures as infinite error"])),
  { x: 8.65, y: 1.7, w: 3.85, h: 4.6, fontSize: 14 });
  s.addNotes("Ground truth from four public datasets, converted to the OpenCV convention and checked against epipolar geometry. The test pairs were never used to choose any parameter.");
}

// ------------------------------------------------------------------ 9 worked example
{
  const s = slide("Worked example: every stage on one pair", "Results");
  img(s, "case_planar.jpg", 0.6, 1.4, 7.35, 2146 / 1549, "Nine-panel stage figure for a TUM poster pair");
  T(s, bullets([
    "TUM poster scene, true rotation 22.0°",
    "SAM 2.1 candidates all follow the background (panels 3–4): static scene, whole images used",
    "MASt3R correspondences, GRIC model choice, decomposition and refinement",
    "Rotation error 1.68°, reprojection error 0.17 px",
    "Only the two images were used; the focal length was estimated",
  ]), { x: 8.25, y: 1.6, w: 4.45, h: 5.0, fontSize: 15 });
  s.addNotes("Walk through the nine panels: input, segments, motion rule, change rule, region, crops, matches, inliers and reprojection error vectors with the final numbers.");
}

// ------------------------------------------------------------------ 10 main result
{
  const s = slide("MASt3R gives the most accurate pose", "Results");
  const labels = ["SIFT", "XFeat+LG", "LoFTR", "accurate", "confident", "MASt3R"];
  s.addChart(pres.charts.BAR, [{ name: "AUC@10 (%)", labels, values: [46.4, 46.6, 46.7, 48.5, 66.1, 69.0] }], {
    x: 0.6, y: 1.45, w: 7.2, h: 5.3, barDir: "bar", chartColors: [HEX.accent1],
    showTitle: true, title: "AUC@10 (%), 46 test pairs ≥ 5°, two images only", titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 13, catAxisLabelColor: HEX.dk1, catAxisLabelFontFace: "+mn-lt",
    valAxisHidden: true, valAxisMaxVal: 80, valAxisMinVal: 0, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: false, barGapWidthPct: 45,
  });
  stat(s, 8.2, 1.55, 4.5, "0.97°", "median rotation error (MASt3R, all 56 pairs)");
  stat(s, 8.2, 3.15, 4.5, "1.79°", "median translation-direction error", C.accent2);
  stat(s, 8.2, 4.75, 4.5, "57.5 vs 58.5", "AUC@10: two images only vs given true camera and mask", C.accent3);
  s.addNotes("With only the two images, MASt3R is within one AUC point of the same estimator given the true intrinsics and object mask, so estimating the focal length and finding the object cost almost nothing on average. The confident cascade comes close at a fraction of the matching time.");
}

// ------------------------------------------------------------------ 11 viewpoint
{
  const s = slide("Accuracy across viewpoint changes", "Results");
  const labels = ["< 1°", "5–15°", "15–30°", "30–60°", "60–90°"];
  s.addChart(pres.charts.BAR, [
    { name: "MASt3R", labels, values: [7.4, 70.9, 80.3, 68.8, 65.2] },
    { name: "confident", labels, values: [7.4, 72.3, 71.3, 59.5, 67.8] },
    { name: "accurate", labels, values: [0.0, 68.2, 71.3, 53.0, 17.2] },
  ], {
    x: 0.6, y: 1.45, w: 7.8, h: 5.3, barDir: "col", barGrouping: "clustered",
    chartColors: [HEX.accent1, HEX.accent2, HEX.accent4],
    showTitle: true, title: "AUC@10 (%) by true rotation between the views", titleFontSize: 14, titleColor: HEX.dk1, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 13, catAxisLabelColor: HEX.dk1, catAxisLabelFontFace: "+mn-lt",
    valAxisLabelFontSize: 11, valAxisLabelColor: HEX.accent4, valAxisLabelFontFace: "+mn-lt", valAxisMaxVal: 100,
    valGridLine: { color: "E3E7EE", size: 0.5 }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 12, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
  });
  card(s, 8.8, 1.5, 3.9, 5.2);
  T(s, bullets([
    "MASt3R's median rotation error grows only from 0.76° (5–15°) to 3.08° (60–90°).",
    "The 2D cascade fails on most pairs beyond 60°.",
    "Consecutive frames: rotation is accurate (0.32°), but with a millimetre baseline the translation direction is not observable, so AUC is low for every method.",
  ]), { x: 9.05, y: 1.75, w: 3.4, h: 4.8, fontSize: 14 });
  s.addNotes("The pose error is the larger of the rotation and translation errors, which explains the low AUC on consecutive frames: the rotation is excellent but the translation direction cannot be measured over such a short baseline.");
}

// ------------------------------------------------------------------ 12 euler track
{
  const s = slide("Roll, pitch and yaw along a sequence", "Results");
  img(s, "euler_struct_near_gap20.png", 0.6, 1.4, 6.0, 1800 / 1600, "Roll, pitch and yaw against ground truth");
  T(s, "38 TUM pairs 20 frames apart, each solved from the two images only.", { x: 7.0, y: 1.5, w: 5.7, h: 0.7, fontSize: 15 });
  s.addTable([
    head(["per-axis error", "MAE", "MAX"]),
    ["roll", "0.43°", "8.48°"], ["pitch", "0.34°", "3.84°"], ["yaw", "0.19°", "0.75°"],
    ["translation direction", "8.44°", "57.7°"], ["reprojection RMS", "0.21 px", "0.33 px"],
  ], tableOpts({ x: 7.0, y: 2.35, w: 5.7, colW: [2.7, 1.5, 1.5], fontSize: 14, rowH: 0.45 }));
  T(s, "The estimates follow the ground truth closely; the largest deviation is one roll error of 8.5° at pair 30.",
    { x: 7.0, y: 5.4, w: 5.7, h: 0.9, fontSize: 14, italic: true });
  s.addNotes("Frame-wise comparison in roll, pitch and yaw. The XYZ Euler convention is used only for presentation; the geodesic rotation error is used elsewhere.");
}

// ------------------------------------------------------------------ 13 method comparison
{
  const s = slide("Where each method wins", "Results");
  img(s, "methods.jpg", 0.6, 1.4, 9.15, 2622 / 1527, "Method comparison on four pairs");
  T(s, bullets([
    "MASt3R: keys with weak texture where 2D matchers fail",
    "confident: defers to MASt3R on a similar pair",
    "accurate: its outline stage on a laptop when correspondences mislead",
    "LoFTR: the checkerboard pair where the region pairing misleads MASt3R",
    "No pair met the criterion for SIFT or XFeat+LightGlue alone",
  ]), { x: 10.0, y: 1.5, w: 2.75, h: 5.3, fontSize: 12.5 });
  s.addNotes("Each row is a pair on which the framed method is clearly best: at most 5 degrees, and every other method at least twice and 3 degrees worse. Green correspondences mean a rotation error below 5 degrees.");
}

// ------------------------------------------------------------------ 14 failure + reliability
{
  const s = slide("Failure case and reliability of the output", "Results");
  img(s, "case_failure.jpg", 0.6, 1.4, 7.35, 2131 / 1548, "Nine-panel figure of the failure case");
  T(s, [{ text: "Failure: wrong region pairing", options: { bold: true, breakLine: true } }]
    .concat(bullets(["Strip right of the board paired with the strip left of it", "Pose 61.7° wrong, reprojection error only 0.49 px"], { breakLine: true })),
  { x: 8.25, y: 1.5, w: 4.45, h: 2.0, fontSize: 14 });
  card(s, 8.25, 3.7, 4.45, 2.95, C.accent6);
  T(s, [{ text: "A better indicator", options: { bold: true, breakLine: true } },
    { text: "When MASt3R and the accurate cascade agree within 2° (34 of 56 pairs), no MASt3R rotation is more than 10° off; when they disagree, 14% are.", options: {} }],
  { x: 8.5, y: 3.9, w: 4.0, h: 2.6, fontSize: 14 });
  s.addNotes("A low reprojection error shows only that the pose is self-consistent. Agreement between two independent matchers is a much stronger indication of a correct rotation.");
}

// ------------------------------------------------------------------ 15 conclusion
pres.addSection({ title: "Conclusion" }); current = "Conclusion";
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: current });
  s.addText("Conclusion", { placeholder: "title" });
  s.addText([
    { text: "Two images only: median rotation error 0.97°, translation direction 1.79°, reprojection 0.46 px", options: { bullet: true, breakLine: true } },
    { text: "Within one AUC point of the estimator given the true camera and object mask", options: { bullet: true, breakLine: true } },
    { text: "Robust to 90° viewpoint change; GRIC and the planar-twin check handle flat objects", options: { bullet: true, breakLine: true } },
    { text: "Limits: region pairing in static scenes, translation over very short baselines, close-up focal estimates", options: { bullet: true } },
  ], { placeholder: "body", fontSize: 18, paraSpaceAfter: 8 });
  s.addNotes("Summary of results and limitations. Future work: use agreement between independent matchers in the verdict, and track the object region jointly across both images.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  if (SKILL) {
    const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));
    await applyTheme(OUT, THEME);
  }
  console.log("written", OUT, n + 2, "slides");
})();
