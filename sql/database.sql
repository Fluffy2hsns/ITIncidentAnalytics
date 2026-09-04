-- Создание базы данных
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'ITIncidentAnalytics')
BEGIN
    CREATE DATABASE ITIncidentAnalytics;
END;
GO

USE ITIncidentAnalytics;
GO