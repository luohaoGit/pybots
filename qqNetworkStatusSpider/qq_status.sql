CREATE TABLE `qq_status` (
    `id` bigint(20) NOT NULL DEFAULT '0',
    `status` varchar(20) DEFAULT NULL,
    `time` datetime DEFAULT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;