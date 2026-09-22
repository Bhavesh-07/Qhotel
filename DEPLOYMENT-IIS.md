# QHotels IIS 8.5 Deployment

This project is a Flask application deployed to IIS using `wfastcgi`.

## 1. Prepare the server

- Install Python 3.10 or 3.11 (64-bit).
- In Windows Server, enable IIS with the `CGI` feature.
- Create a site folder, for example: `C:\sites\qhotels`
- Create a logs folder: `C:\sites\qhotels\logs`

## 2. Upload the project

Copy the full project to:

`C:\sites\qhotels`

## 3. Create the virtual environment

```powershell
cd C:\sites\qhotels
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m wfastcgi enable
```

## 4. Create the database

Create a MySQL database and run:

```sql
SOURCE C:/sites/qhotels/schema.sql;
```

Create a dedicated MySQL user and update the values in `web.config`.

## 5. Update production values

Edit `web.config` and replace these placeholders:

- `FLASK_SECRET_KEY`
- `ADMIN_BOOTSTRAP_USERNAME`
- `ADMIN_BOOTSTRAP_PASSWORD`
- `DB_USER`
- `DB_PASSWORD`

Also update the Python and project paths if your live folder is different from `C:\sites\qhotels`.

The bootstrap admin credentials are used only to create the first admin record in the database. After the first successful login, change or remove the bootstrap password from `web.config`.

## 6. Configure IIS

- Create an Application Pool
- Set `.NET CLR version` to `No Managed Code`
- Set `Managed pipeline mode` to `Integrated`
- Point the IIS site to `C:\sites\qhotels`

Grant permissions:

- `Read & Execute` on the project folder for the IIS App Pool identity
- `Modify` on `C:\sites\qhotels\logs`

## 7. Test the site

After starting the site, test:

- `/`
- `/contact`
- `/submit_contact`
- `/login`
- `/admin/submissions`

If the app fails, check:

- IIS site bindings
- `C:\sites\qhotels\logs\wfastcgi.log`
- Windows Event Viewer

## 8. SMTP setup

SMTP is stored in the `settings` table. After login, add these values:

- `smtp_host`
- `smtp_port`
- `smtp_user`
- `smtp_pass`
- `email_from`
- `email_to`
- `email_template`

## 9. Recommended hardening

- Use HTTPS and install a valid SSL certificate
- Keep `SESSION_COOKIE_SECURE=true`
- Replace the admin password immediately
- Use a non-root MySQL user
- Restrict access to `/login` if possible by IP or VPN
- Remove or randomize `ADMIN_BOOTSTRAP_PASSWORD` after the first admin user is created
