-- Run automatically ONCE when the optional Docker volume is first created.
-- The official image creates portfolio@% and grants job_portal access first.
CREATE DATABASE IF NOT EXISTS inventory_management CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS product_api CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS inventory_management_test CHARACTER SET utf8mb4;
GRANT ALL PRIVILEGES ON inventory_management.* TO 'portfolio'@'%';
GRANT ALL PRIVILEGES ON product_api.* TO 'portfolio'@'%';
-- Separate disposable databases for automated integration tests.
GRANT ALL PRIVILEGES ON test_job_portal.* TO 'portfolio'@'%';
GRANT ALL PRIVILEGES ON test_product_api.* TO 'portfolio'@'%';
GRANT ALL PRIVILEGES ON inventory_management_test.* TO 'portfolio'@'%';
