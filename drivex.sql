-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 09, 2024 at 10:32 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `drivex`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `admin_id` varchar(50) NOT NULL,
  `position` varchar(100) NOT NULL,
  `nid` varchar(20) NOT NULL,
  `password` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cars`
--

CREATE TABLE `cars` (
  `id` int(11) NOT NULL,
  `carVIN_No` varchar(100) NOT NULL,
  `name` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  `capacity` int(11) NOT NULL,
  `color` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `plate_num` varchar(50) NOT NULL,
  `price` float DEFAULT NULL,
  `pickup_point_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cars`
--

INSERT INTO `cars` (`id`, `carVIN_No`, `name`, `model`, `capacity`, `color`, `description`, `image_url`, `plate_num`, `price`, `pickup_point_id`) VALUES
(1, '1', 'Corolla', 'Toyota Corolla', 4, 'white', 'Reinvent adventure with an all new hybrid experience.', 'Corolla.jpg', '8976', 0, 1),
(2, '123', 'Noah', 'Toyota Noah', 4, 'white', 'A good seating arrangement for eight passengers.', 'Noah.jpg', '7565', 0, 1),
(41, '12345', 'HondaHRV', 'Honda HR-V', 4, 'White', 'Reinvent adventure with an all new hybrid experience.', 'Honda_HR-V.jpg', '1234', 0, 2),
(42, '1234', 'NissanX-Trail', 'Nissan X-Trail', 4, 'White', 'A good seating arrangement for eight passengers.', 'Prado.jpg', '1234', 0, 2);

-- --------------------------------------------------------

--
-- Table structure for table `employee`
--

CREATE TABLE `employee` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `employee_id` varchar(50) NOT NULL,
  `position` varchar(100) NOT NULL,
  `nid` varchar(20) NOT NULL,
  `password` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `employee`
--

INSERT INTO `employee` (`id`, `name`, `email`, `employee_id`, `position`, `nid`, `password`) VALUES
(1, 'nusrat zahan', 'nusratzahan@gmail.com', '1234', 'employee', '1234', 'scrypt:32768:8:1$yS0DqI3oHE6O3lvT$bb7729fd7a904b3e1b5627e18e66e02769dae8b0277e4204e9a2ccc748769b01aecb26946432b469bf2399dcfc373c92ca3af7ee8d706a1b652cebcfc3e2a210'),
(2, 'Nusrat', 'nusratzahan6070@gmail.com', '123', '3', '45', 'scrypt:32768:8:1$5L1kupLnv8e5d3ww$b4bb417ca018f7f23d5ceea00aa95c5eb1ea705832d28da3bf74c30a5cf6ccfaf9cfa8914bd67667d0e4156ae2a547adb794faccfabce257b4f11908800ef070');

-- --------------------------------------------------------

--
-- Table structure for table `pickup_points`
--

CREATE TABLE `pickup_points` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `latitude` float NOT NULL,
  `longitude` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pickup_points`
--

INSERT INTO `pickup_points` (`id`, `name`, `latitude`, `longitude`) VALUES
(1, 'DriveX Pickup Point 1', 23.877, 90.3228),
(2, 'DriveX Pickup Point 2', 23.8519, 90.4081);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) NOT NULL,
  `license` varchar(50) DEFAULT NULL,
  `nid` varchar(20) NOT NULL,
  `password` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `license`, `nid`, `password`) VALUES
(1, 'shihab', 'samiulalim123456789@gmail.com', '1234', '1234', 'scrypt:32768:8:1$ragIkspDJIRXsco1$e799ed0e81c3a6960731eb380625be6d93b8493ae3280639ff1b09a7b4f2ea5ffaddc6e621aec3d49a479916c94a0b13b55182974f9d2c289f51b90980b46cc2'),
(2, 'shihab', 'shihab22205101551@diu.edu.bd', '1234', '1234', 'scrypt:32768:8:1$Q4cPOP0slbTczkX4$899627b524b8344856b18e3357cca1698741f4d7ede92870efe50873f5a497740bca39ae07fa1bf5d03237db101e7e225af3a7f4c3710431610e09c40ead2c49'),
(3, 'Nusrat', 'nusratzahan6070@gmail.com', '12345678', '1234567', 'scrypt:32768:8:1$oXXZr7Y1ULW2fGzK$e9e8b13035063df2528d7fd929d408b81956e7fd1af4d37dc3040cc5f642055cf3256dec81535cd66440221e487f236bbe37f4dc3834aa5d6435802f34fa12c5');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `admin_id` (`admin_id`);

--
-- Indexes for table `cars`
--
ALTER TABLE `cars`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `carVIN_No` (`carVIN_No`),
  ADD KEY `pickup_point_id` (`pickup_point_id`);

--
-- Indexes for table `employee`
--
ALTER TABLE `employee`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `employee_id` (`employee_id`);

--
-- Indexes for table `pickup_points`
--
ALTER TABLE `pickup_points`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `admin`
--
ALTER TABLE `admin`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cars`
--
ALTER TABLE `cars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `employee`
--
ALTER TABLE `employee`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `pickup_points`
--
ALTER TABLE `pickup_points`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `cars`
--
ALTER TABLE `cars`
  ADD CONSTRAINT `cars_ibfk_1` FOREIGN KEY (`pickup_point_id`) REFERENCES `pickup_points` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
