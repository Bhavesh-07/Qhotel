# IIS 8.5 Upload Checklist

Use this checklist on the live Windows server.

## A. Server prerequisites

Run PowerShell as Administrator:

```powershell
Install-WindowsFeature Web-Server,Web-CGI -IncludeManagementTools
```

Install:

- Python 3.10 or 3.11 x64
- MySQL Server or access to an external MySQL server

## B. Upload application files

Create folders:

```powershell
New-Item -ItemType Directory -Force C:\sites\qhotels
New-Item -ItemType Directory -Force C:\sites\qhotels\logs
```

Upload the project contents into:

`C:\sites\qhotels`

## C. Python environment

```powershell
cd C:\sites\qhotels
python -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m wfastcgi enable
```

## D. Database setup

Create the MySQL database user with limited permissions, then run:

```sql
SOURCE C:/sites/qhotels/schema.sql;
```

Example grants:

```sql
CREATE USER 'qhotels_user'@'localhost' IDENTIFIED BY 'StrongPasswordHere';
GRANT SELECT, INSERT, UPDATE, DELETE ON qhotels_db.* TO 'qhotels_user'@'localhost';
FLUSH PRIVILEGES;
```

## E. Update web.config

Open [web.config](/C:/wamp64/www/Qhotels--Live/web.config:1) and set:

- correct `scriptProcessor` Python and `wfastcgi.py` paths
- correct `PYTHONPATH`
- correct `WSGI_LOG`
- real `FLASK_SECRET_KEY`
- real `ADMIN_BOOTSTRAP_USERNAME`
- real `ADMIN_BOOTSTRAP_PASSWORD`
- real `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`

If your live path is different, update every `C:\sites\qhotels` reference.

## F. IIS site and app pool

Create an Application Pool:

- Name: `QHotelsPool`
- .NET CLR Version: `No Managed Code`
- Managed Pipeline Mode: `Integrated`

Create the IIS site:

- Site name: `QHotels`
- Physical path: `C:\sites\qhotels`
- Bind your domain and port 80/443

## G. Permissions

Give IIS access:

```powershell
icacls C:\sites\qhotels /grant "IIS AppPool\QHotelsPool:(OI)(CI)(RX)"
icacls C:\sites\qhotels\logs /grant "IIS AppPool\QHotelsPool:(OI)(CI)(M)"
```

## H. First start and smoke test

Recycle the app pool, then test:

- home page
- contact form
- `/login`
- `/admin/submissions`

After first login:

- verify the bootstrap admin account was created in `admin_users`
- remove or replace `ADMIN_BOOTSTRAP_PASSWORD` in `web.config`

## I. HTTPS and DNS

- point domain DNS to the server IP
- bind SSL certificate in IIS
- force HTTPS if needed

## J. Troubleshooting

Check:

- `C:\sites\qhotels\logs\wfastcgi.log`
- IIS site status
- Application Pool status
- Windows Event Viewer
- MySQL connectivity from the server
