-- Opcional: la app crea la base y la tabla sola al iniciar.
-- Úsalo en phpMyAdmin (pestaña SQL) solo si prefieres crearlas a mano.
CREATE DATABASE IF NOT EXISTS prueba_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE prueba_db;
CREATE TABLE IF NOT EXISTS mensaje (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(60) NOT NULL,
  texto VARCHAR(300) NOT NULL,
  fecha DATETIME DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
