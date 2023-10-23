#**[Population Census](https://www.hackerrank.com/challenges/asian-population)**
```sql
SELECT SUM(A.POPULATION) FROM CITY A 
INNER JOIN COUNTRY B
ON A.COUNTRYCODE = B.CODE 
WHERE B.CONTINENT = 'ASIA';
```
#**[African cities](https://www.hackerrank.com/challenges/african-cities)**
```sql
SELECT A.NAME FROM CITY A
INNER JOIN COUNTRY B
ON A.CountryCode = B.Code
WHERE B.CONTINENT = 'AFRICA';
```
#**[Average population of each continent](https://www.hackerrank.com/challenges/average-population-of-each-continent)**
```sql
SELECT A.CONTINENT, FLOOR(AVG(B.POPULATION)) 
FROM COUNTRY A
INNER JOIN CITY B
ON A.Code = B.CountryCode
GROUP BY A.CONTINENT;
```
#**[The Report](https://www.hackerrank.com/challenges/the-report)**
```sql
SELECT 
    CASE
    WHEN grades.grade < 8 THEN 'NULL'
    ELSE students.name
    END,
    grades.grade, students.marks
    FROM students, grades 
    WHERE students.marks >= grades.min_mark AND students.marks <= grades.max_mark
ORDER BY grades.grade DESC, students.name;
```
#**[Top Competitors](https://www.hackerrank.com/challenges/full-score)**
```sql

```
