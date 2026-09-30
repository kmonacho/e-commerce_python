-- ==========================================================
-- Boutique de chaussures en ligne - Schema MySQL 8.1 (version Python)
-- ==========================================================
DROP DATABASE IF EXISTS boutique_chaussures3;
CREATE DATABASE boutique_chaussures3 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE boutique_chaussures3;

CREATE TABLE marque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);

-- Les collections sont extensibles : l'administrateur peut en ajouter de
-- nouvelles depuis le back-office (table alimentee au depart avec "Aucune",
-- collection par defaut de toute nouvelle chaussure).
CREATE TABLE collection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL UNIQUE
);
INSERT INTO collection (nom) VALUES ('Aucune');

CREATE TABLE chaussure (
    id INT AUTO_INCREMENT PRIMARY KEY,
    modele VARCHAR(150) NOT NULL,
    marque_id INT NOT NULL,
    date_sortie DATE,
    prix DECIMAL(10,2) NOT NULL,
    genre ENUM('HOMME','FEMME','UNISEXE') NOT NULL DEFAULT 'UNISEXE',
    collection_id INT NOT NULL DEFAULT 1,
    description TEXT,
    image_url VARCHAR(255),
    CONSTRAINT fk_chaussure_marque FOREIGN KEY (marque_id) REFERENCES marque(id),
    CONSTRAINT fk_chaussure_collection FOREIGN KEY (collection_id) REFERENCES collection(id)
);

CREATE TABLE taille (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chaussure_id INT NOT NULL,
    taille_us DECIMAL(3,1) NOT NULL,
    taille_fr DECIMAL(3,1) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_taille_chaussure FOREIGN KEY (chaussure_id) REFERENCES chaussure(id) ON DELETE CASCADE,
    UNIQUE KEY uniq_taille_chaussure (chaussure_id, taille_us)
);

CREATE TABLE utilisateur (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    role ENUM('CLIENT','ADMIN') NOT NULL DEFAULT 'CLIENT',
    accepte_cookies BOOLEAN NOT NULL DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE panier_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    taille_id INT NOT NULL,
    quantite INT NOT NULL DEFAULT 1,
    CONSTRAINT fk_panier_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id) ON DELETE CASCADE,
    CONSTRAINT fk_panier_taille FOREIGN KEY (taille_id) REFERENCES taille(id) ON DELETE CASCADE
);

CREATE TABLE commande (
    id INT AUTO_INCREMENT PRIMARY KEY,
    utilisateur_id INT NOT NULL,
    date_commande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut ENUM('EN_ATTENTE','PAYEE','ANNULEE') NOT NULL DEFAULT 'EN_ATTENTE',
    total DECIMAL(10,2) NOT NULL DEFAULT 0,
    mode_paiement ENUM('CARTE','TWINT','GOOGLE_GIFT_CARD') DEFAULT NULL,
    CONSTRAINT fk_commande_utilisateur FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id)
);

CREATE TABLE ligne_commande (
    id INT AUTO_INCREMENT PRIMARY KEY,
    commande_id INT NOT NULL,
    taille_id INT NOT NULL,
    quantite INT NOT NULL,
    prix_unitaire DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_ligne_commande FOREIGN KEY (commande_id) REFERENCES commande(id) ON DELETE CASCADE,
    CONSTRAINT fk_ligne_taille FOREIGN KEY (taille_id) REFERENCES taille(id)
);

CREATE TABLE partenaire (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(150) NOT NULL,
    description TEXT,
    logo_url VARCHAR(255),
    site_web VARCHAR(255),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE message_contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    sujet VARCHAR(200),
    message TEXT NOT NULL,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    lu BOOLEAN DEFAULT FALSE
);

CREATE TABLE carte_cadeau_google (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(30) NOT NULL UNIQUE,
    montant DECIMAL(10,2) NOT NULL,
    utilisee BOOLEAN DEFAULT FALSE
);

CREATE TABLE paiement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    commande_id INT NOT NULL,
    mode ENUM('CARTE','TWINT','GOOGLE_GIFT_CARD') NOT NULL,
    reference VARCHAR(100),
    statut ENUM('REUSSI','ECHOUE') NOT NULL,
    date_paiement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_paiement_commande FOREIGN KEY (commande_id) REFERENCES commande(id)
);

-- ==========================================================
-- Donnees de demonstration
-- ==========================================================
INSERT INTO marque (nom) VALUES ('Nike'), ('Adidas'), ('Puma'), ('New Balance');

INSERT INTO chaussure (modele, marque_id, date_sortie, prix, genre, collection_id, description, image_url) VALUES
('Air Max 90', 1, '2024-03-01', 139.90, 'HOMME', 1, 'Une icone intemporelle du style urbain.', 'images/airmax90.jpg'),
('Ultraboost 22', 2, '2023-11-15', 179.90, 'FEMME', 1, 'Confort et retour d energie exceptionnels.', 'images/ultraboost22.jpg'),
('Suede Classic', 3, '2022-05-20', 79.90, 'UNISEXE', 1, 'Le modele le plus iconique de Puma.', 'images/suede.jpg'),
('574 Core', 4, '2023-01-10', 99.90, 'HOMME', 1, 'Un mix parfait entre style retro et confort moderne.', 'images/574core.jpg');

INSERT INTO taille (chaussure_id, taille_us, taille_fr, stock) VALUES
(1, 8.0, 41, 10), (1, 9.0, 42, 8), (1, 10.0, 43, 5),
(2, 6.0, 37, 6), (2, 7.0, 38, 9), (2, 8.0, 39, 4),
(3, 7.5, 40, 12), (3, 8.5, 41.5, 7),
(4, 8.0, 41, 10), (4, 9.0, 42, 6);

INSERT INTO partenaire (nom, description, logo_url, site_web) VALUES
('SportCorp SA', 'Distributeur officiel Nike en Suisse romande.', 'images/partenaire1.png', 'https://example.com'),
('ShoeWorld', 'Grossiste multimarque de chaussures de sport.', 'images/partenaire2.png', 'https://example.com');

INSERT INTO carte_cadeau_google (code, montant, utilisee) VALUES
('GGC-1234-5678-9012', 50.00, FALSE),
('GGC-1111-2222-3333', 100.00, FALSE);

-- Remarque : le compte administrateur se cree via le script Python
-- scripts/creer_admin.py (voir README.md) car le mot de passe doit etre
-- hache avant insertion.
