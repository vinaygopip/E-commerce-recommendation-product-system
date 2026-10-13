/**
 * ShopSmart - Interactive E-Commerce Client Scripts
 * Handles AJAX Wishlist toggles, Cart additions, and dynamic UI feedback.
 */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Notification Toast Generator
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.bottom = '24px';
        container.style.right = '24px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const bgClass = type === 'success' ? '#10b981' : (type === 'error' ? '#ef4444' : '#2563eb');
    toast.style.background = bgClass;
    toast.style.color = '#ffffff';
    toast.style.padding = '12px 20px';
    toast.style.borderRadius = '10px';
    toast.style.boxShadow = '0 10px 15px -3px rgba(0,0,0,0.1)';
    toast.style.fontSize = '0.9rem';
    toast.style.fontWeight = '500';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '8px';
    toast.style.animation = 'fadeInUp 0.3s ease forwards';
    toast.innerHTML = `<i class="bi ${type === 'success' ? 'bi-check-circle-fill' : 'bi-info-circle-fill'}"></i> <span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 3500);
}

// Global AJAX Wishlist Toggle
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-wishlist-ajax').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const url = `/recommendations/wishlist/toggle/${productId}/`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(res => {
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }
                return res.json();
            })
            .then(data => {
                if (data && data.status === 'success') {
                    const icon = this.querySelector('i');
                    if (data.added) {
                        this.classList.add('active');
                        if (icon) {
                            icon.classList.remove('bi-heart');
                            icon.classList.add('bi-heart-fill');
                        }
                    } else {
                        this.classList.remove('active');
                        if (icon) {
                            icon.classList.remove('bi-heart-fill');
                            icon.classList.add('bi-heart');
                        }
                    }

                    // Update navbar badge counter
                    const badge = document.getElementById('nav-wishlist-badge');
                    if (badge) {
                        badge.textContent = data.wishlist_count;
                        badge.style.display = data.wishlist_count > 0 ? 'inline-block' : 'none';
                    }

                    showToast(data.message, data.added ? 'success' : 'info');
                }
            })
            .catch(err => {
                console.error("Wishlist error:", err);
            });
        });
    });

    // Quick Add to Cart via AJAX
    document.querySelectorAll('.btn-cart-ajax').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const quantity = this.getAttribute('data-quantity') || 1;
            const url = `/cart/add/${productId}/`;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `quantity=${quantity}`
            })
            .then(res => res.json())
            .then(data => {
                if (data && data.status === 'success') {
                    const badge = document.getElementById('nav-cart-badge');
                    if (badge) {
                        badge.textContent = data.cart_count;
                        badge.style.display = data.cart_count > 0 ? 'inline-block' : 'none';
                    }
                    showToast(data.message, 'success');
                }
            })
            .catch(err => {
                console.error("Cart error:", err);
            });
        });
    });
});
