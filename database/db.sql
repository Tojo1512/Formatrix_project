-- Création des tables pour le système de formation

-- Table des types de clients
CREATE TABLE type_client (
    type_client_id SERIAL PRIMARY KEY,
    type_client VARCHAR(100) NOT NULL,
    reseau VARCHAR(50) CHECK (reseau IN ('interne', 'externe')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des clients
CREATE TABLE client (
    client_id SERIAL PRIMARY KEY,
    nom_client VARCHAR(100) NOT NULL,
    autres_nom VARCHAR(100),
    email VARCHAR(100),
    localite VARCHAR(100),
    ville VARCHAR(100),
    numero_immatriculation VARCHAR(50),
    adresse_rue TEXT,
    telephone VARCHAR(20),
    type_client_id INTEGER REFERENCES type_client(type_client_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des lieux
CREATE TABLE lieu (
    lieu_id SERIAL PRIMARY KEY,
    nom_lieu VARCHAR(100) NOT NULL,
    adresse TEXT,
    personne_contact VARCHAR(100),
    telephone VARCHAR(20),
    mobile VARCHAR(20),
    capacite INTEGER,
    equipements TEXT,
    disponibilite TEXT,
    cout_location DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des cours (remplace details_formation)
CREATE TABLE cours (
    cours_id SERIAL PRIMARY KEY,
    nom_cours VARCHAR(200) NOT NULL,
    niveau VARCHAR(50),
    frais_par_participant DECIMAL(10, 2),
    duree_heures INTEGER,
    type_cours VARCHAR(50) CHECK (type_cours IN ('formateur', 'apprenant', 'court', 'long')),
    objectifs TEXT,
    prerequis TEXT,
    materiel_requis TEXT,
    statut_approbation VARCHAR(50),
    date_approbation DATE,
    date_expiration_validite DATE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des modules de cours
CREATE TABLE module (
    module_id SERIAL PRIMARY KEY,
    cours_id INTEGER REFERENCES cours(cours_id),
    nom_module VARCHAR(200) NOT NULL,
    description TEXT,
    duree_heures INTEGER,
    ordre INTEGER,
    objectifs_module TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des documents administratifs
CREATE TABLE document (
    document_id SERIAL PRIMARY KEY,
    cours_id INTEGER REFERENCES cours(cours_id),
    type_document VARCHAR(100) NOT NULL,
    nom_fichier VARCHAR(255),
    chemin_fichier TEXT,
    date_soumission DATE,
    date_validation DATE,
    statut VARCHAR(50) CHECK (statut IN ('en_attente', 'valide', 'refuse', 'expire')),
    commentaires TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des renouvellements de cours
CREATE TABLE renouvellement (
    renouvellement_id SERIAL PRIMARY KEY,
    cours_id INTEGER REFERENCES cours(cours_id),
    date_demande DATE NOT NULL,
    date_renouvellement DATE,
    statut VARCHAR(50) CHECK (statut IN ('en_cours', 'approuve', 'refuse')),
    commentaires TEXT,
    documents_soumis TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des sessions de formation
CREATE TABLE session (
    session_id SERIAL PRIMARY KEY,
    cours_id INTEGER REFERENCES cours(cours_id),
    lieu_id INTEGER REFERENCES lieu(lieu_id),
    horaires VARCHAR(100),
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(50) CHECK (statut IN ('en_cours', 'termine', 'annule_avec_paiement', 'annule_sans_paiement')),
    nombre_places_total INTEGER,
    nombre_places_restantes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des formateurs
CREATE TABLE formateur (
    formateur_id SERIAL PRIMARY KEY,
    nom_formateur VARCHAR(100) NOT NULL,
    autres_nom VARCHAR(100),
    cin VARCHAR(20) UNIQUE,
    date_naissance DATE,
    telephone VARCHAR(20),
    email VARCHAR(100),
    sexe CHAR(1) CHECK (sexe IN ('M', 'F', 'A')),
    qualifications TEXT,
    specialites TEXT,
    disponibilites TEXT,
    taux_horaire DECIMAL(10, 2) DEFAULT 300.00,
    statut VARCHAR(50) CHECK (statut IN ('actif', 'inactif', 'en_conge')),
    date_debut_contrat DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des apprenants
CREATE TABLE apprenant (
    apprenant_id SERIAL PRIMARY KEY,
    nom_apprenant VARCHAR(100) NOT NULL,
    autres_nom VARCHAR(100),
    cin VARCHAR(20) UNIQUE,
    date_naissance DATE,
    adresse_rue TEXT,
    localite VARCHAR(100),
    ville VARCHAR(100),
    type_apprenant VARCHAR(50),
    sexe CHAR(1) CHECK (sexe IN ('M', 'F', 'A')),
    niveau_academique VARCHAR(50) CHECK (niveau_academique IN ('sous_certificat', 'certificat', 'superieur')),
    categorie_age VARCHAR(20) CHECK (categorie_age IN ('16-30', '31-60', '60+')),
    besoins_speciaux TEXT,
    contact_urgence VARCHAR(100),
    telephone_urgence VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des présences
CREATE TABLE presence (
    presence_id SERIAL PRIMARY KEY,
    date_presence DATE NOT NULL,
    session_id INTEGER REFERENCES session(session_id),
    apprenant_id INTEGER REFERENCES apprenant(apprenant_id),
    present BOOLEAN DEFAULT false,
    retard INTEGER DEFAULT 0,
    commentaires TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de jonction entre clients, sessions et apprenants
CREATE TABLE inscription (
    inscription_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(client_id),
    session_id INTEGER REFERENCES session(session_id),
    apprenant_id INTEGER REFERENCES apprenant(apprenant_id),
    type_inscription VARCHAR(50) CHECK (type_inscription IN ('individuelle', 'groupe', 'entreprise', 'rse', 'ong')),
    date_inscription DATE DEFAULT CURRENT_DATE,
    statut_inscription VARCHAR(50) DEFAULT 'en_cours',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (client_id, session_id, apprenant_id)
);

-- Table des paiements formateurs
CREATE TABLE paiement_formateur (
    paiement_formateur_id SERIAL PRIMARY KEY,
    formateur_id INTEGER REFERENCES formateur(formateur_id),
    session_id INTEGER REFERENCES session(session_id),
    presence_id INTEGER REFERENCES presence(presence_id),
    montant_paye DECIMAL(10, 2),
    date_paiement DATE,
    mode_paiement VARCHAR(50),
    reference_paiement VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des tarifs
CREATE TABLE tarif (
    tarif_id SERIAL PRIMARY KEY,
    pourcentage_remise DECIMAL(5, 2),
    montant_remise DECIMAL(10, 2),
    frais_formateur DECIMAL(10, 2),
    date_debut_validite DATE,
    date_fin_validite DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des résultats
CREATE TABLE resultat (
    resultat_id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES session(session_id),
    apprenant_id INTEGER REFERENCES apprenant(apprenant_id),
    resultat VARCHAR(50) CHECK (resultat IN ('reussite', 'echec', 'abandon')),
    evaluation_continue DECIMAL(5, 2),
    portfolio_complete BOOLEAN,
    commentaires TEXT,
    date_evaluation DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (session_id, apprenant_id)
);

-- Table des factures
CREATE TABLE facture (
    facture_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(client_id),
    session_id INTEGER REFERENCES session(session_id),
    revision_facture_id INTEGER,
    date_facture DATE DEFAULT CURRENT_DATE,
    montant DECIMAL(10, 2),
    statut VARCHAR(50) DEFAULT 'en_attente',
    mode_paiement VARCHAR(50),
    facilite_paiement BOOLEAN DEFAULT false,
    echeances_paiement JSON,
    reference_paiement VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajout d'indexes pour améliorer les performances
CREATE INDEX idx_session_lieu ON session(lieu_id);
CREATE INDEX idx_session_cours ON session(cours_id);
CREATE INDEX idx_type_client ON client(type_client_id);
CREATE INDEX idx_presence_session ON presence(session_id);
CREATE INDEX idx_presence_date ON presence(date_presence);
CREATE INDEX idx_inscription_client ON inscription(client_id);
CREATE INDEX idx_inscription_session ON inscription(session_id);
CREATE INDEX idx_inscription_apprenant ON inscription(apprenant_id);
CREATE INDEX idx_resultat_session ON resultat(session_id);
CREATE INDEX idx_resultat_apprenant ON resultat(apprenant_id);
CREATE INDEX idx_facture_client ON facture(client_id);
CREATE INDEX idx_facture_session ON facture(session_id);
CREATE INDEX idx_paiement_formateur ON paiement_formateur(formateur_id);
CREATE INDEX idx_paiement_session ON paiement_formateur(session_id);
CREATE INDEX idx_module_cours ON module(cours_id);
CREATE INDEX idx_document_cours ON document(cours_id);

-- Commentaires de documentation sur les tables principales
COMMENT ON TABLE type_client IS 'Types de clients (entreprise, individuel, ONG)';
COMMENT ON TABLE client IS 'Informations sur les clients';
COMMENT ON TABLE cours IS 'Catalogue des cours proposés';
COMMENT ON TABLE session IS 'Sessions de formation programmées';
COMMENT ON TABLE formateur IS 'Informations sur les formateurs';
COMMENT ON TABLE apprenant IS 'Informations sur les apprenants';
COMMENT ON TABLE presence IS 'Suivi de présence aux sessions';
COMMENT ON TABLE inscription IS 'Inscriptions des apprenants aux sessions';
COMMENT ON TABLE resultat IS 'Résultats des apprenants par session';
COMMENT ON TABLE facture IS 'Factures émises aux clients';
COMMENT ON TABLE paiement_formateur IS 'Paiements des formateurs';
COMMENT ON TABLE module IS 'Modules composant les cours';
COMMENT ON TABLE document IS 'Documents administratifs des cours';
COMMENT ON TABLE renouvellement IS 'Suivi des renouvellements de certification';

-- Exemples de valeurs pour les types de clients
INSERT INTO type_client (type_client, reseau) VALUES 
('Individuel', 'externe'),
('Entreprise', 'externe'),
('ONG', 'externe'),
('Interne', 'interne');