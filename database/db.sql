-- Script PostgreSQL pour Formatrix
-- Création de la base de données
CREATE DATABASE formatrix_db;

\c formatrix_db

-- Activation de l'extension UUID si nécessaire
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des types de clients
CREATE TABLE type_client (
    id SERIAL PRIMARY KEY,
    type_client VARCHAR(50) NOT NULL,
    reseau VARCHAR(50) COMMENT 'Interne (communauté) ou externe'
);

-- Table des clients
CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    autre_nom VARCHAR(100),
    email VARCHAR(100),
    localite VARCHAR(100),
    ville VARCHAR(100),
    numero_enregistrement VARCHAR(50),
    adresse_rue VARCHAR(255),
    telephone VARCHAR(20),
    type_client_id INTEGER REFERENCES type_client(id)
);

-- Table des lieux (venues)
CREATE TABLE lieu (
    id SERIAL PRIMARY KEY,
    nom_lieu VARCHAR(100) NOT NULL,
    adresse VARCHAR(255),
    personne_contact VARCHAR(100),
    telephone VARCHAR(20),
    mobile VARCHAR(20)
);

-- Table des taux
CREATE TABLE tarif (
    id SERIAL PRIMARY KEY,
    pourcentage_remise DECIMAL(5,2),
    montant_remise DECIMAL(10,2),
    tarif_formateur DECIMAL(10,2) DEFAULT 300 COMMENT 'Tarif horaire par défaut à 300 Rs'
);

-- Table des cours
CREATE TABLE cours (
    id SERIAL PRIMARY KEY,
    nom_cours VARCHAR(200) NOT NULL,
    date_approbation DATE COMMENT 'Date d''approbation par l''autorité qualifiante',
    date_debut DATE,
    date_fin_prevue DATE,
    date_fin_reelle DATE,
    lieu_id INTEGER REFERENCES lieu(id),
    horaire VARCHAR(50) COMMENT 'Heures bureau, après heures, weekend',
    statut VARCHAR(20) DEFAULT 'en_cours' COMMENT 'en_cours, terminé, annulé',
    annulation_avec_paiement BOOLEAN DEFAULT FALSE
);

-- Table des détails de cours
CREATE TABLE details_cours (
    id SERIAL PRIMARY KEY,
    cours_id INTEGER REFERENCES cours(id),
    nom_cours VARCHAR(200) NOT NULL,
    niveau VARCHAR(50),
    frais_par_participant DECIMAL(10,2),
    description TEXT,
    objectifs TEXT,
    duree_heures INTEGER,
    type_cours VARCHAR(50) COMMENT 'formation_formateur, apprentissage',
    date_expiration DATE COMMENT 'Validité de 3 ans après approbation'
);

-- Table des apprenants
CREATE TABLE apprenant (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    autre_nom VARCHAR(100),
    nic VARCHAR(20) COMMENT 'Numéro d''identification nationale',
    date_naissance DATE,
    adresse_rue VARCHAR(255),
    localite VARCHAR(100),
    ville VARCHAR(100),
    type_apprenant VARCHAR(50),
    genre VARCHAR(10),
    niveau_academique VARCHAR(50) COMMENT 'En dessous du certificat scolaire, certificat scolaire et au-dessus',
    tranche_age VARCHAR(20) COMMENT '16-30, 31-60, >60'
);

-- Table des formateurs
CREATE TABLE formateur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    autre_nom VARCHAR(100),
    nic VARCHAR(20) COMMENT 'Numéro d''identification nationale',
    date_naissance DATE,
    telephone VARCHAR(20),
    email VARCHAR(100),
    genre VARCHAR(10),
    qualifications TEXT,
    specialites TEXT,
    disponibilite TEXT
);

-- Table de relation client-cours-apprenant
CREATE TABLE client_cours_apprenant (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(id),
    cours_id INTEGER REFERENCES cours(id),
    apprenant_id INTEGER REFERENCES apprenant(id),
    date_inscription DATE DEFAULT CURRENT_DATE
);

-- Table des présences
CREATE TABLE presence (
    id SERIAL PRIMARY KEY,
    date_presence DATE NOT NULL,
    cours_id INTEGER REFERENCES cours(id),
    details_cours_id INTEGER REFERENCES details_cours(id),
    lieu_id INTEGER REFERENCES lieu(id),
    commentaires TEXT
);

-- Table des honoraires des formateurs
CREATE TABLE honoraire_formateur (
    id SERIAL PRIMARY KEY,
    formateur_id INTEGER REFERENCES formateur(id),
    cours_id INTEGER REFERENCES cours(id),
    presence_id INTEGER REFERENCES presence(id),
    heures_prestees DECIMAL(5,2),
    montant_paye DECIMAL(10,2),
    date_paiement DATE,
    statut_paiement VARCHAR(20) DEFAULT 'en_attente' COMMENT 'en_attente, payé'
);

-- Table des résultats
CREATE TABLE resultat (
    id SERIAL PRIMARY KEY,
    cours_id INTEGER REFERENCES cours(id),
    apprenant_id INTEGER REFERENCES apprenant(id),
    resultat VARCHAR(20) COMMENT 'réussite, échec, abandon',
    assiduite DECIMAL(5,2) COMMENT 'Pourcentage de présence',
    evaluation_continue DECIMAL(5,2),
    portfolio DECIMAL(5,2),
    commentaires TEXT
);

-- Table des factures
CREATE TABLE facture (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES client(id),
    cours_id INTEGER REFERENCES cours(id),
    numero_revision INTEGER DEFAULT 1,
    date_emission DATE DEFAULT CURRENT_DATE,
    montant_total DECIMAL(10,2),
    montant_paye DECIMAL(10,2) DEFAULT 0,
    statut VARCHAR(20) DEFAULT 'émise' COMMENT 'émise, payée, annulée',
    date_paiement DATE,
    mode_paiement VARCHAR(50),
    facilite_paiement BOOLEAN DEFAULT FALSE COMMENT 'Pour les inscriptions individuelles'
);

-- Création des index pour optimiser les performances
CREATE INDEX idx_cours_statut ON cours(statut);
CREATE INDEX idx_apprenant_genre ON apprenant(genre);
CREATE INDEX idx_apprenant_niveau ON apprenant(niveau_academique);
CREATE INDEX idx_apprenant_age ON apprenant(tranche_age);
CREATE INDEX idx_resultat_cours ON resultat(cours_id);
CREATE INDEX idx_facture_client ON facture(client_id);
CREATE INDEX idx_facture_statut ON facture(statut);
CREATE INDEX idx_presence_date ON presence(date_presence);
CREATE INDEX idx_client_cours_apprenant ON client_cours_apprenant(client_id, cours_id, apprenant_id);

-- Création d'une vue pour les cours dont la validité expire bientôt (dans 3 mois)
CREATE VIEW cours_expiration_prochaine AS
SELECT c.id, dc.nom_cours, dc.date_expiration
FROM cours c
JOIN details_cours dc ON c.id = dc.cours_id
WHERE dc.date_expiration BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '3 months');

-- Création d'une vue pour le rapport démographique par genre et âge
CREATE VIEW rapport_demographique AS
SELECT 
    c.id AS cours_id,
    c.nom_cours,
    SUM(CASE WHEN a.genre = 'M' AND a.tranche_age = '16-30' THEN 1 ELSE 0 END) AS hommes_16_30,
    SUM(CASE WHEN a.genre = 'M' AND a.tranche_age = '31-60' THEN 1 ELSE 0 END) AS hommes_31_60,
    SUM(CASE WHEN a.genre = 'M' AND a.tranche_age = '>60' THEN 1 ELSE 0 END) AS hommes_60_plus,
    SUM(CASE WHEN a.genre = 'F' AND a.tranche_age = '16-30' THEN 1 ELSE 0 END) AS femmes_16_30,
    SUM(CASE WHEN a.genre = 'F' AND a.tranche_age = '31-60' THEN 1 ELSE 0 END) AS femmes_31_60,
    SUM(CASE WHEN a.genre = 'F' AND a.tranche_age = '>60' THEN 1 ELSE 0 END) AS femmes_60_plus,
    SUM(CASE WHEN a.genre = 'M' AND a.niveau_academique = 'below_sc' THEN 1 ELSE 0 END) AS hommes_sous_sc,
    SUM(CASE WHEN a.genre = 'M' AND a.niveau_academique = 'sc_above' THEN 1 ELSE 0 END) AS hommes_sc_et_plus,
    SUM(CASE WHEN a.genre = 'F' AND a.niveau_academique = 'below_sc' THEN 1 ELSE 0 END) AS femmes_sous_sc,
    SUM(CASE WHEN a.genre = 'F' AND a.niveau_academique = 'sc_above' THEN 1 ELSE 0 END) AS femmes_sc_et_plus
FROM cours c
JOIN client_cours_apprenant cca ON c.id = cca.cours_id
JOIN apprenant a ON cca.apprenant_id = a.id
GROUP BY c.id, c.nom_cours;

-- Création d'une vue pour le rapport de résultats
CREATE VIEW rapport_resultats AS
SELECT 
    c.id AS cours_id,
    c.nom_cours,
    cl.nom AS sponsor,
    COUNT(r.id) AS total_participants,
    SUM(CASE WHEN r.resultat = 'réussite' THEN 1 ELSE 0 END) AS reussites,
    SUM(CASE WHEN r.resultat = 'échec' THEN 1 ELSE 0 END) AS echecs,
    SUM(CASE WHEN r.resultat = 'abandon' THEN 1 ELSE 0 END) AS abandons
FROM cours c
JOIN client_cours_apprenant cca ON c.id = cca.cours_id
JOIN client cl ON cca.client_id = cl.id
JOIN resultat r ON c.id = r.cours_id AND cca.apprenant_id = r.apprenant_id
GROUP BY c.id, c.nom_cours, cl.nom;

-- Création d'une vue pour l'utilisation des ressources
CREATE VIEW utilisation_ressources AS
SELECT 
    f.id AS formateur_id,
    f.nom AS nom_formateur,
    COUNT(DISTINCT c.id) AS nombre_cours,
    SUM(hf.heures_prestees) AS total_heures,
    SUM(hf.montant_paye) AS total_paye
FROM formateur f
JOIN honoraire_formateur hf ON f.id = hf.formateur_id
JOIN cours c ON hf.cours_id = c.id
WHERE EXTRACT(YEAR FROM c.date_debut) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY f.id, f.nom;

-- Insertion des données de base pour les types de clients
INSERT INTO type_client (type_client, reseau) VALUES 
('Entreprise', 'externe'),
('Individuel', 'externe'),
('ONG', 'externe'),
('Interne', 'interne');

-- Création de la fonction pour calculer automatiquement les honoraires des formateurs
CREATE OR REPLACE FUNCTION calculer_honoraires_formateur()
RETURNS TRIGGER AS $$
BEGIN
    -- Récupération du tarif horaire actuel
    NEW.montant_paye = NEW.heures_prestees * (SELECT tarif_formateur FROM tarif ORDER BY id DESC LIMIT 1);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Création du trigger pour calculer automatiquement les honoraires
CREATE TRIGGER trigger_calculer_honoraires
BEFORE INSERT OR UPDATE ON honoraire_formateur
FOR EACH ROW
EXECUTE FUNCTION calculer_honoraires_formateur();

-- Fonction pour vérifier l'expiration des cours
CREATE OR REPLACE FUNCTION verifier_expiration_cours()
RETURNS TRIGGER AS $$
BEGIN
    -- Définir la date d'expiration à 3 ans après la date d'approbation
    NEW.date_expiration = NEW.date_approbation + INTERVAL '3 years';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour définir automatiquement la date d'expiration
CREATE TRIGGER trigger_expiration_cours
BEFORE INSERT OR UPDATE ON details_cours
FOR EACH ROW
EXECUTE FUNCTION verifier_expiration_cours();

-- Commentaires sur la base de données
COMMENT ON DATABASE formatrix_db IS 'Base de données pour le système de gestion Formatrix pour centre de formation ONG';
COMMENT ON TABLE cours IS 'Table principale des cours proposés par l''ONG';
COMMENT ON TABLE apprenant IS 'Informations sur les apprenants participant aux cours';
COMMENT ON TABLE formateur IS 'Informations sur les formateurs dispensant les cours';
COMMENT ON TABLE client IS 'Entreprises, individus ou ONG qui inscrivent des apprenants';
COMMENT ON TABLE facture IS 'Factures émises aux clients pour les cours';
COMMENT ON TABLE resultat IS 'Résultats des apprenants pour chaque cours';
