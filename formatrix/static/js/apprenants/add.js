document.addEventListener('DOMContentLoaded', function() {
  // Animation des cartes au chargement
  const cards = document.querySelectorAll('.form-section');
  cards.forEach((card, index) => {
    card.style.animationDelay = (0.15 * index) + 's';
  });
  
  // Initialiser les cartes avec effet d'ombre
  setTimeout(() => {
    document.querySelectorAll('.card').forEach(card => {
      card.classList.add('shadow-transition');
    });
  }, 300);

  // Ajouter une classe active lors du focus sur les champs
  const formInputs = document.querySelectorAll('.form-control, .form-select');
  formInputs.forEach(input => {
    // Vérifier si le champ a déjà une valeur au chargement
    if (input.value) {
      input.closest('.form-group').classList.add('has-value');
    }
    
    input.addEventListener('focus', function() {
      this.closest('.form-group').classList.add('active');
      
      // Ajouter une animation subtile à l'icône
      const icon = this.closest('.form-group').querySelector('.form-icon');
      if (icon) {
        icon.style.transform = 'translateY(-50%) scale(1.2)';
        icon.style.color = 'var(--primary-color)';
      }
    });
    
    input.addEventListener('blur', function() {
      this.closest('.form-group').classList.remove('active');
      
      // Restaurer l'icône
      const icon = this.closest('.form-group').querySelector('.form-icon');
      if (icon) {
        icon.style.transform = 'translateY(-50%)';
        icon.style.color = '';
      }
      
      if (this.value) {
        this.closest('.form-group').classList.add('has-value');
      } else {
        this.closest('.form-group').classList.remove('has-value');
      }
    });
    
    // Amélioration de l'interaction
    input.addEventListener('mouseover', function() {
      if (!this.closest('.form-group').classList.contains('active')) {
        this.style.borderColor = '#cbd5e0';
        this.style.backgroundColor = '#f7fafc';
      }
    });
    
    input.addEventListener('mouseout', function() {
      if (!this.closest('.form-group').classList.contains('active')) {
        this.style.borderColor = '#e2e8f0';
        this.style.backgroundColor = '#fff';
      }
    });
  });
  
  // Effet d'ondulation sur les boutons
  const buttons = document.querySelectorAll('.btn');
  buttons.forEach(btn => {
    btn.addEventListener('mousedown', function(e) {
      const x = e.clientX - this.getBoundingClientRect().left;
      const y = e.clientY - this.getBoundingClientRect().top;
      
      const ripple = document.createElement('span');
      ripple.classList.add('ripple-effect');
      ripple.style.left = `${x}px`;
      ripple.style.top = `${y}px`;
      
      this.appendChild(ripple);
      
      setTimeout(() => {
        ripple.remove();
      }, 600);
    });
  });
  
  // Animation des badges de section
  const badges = document.querySelectorAll('.badge-section');
  badges.forEach(badge => {
    setInterval(() => {
      badge.classList.add('pulse-effect');
      setTimeout(() => {
        badge.classList.remove('pulse-effect');
      }, 1000);
    }, 5000);
  });

  // Transition de couleur pour les en-têtes des sections au survol
  cards.forEach(card => {
    const header = card.querySelector('.card-header');
    if (header) {
      card.addEventListener('mouseenter', () => {
        header.style.background = 'linear-gradient(135deg, #5a7fe4, #3761d1)';
      });
      
      card.addEventListener('mouseleave', () => {
        header.style.background = '';
      });
    }
  });
  
  // Animation subtile pour les labels des champs obligatoires
  const requiredLabels = document.querySelectorAll('.required-asterisk');
  requiredLabels.forEach(label => {
    label.setAttribute('title', 'Champ obligatoire');
  });
  
  // Amélioration de l'interaction pour les champs de textarea
  const textareas = document.querySelectorAll('textarea.form-control');
  textareas.forEach(textarea => {
    textarea.addEventListener('focus', function() {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight + 5) + 'px';
    });
    
    textarea.addEventListener('input', function() {
      this.style.height = 'auto';
      this.style.height = (this.scrollHeight + 5) + 'px';
    });
  });
  
  // Effet de zoom sur les alertes lors de leur apparition
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    alert.style.transform = 'scale(0.95)';
    setTimeout(() => {
      alert.style.transform = 'scale(1)';
    }, 100);
  });
}); 