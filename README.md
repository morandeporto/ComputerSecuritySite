# final_course_project
 
- DB - Using Microsoft SQL 2022
- Web page - using Flask (backend)
             using html+css (frontend)



## Docker Database Setup
1. ** Change directory into the database folder **
```bash
cd database
```
2.  **Build  the  Docker  image**
```bash
docker build -t database .
```
3.  **Set  the  `sa`  password  as  an  environment  variable**
```bash
export  MSSQL_SA_PASSWORD=your-password
```
4.  **Run  the  Docker  image  as  a  container**
```bash
sudo docker run \
-e  "MSSQL_SA_PASSWORD=${MSSQL_SA_PASSWORD}"  \
-p  1433:1433 \
--name database \
-d database
```
5.  **Verify  the  database  is  listening  on  port  1433**
```bash
sudo lsof -nP  -i:1433
```
6.  **Run  the  initialization  SQL  file  to  set  up  the  database  and  tables**
```bash
docker exec -it database \
/opt/mssql-tools/bin/sqlcmd \
-S  127.0.0.1 \
-U sa \
-P  ${MSSQL_SA_PASSWORD}  \
-i initialization.sql
```

