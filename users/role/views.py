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
    