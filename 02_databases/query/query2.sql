SELECT car.carManufacturer as Manufacturer, COUNT(*) AS Sales
FROM car LEFT OUTER JOIN sale ON sale.carID=car.carID
WHERE sale.saleDate>=date_trunc('month', CURRENT_DATE)
GROUP BY car.carManufacturer
ORDER BY Sales DESC
LIMIT 3;