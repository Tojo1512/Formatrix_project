// Script pour mettre à jour uniquement le comptage des apprenants dans le dashboard (sans données statiques)
document.addEventListener('DOMContentLoaded', function() {
    console.log("Script de dashboard propre chargé (sans données statiques)");
    
    // Mise à jour du comptage des apprenants depuis l'API
    fetch('/api/apprenants/count/')
        .then(function(response) { 
            console.log("Réponse reçue du compteur d'apprenants");
            return response.json(); 
        })
        .then(function(data) {
            console.log("Données du compteur d'apprenants:", data);
            var apprenantCards = document.querySelectorAll('.card-category');
            apprenantCards.forEach(function(card) {
                if (card.textContent.trim() === 'Apprenants') {
                    var cardTitle = card.parentNode.querySelector('.card-title');
                    if (cardTitle) {
                        cardTitle.textContent = data.count;
                        console.log("Compteur d'apprenants mis à jour:", data.count);
                    }
                }
            });
        })
        .catch(function(error) {
            console.error('Erreur lors de la récupération du comptage des apprenants:', error);
        });
}); 