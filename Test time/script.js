window.onload = function() {
    const svgObject = document.getElementById('svgObject');
    const timerElement = document.getElementById('animationTime');
    const statusElement = document.getElementById('status');
    
    let startTime;
    let animationDuration = 0;
    
    svgObject.addEventListener('load', function() {
        // Quand le SVG est chargé, commencez à écouter les animations
        const svgDoc = svgObject.contentDocument;
        const pathElements = svgDoc.querySelectorAll('path');
        
        // Démarrer le chronomètre à la première animation
        startTime = performance.now();
        
        // Enregistrer le début de l'animation
        statusElement.innerHTML = 'Animation en cours...';
        
        // Ajouter un listener pour la fin de l'animation
        pathElements.forEach(path => {
            path.addEventListener('animationend', function() {
                // Calculer le temps réel
                const endTime = performance.now();
                const elapsedTime = (endTime - startTime) / 1000; // Temps en secondes
                
                // Afficher le temps dans l'élément "timer"
                timerElement.textContent = elapsedTime.toFixed(2);
                
                // Mettre à jour le statut
                statusElement.innerHTML = `Animation terminée en ${elapsedTime.toFixed(2)} secondes`;
            });
        });
    });
};
