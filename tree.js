const gsap = window.gsap;
const dat = window.dat;

const svgNS = "http://www.w3.org/2000/svg";
const svg = document.getElementById("tree-svg");

const params = {
  depth: 6,
  branchFactor: 2,
  length: 100,
  thickness: 5,
  color: "#8B5A2B",
  animate: true,
  random: false,
};

const gui = new dat.GUI();
gui.add(params, "depth", 1, 10, 1).name("Profondeur").onChange(drawTree);
gui.add(params, "branchFactor", 1, 4, 1).name("Branches").onChange(drawTree);
gui.add(params, "length", 50, 200, 1).name("Longueur").onChange(drawTree);
gui.add(params, "thickness", 1, 10, 1).name("Épaisseur").onChange(drawTree);
gui.addColor(params, "color").name("Couleur").onChange(drawTree);
gui.add(params, "animate").name("Animation");
gui.add(params, "random").name("Aléatoire").onChange(drawTree);

drawTree();

function drawTree() {
  svg.innerHTML = "";
  generateBranch(svg, window.innerWidth / 2, window.innerHeight, -90, params.length, params.depth);
}

function generateBranch(parent, x, y, angle, length, depth) {
  if (depth === 0) return;

  const randomFactor = params.random ? (Math.random() * 0.5 + 0.75) : 1;
  const x2 = x + length * randomFactor * Math.cos(angle * Math.PI / 180);
  const y2 = y + length * randomFactor * Math.sin(angle * Math.PI / 180);

  const line = document.createElementNS(svgNS, "line");
  line.setAttribute("x1", x);
  line.setAttribute("y1", y);
  line.setAttribute("x2", x2);
  line.setAttribute("y2", y2);
  line.setAttribute("stroke", params.color);
  line.setAttribute("stroke-width", params.thickness * (depth / params.depth));
  line.setAttribute("stroke-linecap", "round");
  parent.appendChild(line);

  if (params.animate) {
    gsap.from(line, { duration: 0.5, opacity: 0, scaleY: 0, ease: "power2.out" });
  }

  for (let i = 0; i < params.branchFactor; i++) {
    const newAngle = angle + (i % 2 === 0 ? -90 : 90);
    generateBranch(parent, x2, y2, newAngle, length * 0.75 * randomFactor, depth - 1);
  }
}