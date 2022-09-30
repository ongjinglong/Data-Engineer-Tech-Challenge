SELECT customer.customerName AS Customer, COALESCE(SUM(car.carPrice),0) AS Spending
FROM customer LEFT OUTER JOIN sale ON sale.customerID=customer.customerID
LEFT OUTER JOIN car ON sale.carID=car.carID
GROUP BY customer.customerID, customer.customerName;