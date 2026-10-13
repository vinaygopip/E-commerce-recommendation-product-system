from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from cart.models import Cart
from orders.models import Order

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Transfer guest cart if session exists
            session_key = request.session.session_key
            if session_key:
                guest_cart = Cart.objects.filter(session_key=session_key).first()
                if guest_cart:
                    guest_cart.user = user
                    guest_cart.session_key = None
                    guest_cart.save()

            login(request, user)
            messages.success(request, f"Welcome to ShopAI, {user.first_name or user.username}! Your account has been created.")
            return redirect('home')
    else:
        form = UserRegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                # Merge guest cart to user cart
                session_key = request.session.session_key
                login(request, user)

                if session_key:
                    guest_cart = Cart.objects.filter(session_key=session_key).first()
                    user_cart, _ = Cart.objects.get_or_create(user=user)
                    if guest_cart and guest_cart != user_cart:
                        for g_item in guest_cart.items.all():
                            u_item, created = user_cart.items.get_or_create(
                                product=g_item.product,
                                defaults={'quantity': g_item.quantity}
                            )
                            if not created:
                                u_item.quantity += g_item.quantity
                                u_item.save()
                        guest_cart.delete()

                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)
