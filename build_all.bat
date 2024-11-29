@echo off

REM Navigate to the customers service directory, build and compose
echo Building and starting customers service...
cd customer_service
docker-compose up --build -d
cd ..

REM Navigate to the inventory service directory, build and compose
echo Building and starting inventory service...
cd inventory_service
docker-compose up --build -d
cd ..

REM Navigate to the sales service directory, build and compose
echo Building and starting sales service...
cd sales_service
docker-compose up --build -d
cd ..

echo All services are up and running.
pause