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
  svg.innerHTML = ""; // Réinitialiser le SVG avant chaque dessin
  // Position de départ au centre de l'écran, avec une direction vers la droite (angle 0)
  generateBranch(svg, 500, 500, 0, params.length, params.depth);
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
  line.setAttribute("stroke-width", params.thickness);  // Épaisseur constante
  line.setAttribute("stroke-linecap", "round");
  parent.appendChild(line);

  if (params.animate) {
    gsap.from(line, { duration: 0.5, opacity: 0, scaleY: 0, ease: "power2.out" });
  }

  // Si le paramètre 'random' est activé, choisir un nombre de branches aléatoire entre 1 et 3
  const branchCount = params.random ? Math.floor(Math.random() * 3) + 1 : params.branchFactor;

  for (let i = 0; i < branchCount; i++) {
    let newAngle;
    if (angle === 0) {
      // Si l'angle précédent est 0, on génère des branches à gauche et à droite
      newAngle = (i === 0) ? -90 : 90;  // À gauche ou à droite
    } else if (angle === -90) {
      // Si l'angle précédent est -90, la branche suivante peut aller à droite (0) ou à gauche (90)
      newAngle = (i === 0) ? 0 : -90;
    } else if (angle === 90) {
      // Si l'angle précédent est 90, la branche suivante peut aller à gauche (0) ou à droite (-90)
      newAngle = (i === 0) ? 0 : 90;
    }

    // Calcul de la longueur de la branche entre 0.4 et 1.5 de la longueur du parent
    const newLength = length * (0.4 + Math.random() * 1.1); // Entre 0.4 et 1.5

    // Appel récursif pour générer la branche suivante avec l'angle et la longueur calculés
    generateBranch(parent, x2, y2, newAngle, newLength, depth - 1);
  }
}
