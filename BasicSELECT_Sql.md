#**[Revising the Select Query-I](https://www.hackerrank.com/challenges/revising-the-select-query)**
```sql
SELECT * FROM CITY WHERE COUNTRYCODE = 'USA' AND POPULATION > 100000;
```
#**[Revising the Select Query-II](https://www.hackerrank.com/challenges/revising-the-select-query)**
```sql
SELECT NAME FROM CITY WHERE COUNTRYCODE = 'USA' AND POPULATION > 120000;
```
#**[Select All Sql](https://www.hackerrank.com/challenges/select-all-sql)**
```sql
SELECT * FROM CITY;
```
#**[Select by ID](https://www.hackerrank.com/challenges/select-by-id)**
```sql
SELECT * FROM CITY WHERE ID = 1661;
```
#**[Japanese Cities' Atrributes](https://www.hackerrank.com/challenges/japanese-cities-attributes)**
```sql
SELECT * FROM CITY WHERE COUNTRYCODE = 'JPN';
```
#**[Japanese Cities' Names](https://www.hackerrank.com/challenges/japanese-cities-name)**
```sql
SELECT NAME FROM CITY WHERE COUNTRYCODE = 'JPN';
```
#**[Weather Observation Station-1](https://www.hackerrank.com/challenges/weather-observation-station-1)**
```sql
SELECT CITY,STATE FROM STATION;
```
#**[Weather Observation Station-3](https://www.hackerrank.com/challenges/weather-observation-station-3)**
```sql
SELECT DISTINCT CITY FROM STATION WHERE MOD(ID,2)=0 ORDER BY CITY ASC;
```
#**[Weather Observation Station-4](https://www.hackerrank.com/challenges/weather-observation-station-4)**
```sql
SELECT COUNT(CITY) - COUNT(DISTINCT CITY) FROM STATION;
```
#**[Weather Observation Station-5](https://www.hackerrank.com/challenges/weather-observation-station-5)**
```sql
SELECT CITY, LENGTH(CITY) FROM STATION ORDER BY LENGTH(CITY)ASC, CITY LIMIT 1;
SELECT CITY, LENGTH(CITY) FROM STATION ORDER BY LENGTH(CITY) DESC, CITY LIMIT 1;
```
#**[Weather Observation Station-6](https://www.hackerrank.com/challenges/weather-observation-station-6)**
```sql
SELECT DISTINCT CITY FROM STATION 
WHERE CITY LIKE 'a%' OR CITY LIKE 'e%' OR CITY LIKE 'i%' OR CITY LIKE 'o%' OR CITY LIKE'u%' ORDER BY CITY;
```
#**[Weather Observation Station-7](https://www.hackerrank.com/challenges/weather-observation-station-7)**
```sql
SELECT DISTINCT CITY FROM STATION 
WHERE CITY LIKE '%a' OR CITY LIKE '%e' OR CITY LIKE '%i' OR CITY LIKE '%o' OR CITY LIKE'%u' ORDER BY CITY;
```
#**[Weather Observation Station-8](https://www.hackerrank.com/challenges/weather-observation-station-8)**
```sql
SELECT DISTINCT CITY FROM STATION 
WHERE (CITY LIKE 'A%' OR CITY LIKE 'E%' OR CITY LIKE 'I%' OR CITY LIKE 'O%' OR CITY LIKE 'U%') 
AND (CITY LIKE '%A' OR CITY LIKE '%E' OR CITY LIKE '%I' OR CITY LIKE '%O' OR CITY LIKE '%U') ORDER BY CITY;
```
#**[Weather Observation Station-9](https://www.hackerrank.com/challenges/weather-observation-station-9)**
```sql
SELECT DISTINCT CITY FROM STATION 
WHERE upper(SUBSTR(CITY,1,1)) NOT IN ('A','E','I','O','U'); 
```
#**[Weather Observation Station-10](https://www.hackerrank.com/challenges/weather-observation-station-10)**
```sql
SELECT DISTINCT CITY FROM STATION WHERE upper(SUBSTR(CITY,LENGTH(CITY),1)) NOT IN ('A','E','I','O','U');
```
#**[Weather Observation Station-11](https://www.hackerrank.com/challenges/weather-observation-station-11)**
```sql
SELECT DISTINCT CITY FROM STATION 
WHERE lower(SUBSTR(CITY,1,1)) NOT IN ('a','e','i','o','u')
OR lower(SUBSTR(CITY,LENGTH(CITY),1)) NOT IN ('a','e','i','o','u'); 
```
#**[Weather Observation Station-12](https://www.hackerrank.com/challenges/weather-observation-station-12)**
```sql
SELECT DISTINCT CITY FROM STATION 
WHERE lower(SUBSTR(CITY,1,1)) NOT IN ('a','e','i','o','u')
AND lower(SUBSTR(CITY,LENGTH(CITY),1)) NOT IN ('a','e','i','o','u'); 
```
#**[More than 75 marks](https://www.hackerrank.com/challenges/more-than-75-marks)**
```sql
SELECT NAME FROM STUDENTS WHERE MARKS > 75 ORDER BY RIGHT(NAME,3),ID;
```
#**[Name of employees](https://www.hackerrank.com/challenges/name-of-employees)**
```sql
SELECT NAME FROM EMPLOYEE ORDER BY NAME;
```
#**[Salary of employees](https://www.hackerrank.com/challenges/salary-of-employees)**
```sql
SELECT NAME FROM EMPLOYEE WHERE SALARY > 2000 AND MONTHS < 10 ORDER BY EMPLOYEE_ID;
```
