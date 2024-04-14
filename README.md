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

# Crear la carpeta "STATIC" y dentro "CSS" crearemos los css para cada HTML

# Creamos la carpeta "TEMPLATES" y dentro los archivos HTML

# Ahora preparaemos los codigos para nuestra app

# admin.py
```
    from django.contrib import admin
    from .models import Producto


    admin.site.register(Producto)
```

# forms.py
```
    from django import forms
    from django.contrib.auth.forms import UserCreationForm
    from django.contrib.auth.models import User
    from .models import PermisoProducto

    class SignUpForm(UserCreationForm):
        puede_agregar = forms.BooleanField(label='¿Puede agregar productos?', required=False)
        puede_cambiar = forms.BooleanField(label='¿Puede cambiar productos?', required=False)
        puede_eliminar = forms.BooleanField(label='¿Puede eliminar productos?', required=False)

        class Meta:
            model = User
            fields = ('username', 'password1', 'password2', 'puede_agregar', 'puede_cambiar', 'puede_eliminar')

        def save(self, commit=True):
            user = super().save(commit=False)
            if commit:
                user.save()
                permisos = PermisoProducto.objects.create(
                    user=user,
                    puede_agregar=self.cleaned_data.get('puede_agregar', False),
                    puede_cambiar=self.cleaned_data.get('puede_cambiar', False),
                    puede_eliminar=self.cleaned_data.get('puede_eliminar', False),
                )
            return user
```

# models.py
```
    from django.db import models
    from django.contrib.auth.models import User

    class Producto(models.Model):
        nombre = models.CharField(max_length=100)
        descripcion = models.TextField()
        precio = models.DecimalField(max_digits=10, decimal_places=2)
        imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

        def __str__(self):
            return self.nombre

    class PermisoProducto(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE)
        puede_agregar = models.BooleanField(default=False)
        puede_cambiar = models.BooleanField(default=False)
        puede_eliminar = models.BooleanField(default=False)
        puede_ver = models.BooleanField(default=True)
```

# urls.py
```
    from django.urls import path
    from django.contrib.auth import views
    from django.contrib.auth.views import LogoutView
    from django.conf import settings
    from django.conf.urls.static import static
    from . import views

    urlpatterns = [
        path('login/', views.login_view, name='login'),
        path('productos/', views.ProductoListView.as_view(), name='productos'),
        path('signup/', views.signup, name='signup'),
        path('logout/', views.CustomLogoutView.as_view(), name='logout'),
        path('agregar/', views.agregar_producto, name='agregar_producto'),
        path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
        path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    ]

    if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

# views.py
```
    from django.shortcuts import render, redirect, get_object_or_404
    from django.contrib.auth.decorators import login_required
    from django.contrib.auth import authenticate, login
    from django.contrib.auth.views import LogoutView
    from django.urls import reverse_lazy
    from django.http import HttpResponseRedirect
    from django.views.generic import ListView
    from .models import Producto, PermisoProducto
    from .forms import SignUpForm

    @login_required
    def login_view(request):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Verificar y crear permisos predeterminados para el usuario
                PermisoProducto.objects.get_or_create(user=user)
                return redirect('productos')
        return render(request, 'login.html')

    class ProductoListView(ListView):
        model = Producto
        template_name = 'productos.html'
        context_object_name = 'productos'

        def get_queryset(self):
            user = self.request.user
            permisos_usuario, _ = PermisoProducto.objects.get_or_create(user=user)
            if permisos_usuario.puede_ver:
                return Producto.objects.all()
            else:
                return Producto.objects.none()

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            user = self.request.user
            permisos_usuario, _ = PermisoProducto.objects.get_or_create(user=user)
            context['permisos'] = permisos_usuario
            return context

    def signup(request):
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
        else:
            form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

    class CustomLogoutView(LogoutView):
        def dispatch(self, request, *args, **kwargs):
            response = super().dispatch(request, *args, **kwargs)
            return HttpResponseRedirect(reverse_lazy('signup'))
        
    @login_required
    def agregar_producto(request):
        if request.method == 'POST':
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion')
            precio = request.POST.get('precio')
            imagen = request.FILES.get('imagen')
            
            producto = Producto(nombre=nombre, descripcion=descripcion, precio=precio, imagen=imagen)
            producto.save()
            return redirect('productos')
        else:
            return render(request, 'agregar_producto.html')

    @login_required
    def editar_producto(request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        if request.method == 'POST':
            producto.nombre = request.POST.get('nombre')
            producto.descripcion = request.POST.get('descripcion')
            producto.precio = request.POST.get('precio')
            producto.imagen = request.FILES.get('imagen') or producto.imagen
            
            producto.save()
            return redirect('productos')
        else:
            return render(request, 'editar_producto.html', {'producto': producto})

    @login_required
    def eliminar_producto(request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        if request.method == 'POST':
            producto.delete()
            return redirect('productos')
        else:
            return render(request, 'eliminar_producto.html', {'producto': producto})
```

# La configuracion final de nuestro setting.py seria la siguiente
```
    """
    Django settings for users project.

    Generated by 'django-admin startproject' using Django 5.0.4.

    For more information on this file, see
    https://docs.djangoproject.com/en/5.0/topics/settings/

    For the full list of settings and their values, see
    https://docs.djangoproject.com/en/5.0/ref/settings/
    """

    from pathlib import Path

    # Build paths inside the project like this: BASE_DIR / 'subdir'.
    BASE_DIR = Path(__file__).resolve().parent.parent


    # Quick-start development settings - unsuitable for production
    # See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = 'django-insecure-8!yrxav9w6yc*-)x%j14@i434jf77hczc^^l)=x5ij*bf3e6ui'

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    ALLOWED_HOSTS = []


    # Application definition

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'role',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'users.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'users.wsgi.application'


    # Database
    # https://docs.djangoproject.com/en/5.0/ref/settings/#databases

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


    # Password validation
    # https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    LOGIN_REDIRECT_URL = '/productos/'

    # Internationalization
    # https://docs.djangoproject.com/en/5.0/topics/i18n/

    LANGUAGE_CODE = 'es-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_TZ = True


    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/5.0/howto/static-files/

    STATIC_URL = 'static/'

    # Configuración de archivos multimedia
    MEDIA_URL = ''
    MEDIA_ROOT = BASE_DIR / ''

    # Default primary key field type
    # https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

    DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```


