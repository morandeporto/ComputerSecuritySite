import os
import subprocess
import sys
import venv
import time

def create_virtual_environment():
    print("Creating virtual environment...")
    venv.create('env', with_pip=True)

def install_requirements():
    print("Installing requirements...")
    pip_path = os.path.join('env', 'Scripts', 'pip') if os.name == 'nt' else os.path.join('env', 'bin', 'pip')
    subprocess.run([pip_path, "install", "-r", "requirements.txt"])

def run_in_virtual_environment():
    print("Starting new shell session in virtual environment...")
    venv_python = os.path.join('env', 'Scripts', 'python') if os.name == 'nt' else os.path.join('env', 'bin', 'python')
    subprocess.run(" ".join([venv_python] + sys.argv + ['--venv']), shell=True)

def load_environment_variables():
    print("Loading environment variables...")
    from dotenv import load_dotenv
    load_dotenv()

def create_docker_client():
    print("Creating Docker client...")
    import docker
    return docker.from_env()

def remove_existing_container(docker_client):
    print("Removing existing 'database' container...")
    container = docker_client.containers.get('database')
    container.stop()
    container.remove()

def build_and_run_container(docker_client, password):
    print("Building 'database' image...")
    docker_client.images.build(path='database', tag='database')
    print("Running 'database' container...")
    docker_client.containers.run(
        'database',
        environment={"MSSQL_SA_PASSWORD": password},
        ports={'1433/tcp': 1433},
        detach=True,
        name='database'
    )

def wait_for_database():
    print("Waiting for the database to start... (30 seconds)")
    time.sleep(30)

def execute_initialization_script(docker_client, password):
    print("Executing initialization script...")
    docker_client.containers.get('database').exec_run(
        f"/opt/mssql-tools/bin/sqlcmd -S 127.0.0.1 -U sa -P {password} -i initialization.sql"
    )

def run_backend():
    print("Running backend...")
    python_path = os.path.join('env', 'Scripts', 'python') if os.name == 'nt' else os.path.join('env', 'bin', 'python')
    subprocess.run([python_path, "backend.py"])

def main():
    if '--venv' not in sys.argv:
        print("Checking virtual environment...")
        if not os.path.exists('env'):
            create_virtual_environment()
            install_requirements()
        run_in_virtual_environment()
        sys.exit()

    load_environment_variables()
    password = os.getenv('MSSQL_SA_PASSWORD')
    docker_client = create_docker_client()

    container_exists = any(container.name == 'database' for container in docker_client.containers.list(all=True))

    if container_exists:
        user_input = input("A container named 'database' already exists. Do you want to remove it? (y/n): ")
        if user_input.lower() == 'y':
            remove_existing_container(docker_client)
            build_and_run_container(docker_client, password)
            wait_for_database()
            execute_initialization_script(docker_client, password)
        elif user_input.lower() == 'n':
            print("Using the existing 'database' container.")
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
            sys.exit()
    else:
        build_and_run_container(docker_client, password)
        wait_for_database()
        execute_initialization_script(docker_client, password)

    run_backend()

if __name__ == "__main__":
    main()
    