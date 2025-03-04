-- Création des tables pour le système de formation

-- Table des types de clients
CREATE TABLE typeclient (
    typeclientid SERIAL PRIMARY KEY,
    typeclient VARCHAR(100) NOT NULL,
    reseau VARCHAR(50) CHECK (reseau IN ('interne', 'externe'))
);

-- Table des clients
CREATE TABLE client (
    clientid SERIAL PRIMARY KEY,
    nomclient VARCHAR(100) NOT NULL,
    autresnom VARCHAR(100),
    email VARCHAR(100),
    localite VARCHAR(100),
    ville VARCHAR(100),
    numero_immatriculation VARCHAR(50),
    adresse_rue TEXT,
    telephone VARCHAR(20),
    typeclientid INTEGER REFERENCES typeclient(typeclientid)
);

-- Table des lieux de formation
CREATE TABLE lieu (
    lieuid SERIAL PRIMARY KEY,
    lieu VARCHAR(100) NOT NULL,
    adresse TEXT,
    personne_contact VARCHAR(100),
    telephone VARCHAR(20),
    mobile VARCHAR(20)
);

-- Table des détails de formation
CREATE TABLE details_formation (
    details_formation_id SERIAL PRIMARY KEY,
    nom_formation VARCHAR(200) NOT NULL,
    niveau VARCHAR(50),
    frais_par_participant DECIMAL(10, 2),
    duree_heures INTEGER,
    type_formation VARCHAR(50) CHECK (type_formation IN ('formateur', 'apprenant', 'court', 'long')),
    objectifs TEXT,
    statut_approbation VARCHAR(50),
    date_expiration_validite DATE
);

-- Table des formations
CREATE TABLE formation (
    formationid SERIAL PRIMARY KEY,
    details_formation_id INTEGER REFERENCES details_formation(details_formation_id),
    lieu_id INTEGER REFERENCES lieu(lieuid),
    horaires VARCHAR(100),
    date_approbation DATE,
    date_debut DATE NOT NULL,
    date_prevue DATE,
    date_fin DATE,
    statut VARCHAR(50) CHECK (statut IN ('en_cours', 'termine', 'annule_avec_paiement', 'annule_sans_paiement'))
);

-- Table des formateurs
CREATE TABLE formateur (
    formateurid SERIAL PRIMARY KEY,
    nomformateur VARCHAR(100) NOT NULL,
    autresnom VARCHAR(100),
    cin VARCHAR(20) UNIQUE,
    date_naissance DATE,
    telephone VARCHAR(20),
    email VARCHAR(100),
    sexe CHAR(1) CHECK (sexe IN ('M', 'F', 'A')),
    qualifications TEXT,
    specialites TEXT,
    disponibilites TEXT,
    taux_horaire DECIMAL(10, 2) DEFAULT 300.00
);

-- Table des apprenants
CREATE TABLE apprenant (
    apprenantid SERIAL PRIMARY KEY,
    nomapprenant VARCHAR(100) NOT NULL,
    autresnom VARCHAR(100),
    cin VARCHAR(20) UNIQUE,
    date_naissance DATE,
    adresse_rue TEXT,
    localite VARCHAR(100),
    ville VARCHAR(100),
    type_apprenant VARCHAR(50),
    sexe CHAR(1) CHECK (sexe IN ('M', 'F', 'A')),
    niveau_academique VARCHAR(50) CHECK (niveau_academique IN ('sous_certificat', 'certificat', 'superieur')),
    categorie_age VARCHAR(20) CHECK (categorie_age IN ('16-30', '31-60', '60+'))
);

-- Table de présence
CREATE TABLE presence (
    presenceid SERIAL PRIMARY KEY,
    date_presence DATE NOT NULL,
    formationid INTEGER REFERENCES formation(formationid),
    apprenantid INTEGER REFERENCES apprenant(apprenantid),
    present BOOLEAN DEFAULT false
);

-- Table de jonction entre clients, formations et apprenants
CREATE TABLE client_formation_apprenant (
    client_formation_apprenant_id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(clientid),
    formationid INTEGER REFERENCES formation(formationid),
    apprenantid INTEGER REFERENCES apprenant(apprenantid),
    type_inscription VARCHAR(50) CHECK (type_inscription IN ('individuelle', 'groupe', 'entreprise', 'rse', 'ong')),
    UNIQUE (client_id, formationid, apprenantid)
);

-- Table des frais de formateurs
CREATE TABLE frais_formateur (
    frais_formateur_id SERIAL PRIMARY KEY,
    formateurid INTEGER REFERENCES formateur(formateurid),
    formationid INTEGER REFERENCES formation(formationid),
    presenceid INTEGER REFERENCES presence(presenceid),
    montant_paye DECIMAL(10, 2),
    date_paiement DATE
);

-- Table des tarifs
CREATE TABLE tarif (
    tarifid SERIAL PRIMARY KEY,
    pourcentage_remise DECIMAL(5, 2),
    montant_remise DECIMAL(10, 2),
    frais_formateur DECIMAL(10, 2)
);

-- Table des résultats
CREATE TABLE resultats (
    resultatid SERIAL PRIMARY KEY,
    formationid INTEGER REFERENCES formation(formationid),
    apprenantid INTEGER REFERENCES apprenant(apprenantid),
    resultat VARCHAR(50) CHECK (resultat IN ('reussite', 'echec', 'abandon')),
    evaluation_continue DECIMAL(5, 2),
    portfolio_complete BOOLEAN,
    UNIQUE (formationid, apprenantid)
);

-- Table des factures
CREATE TABLE facture (
    factureid SERIAL PRIMARY KEY,
    clientid INTEGER REFERENCES client(clientid),
    formationid INTEGER REFERENCES formation(formationid),
    revision_facture_id INTEGER,
    date_facture DATE DEFAULT CURRENT_DATE,
    montant DECIMAL(10, 2),
    statut VARCHAR(50) DEFAULT 'en_attente',
    mode_paiement VARCHAR(50),
    facilite_paiement BOOLEAN DEFAULT false
);

-- Ajout d'indexes pour améliorer les performances
CREATE INDEX idx_formation_lieu ON formation(lieu_id);
CREATE INDEX idx_details_formation ON formation(details_formation_id);
CREATE INDEX idx_type_client ON client(typeclientid);
CREATE INDEX idx_presence_formation ON presence(formationid);
CREATE INDEX idx_client_formation_apprenant_client ON client_formation_apprenant(client_id);
CREATE INDEX idx_client_formation_apprenant_formation ON client_formation_apprenant(formationid);
CREATE INDEX idx_client_formation_apprenant_apprenant ON client_formation_apprenant(apprenantid);
CREATE INDEX idx_resultats_formation ON resultats(formationid);
CREATE INDEX idx_resultats_apprenant ON resultats(apprenantid);
CREATE INDEX idx_facture_client ON facture(clientid);
CREATE INDEX idx_facture_formation ON facture(formationid);
CREATE INDEX idx_frais_formateur_formateur ON frais_formateur(formateurid);
CREATE INDEX idx_frais_formateur_formation ON frais_formateur(formationid);

-- Commentaires de documentation sur les tables principales
COMMENT ON TABLE typeclient IS 'Types de clients (entreprise, individuel, ONG)';
COMMENT ON TABLE client IS 'Informations sur les clients';
COMMENT ON TABLE details_formation IS 'Détails des formations proposées';
COMMENT ON TABLE formation IS 'Instances spécifiques de formations avec dates et lieu';
COMMENT ON TABLE formateur IS 'Informations sur les formateurs';
COMMENT ON TABLE apprenant IS 'Informations sur les apprenants';
COMMENT ON TABLE presence IS 'Suivi de présence aux formations';
COMMENT ON TABLE client_formation_apprenant IS 'Relation entre clients, formations et apprenants';
COMMENT ON TABLE resultats IS 'Résultats des apprenants par formation';
COMMENT ON TABLE facture IS 'Factures émises aux clients';
COMMENT ON TABLE frais_formateur IS 'Frais des formateurs par formation';

-- Exemples de valeurs pour les types de clients
INSERT INTO typeclient (typeclient, reseau) VALUES 
('Individuel', 'externe'),
('Entreprise', 'externe'),
('ONG', 'externe'),
('Interne', 'interne');