-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 16, 2025 at 10:35 AM
-- Server version: 8.0.38
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `atliq_tshirts`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `PopulateTShirts` ()   BEGIN
    DECLARE counter INT DEFAULT 0;
    DECLARE max_records INT DEFAULT 100;
    DECLARE brand ENUM('Van Huesen', 'Levi', 'Nike', 'Adidas');
    DECLARE color ENUM('Red', 'Blue', 'Black', 'White');
    DECLARE size ENUM('XS', 'S', 'M', 'L', 'XL');
    DECLARE price INT;
    DECLARE stock INT;

    -- Seed the random number generator
    SET SESSION rand_seed1 = UNIX_TIMESTAMP();

    WHILE counter < max_records DO
        -- Generate random values
        SET brand = ELT(FLOOR(1 + RAND() * 4), 'Van Huesen', 'Levi', 'Nike', 'Adidas');
        SET color = ELT(FLOOR(1 + RAND() * 4), 'Red', 'Blue', 'Black', 'White');
        SET size = ELT(FLOOR(1 + RAND() * 5), 'XS', 'S', 'M', 'L', 'XL');
        SET price = FLOOR(10 + RAND() * 41);
        SET stock = FLOOR(10 + RAND() * 91);

        -- Attempt to insert a new record
        -- Duplicate brand, color, size combinations will be ignored due to the unique constraint
        BEGIN
            DECLARE CONTINUE HANDLER FOR 1062 BEGIN END;  -- Handle duplicate key error
            INSERT INTO t_shirts (brand, color, size, price, stock_quantity)
            VALUES (brand, color, size, price, stock);
            SET counter = counter + 1;
        END;
    END WHILE;
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `discounts`
--

CREATE TABLE `discounts` (
  `discount_id` int NOT NULL,
  `t_shirt_id` int NOT NULL,
  `pct_discount` decimal(5,2) DEFAULT NULL
) ;

--
-- Dumping data for table `discounts`
--

INSERT INTO `discounts` (`discount_id`, `t_shirt_id`, `pct_discount`) VALUES
(1, 1, 10.00),
(2, 2, 15.00),
(3, 3, 20.00),
(4, 4, 5.00),
(5, 5, 25.00),
(6, 6, 10.00),
(7, 7, 30.00),
(8, 8, 35.00),
(9, 9, 40.00),
(10, 10, 45.00);

-- --------------------------------------------------------

--
-- Table structure for table `t_shirts`
--

CREATE TABLE `t_shirts` (
  `t_shirt_id` int NOT NULL,
  `brand` enum('Van Huesen','Levi','Nike','Adidas') NOT NULL,
  `color` enum('Red','Blue','Black','White') NOT NULL,
  `size` enum('XS','S','M','L','XL') NOT NULL,
  `price` int DEFAULT NULL,
  `stock_quantity` int NOT NULL
) ;

--
-- Dumping data for table `t_shirts`
--

INSERT INTO `t_shirts` (`t_shirt_id`, `brand`, `color`, `size`, `price`, `stock_quantity`) VALUES
(1, 'Van Huesen', 'Black', 'M', 37, 95),
(2, 'Nike', 'Black', 'S', 28, 45),
(3, 'Nike', 'White', 'XS', 20, 93),
(4, 'Adidas', 'Blue', 'XS', 42, 55),
(5, 'Van Huesen', 'Red', 'M', 33, 71),
(6, 'Nike', 'Red', 'XS', 32, 72),
(7, 'Adidas', 'White', 'M', 23, 19),
(8, 'Nike', 'Red', 'M', 46, 93),
(9, 'Adidas', 'White', 'XS', 37, 94),
(10, 'Nike', 'Blue', 'S', 19, 24),
(11, 'Van Huesen', 'Red', 'S', 10, 28),
(12, 'Adidas', 'Blue', 'XL', 49, 47),
(13, 'Van Huesen', 'Black', 'S', 19, 100),
(14, 'Levi', 'Blue', 'M', 40, 48),
(15, 'Adidas', 'Blue', 'L', 22, 72),
(16, 'Nike', 'Black', 'XL', 28, 37),
(17, 'Van Huesen', 'White', 'L', 10, 94),
(18, 'Nike', 'Blue', 'L', 50, 63),
(20, 'Adidas', 'Black', 'XL', 45, 76),
(21, 'Van Huesen', 'White', 'M', 46, 91),
(22, 'Adidas', 'Blue', 'S', 17, 27),
(23, 'Levi', 'Black', 'M', 28, 13),
(24, 'Adidas', 'Red', 'M', 46, 68),
(26, 'Adidas', 'Red', 'L', 39, 42),
(27, 'Nike', 'White', 'L', 33, 98),
(28, 'Van Huesen', 'Black', 'XL', 41, 10),
(29, 'Nike', 'Black', 'M', 19, 51),
(30, 'Nike', 'Black', 'L', 26, 75),
(31, 'Levi', 'Black', 'L', 20, 89),
(33, 'Van Huesen', 'White', 'S', 32, 87),
(35, 'Adidas', 'Black', 'L', 14, 33),
(38, 'Adidas', 'Red', 'XS', 36, 87),
(39, 'Levi', 'White', 'XL', 37, 65),
(40, 'Van Huesen', 'Blue', 'L', 10, 28),
(41, 'Van Huesen', 'Blue', 'S', 16, 88),
(42, 'Adidas', 'Black', 'S', 47, 63),
(43, 'Van Huesen', 'Blue', 'XS', 17, 78),
(44, 'Levi', 'Red', 'M', 10, 84),
(45, 'Van Huesen', 'Black', 'XS', 28, 12),
(48, 'Levi', 'Blue', 'XS', 34, 51),
(49, 'Levi', 'Red', 'XL', 26, 31),
(56, 'Van Huesen', 'Red', 'XS', 16, 66),
(57, 'Nike', 'Blue', 'XL', 36, 43),
(59, 'Adidas', 'White', 'XL', 28, 46),
(61, 'Levi', 'White', 'S', 18, 12),
(63, 'Adidas', 'Red', 'S', 37, 36),
(68, 'Van Huesen', 'Black', 'L', 47, 73),
(69, 'Adidas', 'Black', 'XS', 27, 87),
(75, 'Van Huesen', 'White', 'XL', 12, 48),
(83, 'Van Huesen', 'Red', 'XL', 37, 48),
(84, 'Van Huesen', 'Blue', 'M', 20, 89),
(85, 'Nike', 'Blue', 'XS', 39, 18),
(86, 'Levi', 'Red', 'L', 50, 98),
(93, 'Nike', 'Red', 'L', 43, 94),
(98, 'Levi', 'Blue', 'XL', 37, 54),
(99, 'Levi', 'Black', 'S', 30, 51);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `discounts`
--
ALTER TABLE `discounts`
  ADD PRIMARY KEY (`discount_id`),
  ADD KEY `t_shirt_id` (`t_shirt_id`);

--
-- Indexes for table `t_shirts`
--
ALTER TABLE `t_shirts`
  ADD PRIMARY KEY (`t_shirt_id`),
  ADD UNIQUE KEY `brand_color_size` (`brand`,`color`,`size`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `discounts`
--
ALTER TABLE `discounts`
  MODIFY `discount_id` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `t_shirts`
--
ALTER TABLE `t_shirts`
  MODIFY `t_shirt_id` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `discounts`
--
ALTER TABLE `discounts`
  ADD CONSTRAINT `discounts_ibfk_1` FOREIGN KEY (`t_shirt_id`) REFERENCES `t_shirts` (`t_shirt_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
