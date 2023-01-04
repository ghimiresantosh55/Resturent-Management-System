# rims-ng-backend

RIMS application with Inventory, Staff Information System, Logging, Multiple branch, Permission etc

### Packages used in this project

1. Djano=3.1.9
2. djangorestframework --> latest version till this date
3. django-filter --> for filters and sorting --> latest version till this date
4. psycopg2 --> for using postgres --> latest version till this date
5. django-simple-history --> to save log to the separate database --> latest version till this date
6. djngo-environ --> to create environment variables --> latest version till this date
7. nepali-datetime==1.0.7 --> Add support for BS, nepali date --> latest version till this date
8. djangorestframework-simplejwt==4.7.1 --> JSON web token for djangorestframework--> latest version till this date
9. django-cors-headers==3.7.0 --> for CSRF tokens --> latest version till this date
10. django-rest-resetpassword==0.12 --> for password forget email
11. ipinfo-django --> for tracking user location
12. drf-spectacular --> for documentation

### customizations 
custom_jwt_authentication.py ---> for Tenant aware JWT authentication
*_permissions.py --> for custom permission for views
tenant_manage.py --> for Tenant aware manage.py ( used to create super users in tenents)

