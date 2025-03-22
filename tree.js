document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("tree-container");
  const regenerateButton = document.getElementById("regenerate-btn");

  let svgNamespace = "http://www.w3.org/2000/svg";
  let treeColor = "#3498db"; // Couleur personnalisable de l'arborescence
  let maxDepth = 5; // Profondeur maximale de l'arborescence
  let maxChildren = 3; // Nombre maximum d'enfants par noeud
  let width = window.innerWidth; // Largeur de la page
  let horizontalSpacing = 150; // Espacement horizontal entre les nœuds
  let verticalSpacing = 100; // Espacement vertical entre les nœuds

  // Fonction pour générer une position horizontale et verticale pour chaque point
  function generatePosition(depth, parentX = 0, parentY = 0, isLeftChild = true) {
    // On change la direction de l'arborescence : horizontal puis vertical (angle droit)
    let x = parentX;
    let y = parentY;

    if (isLeftChild) {
      x += Math.random() * horizontalSpacing; // Position aléatoire à gauche
    } else {
      x -= Math.random() * horizontalSpacing; // Position aléatoire à droite
    }

    y += verticalSpacing; // Ajout de l'espacement vertical pour chaque niveau

    return { x, y };
  }

  // Fonction pour dessiner une ligne (edge) entre deux points
  function drawLine(x1, y1, x2, y2) {
    let line = document.createElementNS(svgNamespace, "line");
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x2);
    line.setAttribute("y2", y2);
    line.setAttribute("stroke", treeColor);
    line.setAttribute("stroke-width", 2);
    return line;
  }

  // Fonction pour dessiner un point (node)
  function drawNode(x, y) {
    let circle = document.createElementNS(svgNamespace, "circle");
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", 5);
    circle.setAttribute("fill", treeColor);
    return circle;
  }

  // Fonction pour générer l'arborescence avec angles à 90° et largeur complète
  function generateTree(depth = 0, parentX = width / 2, parentY = 50, isLeftChild = true) {
    // Création de l'élément SVG
    const svg = document.createElementNS(svgNamespace, "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "500px");

    // Si la profondeur est plus grande que la limite maximale, on arrête
    if (depth >= maxDepth) return svg;

    // Position du point actuel (racine ou noeud parent)
    let { x, y } = generatePosition(depth, parentX, parentY, isLeftChild);

    // On dessine un cercle pour ce noeud
    let node = drawNode(x, y);
    svg.appendChild(node);

    // On génère les enfants (pour chaque noeud, de manière aléatoire)
    let numChildren = Math.floor(Math.random() * maxChildren);
    for (let i = 0; i < numChildren; i++) {
      let { x: childX, y: childY } = generatePosition(depth + 1, x, y, i % 2 === 0);
      let childNode = drawNode(childX, childY);
      svg.appendChild(childNode);

      // Dessin de l'arête (edge) entre le parent et l'enfant
      let line1 = drawLine(x, y, x, childY); // Ligne verticale
      svg.appendChild(line1);
      let line2 = drawLine(x, childY, childX, childY); // Ligne horizontale
      svg.appendChild(line2);

      // Appel récursif pour générer les sous-arborescences
      let childTree = generateTree(depth + 1, x, y, i % 2 === 0);
      svg.appendChild(childTree);
    }

    return svg;
  }

  // Fonction pour réinitialiser l'arborescence
  function regenerateTree() {
    // Effacer l'arborescence actuelle
    container.innerHTML = "";

    // Générer et afficher une nouvelle arborescence
    const newTree = generateTree();
    container.appendChild(newTree);
  }

  // Ajouter un événement pour régénérer l'arborescence
  regenerateButton.addEventListener("click", regenerateTree);

  // Générer initialement l'arborescence
  regenerateTree();
});
