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
  let animationDuration = 2; // Durée de l'animation (en secondes)
  let maxLength = 200; // Longueur maximale des branches

  // Fonction pour générer une position horizontale et verticale pour chaque point
  function generatePosition(depth, parentX = 0, parentY = 0, isLeftChild = true) {
    let x = parentX;
    let y = parentY;

    if (isLeftChild) {
      x += Math.random() * horizontalSpacing;
    } else {
      x -= Math.random() * horizontalSpacing;
    }

    y += verticalSpacing;

    return { x, y };
  }

  // Fonction pour dessiner une ligne (edge) entre deux points
  function drawLine(x1, y1, x2, y2) {
    let line = document.createElementNS(svgNamespace, "line");
    line.setAttribute("x1", x1);
    line.setAttribute("y1", y1);
    line.setAttribute("x2", x1);  // Commence à x1, y1
    line.setAttribute("y2", y1);  // Commence à y1
    line.setAttribute("stroke", treeColor);
    line.setAttribute("stroke-width", 2);
    line.style.opacity = 1; // Toujours visible
    line.classList.add("branch");
    return line;
  }

  // Fonction pour dessiner un point (node)
  function drawNode(x, y) {
    let circle = document.createElementNS(svgNamespace, "circle");
    circle.setAttribute("cx", x);
    circle.setAttribute("cy", y);
    circle.setAttribute("r", 5);
    circle.setAttribute("fill", treeColor);
    circle.classList.add("node");
    return circle;
  }

  // Fonction pour générer l'arborescence
  function generateTree(depth = 0, parentX = width / 2, parentY = 50, isLeftChild = true) {
    const svg = document.createElementNS(svgNamespace, "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "500px");

    if (depth >= maxDepth) return svg;

    let { x, y } = generatePosition(depth, parentX, parentY, isLeftChild);

    let node = drawNode(x, y);
    svg.appendChild(node);

    let numChildren = Math.floor(Math.random() * maxChildren);
    for (let i = 0; i < numChildren; i++) {
      let { x: childX, y: childY } = generatePosition(depth + 1, x, y, i % 2 === 0);
      let childNode = drawNode(childX, childY);
      svg.appendChild(childNode);

      let line1 = drawLine(x, y, x, childY); // Ligne verticale
      svg.appendChild(line1);
      let line2 = drawLine(x, childY, childX, childY); // Ligne horizontale
      svg.appendChild(line2);

      let childTree = generateTree(depth + 1, x, y, i % 2 === 0);
      svg.appendChild(childTree);

      // Animation de la croissance des lignes après génération
      animateLineGrowth(line1, childX, childY);
      animateLineGrowth(line2, childX, childY);
    }

    return svg;
  }

  // Fonction d'animation pour faire grandir les lignes
  function animateLineGrowth(line, x2, y2) {
    let startX = parseFloat(line.getAttribute("x1"));
    let startY = parseFloat(line.getAttribute("y1"));
    
    let deltaX = x2 - startX;
    let deltaY = y2 - startY;

    let progress = 0;
    let duration = animationDuration * 1000; // Convertir en millisecondes
    let startTime = null;

    function animate(timestamp) {
      if (!startTime) startTime = timestamp;
      progress = timestamp - startTime;

      let fraction = Math.min(progress / duration, 1);
      
      // Mettre à jour les coordonnées de la ligne
      line.setAttribute("x2", startX + deltaX * fraction);
      line.setAttribute("y2", startY + deltaY * fraction);

      // Si l'animation n'est pas encore terminée, continuer l'animation
      if (fraction < 1) {
        requestAnimationFrame(animate);
      } else {
        // Faire l'animation inverse (rétracter) après un délai
        setTimeout(() => animateLineShrink(line, x2, y2), 1000); // Délai avant inversion
      }
    }

    requestAnimationFrame(animate);
  }

  // Fonction pour rétracter les lignes après leur croissance
  function animateLineShrink(line, x2, y2) {
    let startX = parseFloat(line.getAttribute("x2"));
    let startY = parseFloat(line.getAttribute("y2"));
    
    let deltaX = x2 - startX;
    let deltaY = y2 - startY;

    let progress = 0;
    let duration = animationDuration * 1000; // Convertir en millisecondes
    let startTime = null;

    function animate(timestamp) {
      if (!startTime) startTime = timestamp;
      progress = timestamp - startTime;

      let fraction = Math.min(progress / duration, 1);
      
      // Mettre à jour les coordonnées de la ligne
      line.setAttribute("x2", startX - deltaX * fraction);
      line.setAttribute("y2", startY - deltaY * fraction);

      // Si l'animation n'est pas encore terminée, continuer l'animation
      if (fraction < 1) {
        requestAnimationFrame(animate);
      } else {
        // Lancer l'animation de croissance à nouveau
        setTimeout(() => animateLineGrowth(line, x2, y2), 1000); // Délai avant régénération
      }
    }

    requestAnimationFrame(animate);
  }

  // Fonction pour réinitialiser l'arborescence et ajouter l'animation
  function regenerateTree() {
    container.innerHTML = "";
    const newTree = generateTree();
    container.appendChild(newTree);
  }

  regenerateButton.addEventListener("click", regenerateTree);

  regenerateTree();
});
