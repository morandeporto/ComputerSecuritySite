# final_course_project
 
- DB - Using Microsoft SQL 2022
- Web page - using Flask (backend)
             using html+css (frontend)

## Setup / Run
### Prerequisites

1. Docker and its [prerequisites](https://docs.docker.com/desktop/install/windows-install/#system-requirements) are installed and **running**
```bash
docker ps
```
2. Python 3 is installed
```bash
python --version
```

### Setup / Run
> The setup of the program or re-running can be done automatically with the same file,`setup.py`. If you don't want to recreate the database, choose `n` for the question regarding removing the database.

1. Change your desired password in the `.env` file. Make sure your password meets [Microsoft's Password Policy](https://learn.microsoft.com/en-us/sql/relational-databases/security/password-policy?view=sql-server-ver16#password-complexity).

2. Run the setup file!
```bash
python setup.py
```
