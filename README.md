# ecoRide : plateforme de covoiturage eco-responsable 

Ce projet est une maquette d'application de covoiturage axée sur la sensibilisation écologique et visant à inciter les utilisateurs à participer à des trajets partagés.

### architecture
- **backend** : Flask, Postgres, Mongo
- **frontend** : Vite, HTMX, Alpinejs, Tailwindcss

The application is containerized using docker, and deployed to Linux based VPS.  
>  [visit the live app](https://vem-test.xyz)
  
credentials for admin access to the live app are provided in the 'copie a rendre'.
<br>
<br>
## environment configuration

for deploying the app, the repository needs to be cloned into a linux machine with docker installed.
Deploy VPS via a provider of your choice. Providers will usually provide a terminal to setup necessary configuration:

  * creation of super user, for use instead of root, with high access level via the 'sudo' command.
  * SSH configuration for connecting to the server via a terminal, and also necessary for accessing git servers among other.
  * installation of nginx and basic configuration for using it as a reverse proxy for applications hosted on the server.

I had a working Fedora based VPS, so my first step there was using the 'dnf' package manager to install docker:  
    ```bash
    $ sudo dnf install ./docker-desktop-x86_64.rpm
    ```
<br>
<br>
## application services
on the compose.yaml file three containers are defined for the different services.  
  
  * postgres : i chose the 'postgis/postgis:17-3.5' because of its GIS capabilities.
  * mongo : 7.0 version was the recommended for compatibility and stability.
  * flask app : python:3.12-slim image. see the Dockerfile at the root of the repository for the complete configuration.

### environment variables
Docker and Flask expect an '.env' file  at the root of the project: our database services rely on authentication, and we use API keys for a third-party mailing service. the 'environment.txt' file at the root of the project provides the template with the expected variables.
<br>
<br>
## ready to build and run
once the previous steps are completed, we are ready to build the containers. at the root of the directory (where the needed docker entry 'compose.yaml' lives):  
    ```bash
    $ docker compose build
    ```  
and then run the containers 'detached', i.e. in the background (-d):  
    ```bash
    $ docker compose up -d
    ```  
we can check logs on the flask app to verify everything is ok:  
    ```bash
    $ docker logs flask_ecoride
    ```  
<br>

**you should see something like**:
> [17:01:57] INFO     TIME NOW : {some date in 2025} - 17:01hs             main.py:52  
> [17:01:58] INFO     static ids loaded ~                               main.py:58  
> >INFO     "DB SEED : Database seeded." main.py:82  
>           INFO     BATCH SUMMARIES: {some number} summaries generated. main.py:95                                              
>            * Serving Flask app 'main'  
>            * Debug mode: off _internal.py:97  


**some important details are revealed here**:  
  
  * 'static ids loaded' this means postgres db is running and flask can talk to it.  
  * the faker module properly seeded the db with test data.  
  * debug mode is off for security reasons.  

now the application is ready and listening on the container's port 5000, which Docker attaches to the same port on the server, as configured in 'compose.yaml' :

    ```yaml
    services:
      flask_ecoride:
        ports:
          - "127.0.0.1:5000:5000"
    ```
<br>
nginx handles traffic from there, mapping the requests to the domain to the flask app.  
the domain is certified by certbot for TLS.  
