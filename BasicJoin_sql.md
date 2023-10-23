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
SELECT H.HACKER_ID, H.NAME FROM SUBMISSIONS S 
JOIN HACKERS H 
ON S.HACKER_ID = H.HACKER_ID 
JOIN CHALLENGES C ON S.CHALLENGE_ID = C.CHALLENGE_ID
JOIN DIFFICULTY D ON C.DIFFICULTY_LEVEL = D.DIFFICULTY_LEVEL
WHERE S.SCORE = D.SCORE 
GROUP BY H.HACKER_ID, H.NAME 
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC, H.HACKER_ID;
```
#**[Ollivander's inventory](https://www.hackerrank.com/challenges/harry-potter-and-wands)**
```sql
SELECT W.ID, P.AGE, W.COINS_NEEDED, W.POWER FROM WANDS AS W 
JOIN WANDS_PROPERTY AS P
ON W.CODE = P.CODE
WHERE W.COINS_NEEDED = (SELECT MIN(COINS_NEEDED)
                       FROM WANDS W2 INNER JOIN WANDS_PROPERTY P2 
                       ON W2.CODE = P2.CODE 
                       WHERE P2.IS_EVIL = 0 AND P.AGE = P2.AGE AND W.POWER = W2.POWER)
ORDER BY W.POWER DESC, P.AGE DESC;
```
