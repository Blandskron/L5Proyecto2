# L5Proyecto2

# Instalar entorno virtual y activar el entorno
```
    python -m venv venv
    venv\Scripts\activate
```

# Instalar Django
```
    pip install django
```

# Crear proyecto Django
```
    django-admin startproject users
    cd users
```

# Crear aplicacion 
```
   python manage.py startapp role
```

# Registrar aplicacion en el setting.py
```
    INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'role',
]
```

# Instalamos Pillow para manejo de imagenes
```
    python -m pip install Pillow
```



