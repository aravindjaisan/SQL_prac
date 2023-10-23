#**[Weather observation station-17](https://www.hackerrank.com/challenges/weather-observation-station-17)**
```sql
SELECT ROUND(LONG_W,4)
FROM STATION
WHERE LAT_N = ( SELECT MIN(LAT_N) FROM STATION WHERE LAT_N > 38.7780);
```
#**[Weather observation station-18](https://www.hackerrank.com/challenges/weather-observation-station-18)**
```sql
SELECT ROUND(ABS(MAX(LAT_N) - MIN(LAT_N)) + ABS(MAX(LONG_W) - MIN(LONG_W)), 4) FROM STATION;
```
#**[Weather observation station-19](https://www.hackerrank.com/challenges/weather-observation-station-19)**
```sql
SELECT ROUND(SQRT(POWER(MAX(LAT_N) - MIN(LAT_N), 2) + POWER(MAX(LONG_W) - MIN(LONG_W), 2)), 4)
FROM STATION;
```
#**[Weather observation station-20](https://www.hackerrank.com/challenges/weather-observation-station-20)**
```sql
SELECT ROUND(a.LAT_N,4)
FROM (SELECT LAT_N FROM STATION ORDER BY LAT_N LIMIT 250)a
ORDER BY LAT_N DESC
LIMIT 1;
```
