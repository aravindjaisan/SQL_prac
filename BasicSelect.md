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
