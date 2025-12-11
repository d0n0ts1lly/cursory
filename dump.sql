-- MySQL dump 10.13  Distrib 9.2.0, for macos15.2 (arm64)
--
-- Host: localhost    Database: shipping_db
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auctions`
--

DROP TABLE IF EXISTS `auctions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auctions` (
  `auction_id` int NOT NULL AUTO_INCREMENT,
  `auction_name` varchar(100) NOT NULL,
  `country_id` int NOT NULL,
  PRIMARY KEY (`auction_id`),
  KEY `country_id` (`country_id`),
  CONSTRAINT `auctions_ibfk_1` FOREIGN KEY (`country_id`) REFERENCES `countries` (`country_id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auctions`
--

LOCK TABLES `auctions` WRITE;
/*!40000 ALTER TABLE `auctions` DISABLE KEYS */;
INSERT INTO `auctions` VALUES (1,'Copart USA',1),(2,'IAAI USA',1),(3,'USS Japan',2),(4,'Autorola Germany',3),(5,'Copart China',4),(6,'Baltic Auctions LT',5);
/*!40000 ALTER TABLE `auctions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `country_id` int NOT NULL AUTO_INCREMENT,
  `country_name` varchar(100) NOT NULL,
  PRIMARY KEY (`country_id`),
  UNIQUE KEY `country_name` (`country_name`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries`
--

LOCK TABLES `countries` WRITE;
/*!40000 ALTER TABLE `countries` DISABLE KEYS */;
INSERT INTO `countries` VALUES (4,'Китай'),(5,'Литва'),(3,'Німеччина'),(6,'Польща'),(1,'Сполучені Штати Америки'),(2,'Японія');
/*!40000 ALTER TABLE `countries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `locations` (
  `location_id` int NOT NULL AUTO_INCREMENT,
  `location_name` varchar(100) NOT NULL,
  `country_id` int NOT NULL,
  `default_port_id` int NOT NULL,
  `days_to_port` int NOT NULL,
  PRIMARY KEY (`location_id`),
  KEY `country_id` (`country_id`),
  KEY `default_port_id` (`default_port_id`),
  CONSTRAINT `locations_ibfk_1` FOREIGN KEY (`country_id`) REFERENCES `countries` (`country_id`),
  CONSTRAINT `locations_ibfk_2` FOREIGN KEY (`default_port_id`) REFERENCES `ports` (`port_id`)
) ENGINE=InnoDB AUTO_INCREMENT=67 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locations`
--

LOCK TABLES `locations` WRITE;
/*!40000 ALTER TABLE `locations` DISABLE KEYS */;
INSERT INTO `locations` VALUES (1,'Маямі',1,1,3),(2,'Лос-Анджелес',1,1,5),(3,'Токіо',2,2,1),(4,'Берлін',3,3,1),(5,'Шанхай',4,4,2),(6,'Вільнюс',5,5,1),(7,'Варшава',6,6,1),(64,'Техас',1,1,5),(65,'Каліфорнія',1,56,2),(66,'Вашингтон',1,1,2);
/*!40000 ALTER TABLE `locations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ports`
--

DROP TABLE IF EXISTS `ports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ports` (
  `port_id` int NOT NULL AUTO_INCREMENT,
  `port_name` varchar(100) NOT NULL,
  `country_id` int NOT NULL,
  `delivery_to_europe_days` int NOT NULL,
  PRIMARY KEY (`port_id`),
  KEY `country_id` (`country_id`),
  CONSTRAINT `ports_ibfk_1` FOREIGN KEY (`country_id`) REFERENCES `countries` (`country_id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ports`
--

LOCK TABLES `ports` WRITE;
/*!40000 ALTER TABLE `ports` DISABLE KEYS */;
INSERT INTO `ports` VALUES (1,'Baltimore',1,30),(2,'Yokohama',2,35),(3,'Hamburg',3,2),(4,'Shanghai',4,40),(5,'Klaipėda',5,0),(6,'Gdynia',6,2),(56,'California',1,40);
/*!40000 ALTER TABLE `ports` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchase_images`
--

DROP TABLE IF EXISTS `purchase_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchase_images` (
  `image_id` int NOT NULL AUTO_INCREMENT,
  `purchase_id` int NOT NULL,
  `image_url` varchar(255) NOT NULL,
  `image_type` enum('auction','port','klaipeda') NOT NULL,
  `uploaded_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `notes` text,
  PRIMARY KEY (`image_id`),
  KEY `purchase_id` (`purchase_id`),
  CONSTRAINT `purchase_images_ibfk_1` FOREIGN KEY (`purchase_id`) REFERENCES `purchases` (`purchase_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchase_images`
--

LOCK TABLES `purchase_images` WRITE;
/*!40000 ALTER TABLE `purchase_images` DISABLE KEYS */;
INSERT INTO `purchase_images` VALUES (16,7,'/Users/d0n0ts1lly/Desktop/курсовой/curs_project/assets/7_20251201_211221_IMG_5988.jpeg','auction','2025-12-01 21:12:21',''),(17,7,'https://worldauto.com.ua/files/images/layout_17_391_980x0.png','auction','2025-12-01 21:13:26',''),(19,7,'https://cdn3.riastatic.com/photosnew/auto/photo/hyundai_santa-fe__622910873bx.jpg','auction','2025-12-01 21:44:33','');
/*!40000 ALTER TABLE `purchase_images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purchases`
--

DROP TABLE IF EXISTS `purchases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `purchases` (
  `purchase_id` int NOT NULL AUTO_INCREMENT,
  `vin_number` varchar(50) NOT NULL,
  `car_make` varchar(50) NOT NULL,
  `car_model` varchar(50) NOT NULL,
  `car_year` year NOT NULL,
  `buyer_id` int NOT NULL,
  `country_id` int NOT NULL,
  `auction_id` int NOT NULL,
  `location_id` int NOT NULL,
  `purchase_date` date NOT NULL,
  `price_usd` decimal(10,2) NOT NULL,
  `status_id` int NOT NULL,
  `estimated_arrival_date` date DEFAULT NULL,
  `is_delivered` tinyint(1) DEFAULT '0',
  `notes` text,
  PRIMARY KEY (`purchase_id`),
  UNIQUE KEY `uq_purchases_vin` (`vin_number`),
  KEY `buyer_id` (`buyer_id`),
  KEY `country_id` (`country_id`),
  KEY `auction_id` (`auction_id`),
  KEY `location_id` (`location_id`),
  KEY `status_id` (`status_id`),
  CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`),
  CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`country_id`) REFERENCES `countries` (`country_id`),
  CONSTRAINT `purchases_ibfk_3` FOREIGN KEY (`auction_id`) REFERENCES `auctions` (`auction_id`),
  CONSTRAINT `purchases_ibfk_4` FOREIGN KEY (`location_id`) REFERENCES `locations` (`location_id`),
  CONSTRAINT `purchases_ibfk_5` FOREIGN KEY (`status_id`) REFERENCES `statuses` (`status_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purchases`
--

LOCK TABLES `purchases` WRITE;
/*!40000 ALTER TABLE `purchases` DISABLE KEYS */;
INSERT INTO `purchases` VALUES (1,'1HGBH41JXMN109186','Toyota','Camry',2018,1,1,1,2,'2025-11-01',8500.00,3,'2025-11-30',0,'Доставляється: Лос-Анджелес → Baltimore → Клайпеда → Україна'),(2,'JH4KA9650MC001234','Nissan','Note',2016,1,3,4,4,'2025-10-20',4200.00,7,'2025-10-27',0,'Європейська доставка: Берлін → Україна'),(7,'WBA123456789ABCDE','BMW','X5',2020,1,1,2,1,'2025-11-10',18500.00,6,'2025-12-15',0,'В океані, прямує до Клайпеди'),(8,'ZFA123456789ABCDE','Fiat','500',2017,1,3,4,4,'2025-11-05',3200.00,9,'2025-11-12',0,'Вже в Україні, доставлено успішно'),(12,'WBA123456789ABCDD','Mazda','CX-30',2025,8,1,2,2,'2025-12-09',10000.00,6,'2026-01-20',0,NULL);
/*!40000 ALTER TABLE `purchases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `statuses`
--

DROP TABLE IF EXISTS `statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `statuses` (
  `status_id` int NOT NULL AUTO_INCREMENT,
  `status_key` varchar(50) NOT NULL,
  `status_name` varchar(100) NOT NULL,
  `order_index` int NOT NULL,
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `status_key` (`status_key`)
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `statuses`
--

LOCK TABLES `statuses` WRITE;
/*!40000 ALTER TABLE `statuses` DISABLE KEYS */;
INSERT INTO `statuses` VALUES (1,'bought_auction','Авто щойно куплено на аукціоні',1),(2,'paid','Оплачено',2),(3,'to_port','Їде в порт',3),(4,'at_port','В порту',4),(5,'in_sea','У морі',5),(6,'in_klaipeda','У Клайпеді',6),(7,'to_ukraine','Їде в Україну',7),(8,'cleared_customs','Розмитнено',8),(9,'in_ukraine','В Україні',9);
/*!40000 ALTER TABLE `statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `role` enum('admin','user') NOT NULL DEFAULT 'user',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'ivan','scrypt:32768:8:1$qu0fBKz1KXvVkyt7$aea406d652804e7b016990940dce991ca1ea47408dc95aafcd6c8ad83930dd1bb21d58f949fb561cdef370c7bcc3c1f6165f8732e47867e610938043d14b6899','user','2025-11-20 08:00:00','+380671234567','ivan@example.com'),(2,'admin','scrypt:32768:8:1$qu0fBKz1KXvVkyt7$aea406d652804e7b016990940dce991ca1ea47408dc95aafcd6c8ad83930dd1bb21d58f949fb561cdef370c7bcc3c1f6165f8732e47867e610938043d14b6899','admin','2025-10-01 06:15:00','+380501112233','admin@example.com'),(8,'demo_user','scrypt:32768:8:1$waZLhqAkarZa30gO$4f034ad71b4d974d4952577eaa1df5446c6ca0fa250b4ff9772631e24708db48c20f066c42fd5f07132acd7dba65f60c656b3909d30dcf12d6f39fa69c5fe3b2','admin','2025-11-22 09:33:09','+380123456789','demo@autotracker.com'),(9,'user1','scrypt:32768:8:1$jg0z831awIqElndN$34f69c947c5b57ae52f231f336734d9a3c09057dc18c7009f3c13d17227ea97bd91d838eef9fcf56f6ad3a9de9b9ab6ce4be0601723f7a9c4d5ef4bc428d2150','user','2025-11-28 09:50:38','+380987654321','user1@autotracker.com');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-11 13:37:03
