CREATE DATABASE  IF NOT EXISTS `medidor_plus` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `medidor_plus`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: medidor_plus
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `imoveis`
--

DROP TABLE IF EXISTS `imoveis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `imoveis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(150) NOT NULL,
  `fk_usuarios_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `imoveis_fk_usuario_id` (`fk_usuarios_id`),
  CONSTRAINT `imoveis_fk_usuario_id` FOREIGN KEY (`fk_usuarios_id`) REFERENCES `usuarios` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `imoveis`
--

LOCK TABLES `imoveis` WRITE;
/*!40000 ALTER TABLE `imoveis` DISABLE KEYS */;
INSERT INTO `imoveis` VALUES (1,'Residencial M7',1),(2,'Predio Mari',1);
/*!40000 ALTER TABLE `imoveis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `leituras`
--

DROP TABLE IF EXISTS `leituras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `leituras` (
  `id` int NOT NULL AUTO_INCREMENT,
  `leitura` decimal(10,2) NOT NULL,
  `data_leitura` datetime DEFAULT CURRENT_TIMESTAMP,
  `valor_total` decimal(10,2) DEFAULT '0.00',
  `fk_medidor_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `leituras_fk_medidor_id` (`fk_medidor_id`),
  CONSTRAINT `leituras_fk_medidor_id` FOREIGN KEY (`fk_medidor_id`) REFERENCES `medidores` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `leituras`
--

LOCK TABLES `leituras` WRITE;
/*!40000 ALTER TABLE `leituras` DISABLE KEYS */;
/*!40000 ALTER TABLE `leituras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `medidores`
--

DROP TABLE IF EXISTS `medidores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `medidores` (
  `id` int NOT NULL AUTO_INCREMENT,
  `unidade` varchar(100) DEFAULT NULL,
  `identificador` varchar(100) DEFAULT NULL,
  `tipo` enum('agua','energia') NOT NULL,
  `valor_total` decimal(10,2) DEFAULT NULL,
  `fk_imoveis_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `medidores_fk_imoveis_id` (`fk_imoveis_id`),
  CONSTRAINT `medidores_fk_imoveis_id` FOREIGN KEY (`fk_imoveis_id`) REFERENCES `imoveis` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `medidores`
--

LOCK TABLES `medidores` WRITE;
/*!40000 ALTER TABLE `medidores` DISABLE KEYS */;
/*!40000 ALTER TABLE `medidores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `senha_hash` varchar(255) NOT NULL,
  `cargo` enum('usuario','admin') DEFAULT 'usuario',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Rafael','rafael@gmail.com','scrypt:32768:8:1$TQNx3sBclOos0hDX$92eeea665f3a69f1b749457895af4b4f0e758a1e682101e100624bb15f41bc6bf1d9c7f6a09018aa4f612ca8d69e0cfc98191da6f0a345464209b303ceb0666e','usuario'),(2,'Kauan','kauan@gmail.com','scrypt:32768:8:1$bGEjPCW7LJSAeM9X$be3ecc967b69285717a6a48e9bd22a6402d30a9ade6c4967d7bb89e02981d06f519296127de91e5a3d8fd64bdd25a160485f0f11053548fd99db8d865861b911','usuario'),(3,'Joao','joao@gmail.com','scrypt:32768:8:1$EyCUOFc9f4AUHbrY$a9b1e264c68fb8219114f253f35110ed084ee0d7cc348ba33b3d94f22e1406b205b276818070fc22e29b0e911a4504f55a881a03ebbeb87932e15591956315d3','usuario'),(4,'Rafael','rafaelmaranhao88@gmail.com','scrypt:32768:8:1$yXORlfxE5rKgFQ5w$97ad1d336d9270b82bd1a2eba599d919c167b719d402b92689080dd848876a8c6689b127e2305862da763e021e98f49aae0e00e34e1284a7562f40f86a5abf2c','usuario');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'medidor_plus'
--

--
-- Dumping routines for database 'medidor_plus'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-24 18:35:48
