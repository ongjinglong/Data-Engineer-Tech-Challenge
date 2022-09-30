BEGIN;

CREATE TABLE IF NOT EXISTS salesPerson (
	salesPersonID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    salesPersonName VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS customer (
	customerID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customerName VARCHAR(100) NOT NULL,
    customerPhone VARCHAR(15) NOT NULL
);

CREATE TABLE IF NOT EXISTS car (
    carID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	carManufacturer VARCHAR(100) NOT NULL,
	carModelName VARCHAR(100) NOT NULL,
    carSerialNumber VARCHAR(100) NOT NULL,
    carWeight NUMERIC NOT NULL,
    carPrice NUMERIC NOT NULL,
    CHECK (carWeight > 0),
    CHECK (carPrice > 0),
    UNIQUE(carManufacturer, carModelName, carSerialNumber)
);

CREATE TABLE IF NOT EXISTS sale (
    saleID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    saleDate TIMESTAMP DEFAULT NOW(),
    customerID INT NOT NULL REFERENCES customer(customerID),
    salesPersonID INT NOT NULL REFERENCES salesPerson(salesPersonID),
    carID INT NOT NULL REFERENCES car(carID),
    CHECK (saleDate <= NOW())
);

END;