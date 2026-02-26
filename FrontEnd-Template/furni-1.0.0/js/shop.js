// Shop Cart Functions
class CartManager {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('cart')) || [];
        this.init();
    }

    init() {
        this.updateCartCount();
        this.setupProductClickEvents();
    }

    updateCartCount() {
        const cartCount = this.cart.reduce((total, item) => total + item.quantity, 0);
        const countElement = document.getElementById('cart-count');
        if (countElement) {
            countElement.textContent = cartCount;
        }
    }

    setupProductClickEvents() {
        document.querySelectorAll('.product-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.product-buttons')) {
                    const productData = JSON.parse(item.getAttribute('data-product'));
                    this.addToCart(productData);
                }
            });
        });
    }

    addToCart(product) {
        const existingItem = this.cart.find(item => item.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += 1;
            existingItem.total = existingItem.price * existingItem.quantity;
            this.showNotification(`${product.name} quantity updated!`, 'info');
        } else {
            const newItem = {
                ...product,
                quantity: 1,
                total: product.price
            };
            this.cart.push(newItem);
            this.showNotification(`${product.name} added to cart!`, 'success');
        }
        
        this.saveCart();
        this.updateCartCount();
        this.addVisualFeedback(product.id);
    }

    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.cart));
    }

    showNotification(message, type = 'info') {
        const existingNotifications = document.querySelectorAll('.cart-notification');
        existingNotifications.forEach(notification => notification.remove());
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show cart-notification`;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-shopping-cart me-2"></i>
                <div>${message}</div>
                <button type="button" class="btn-close ms-auto" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    addVisualFeedback(productId) {
        const productItem = document.querySelector(`[data-product*='"id":${productId}']`);
        if (productItem) {
            productItem.style.animation = 'none';
            setTimeout(() => {
                productItem.style.animation = 'bounce 0.5s';
            }, 10);
            
            setTimeout(() => {
                productItem.style.animation = '';
            }, 500);
        }
    }

    getCartTotalItems() {
        return this.cart.reduce((total, item) => total + item.quantity, 0);
    }

    getCartTotalPrice() {
        return this.cart.reduce((total, item) => total + item.total, 0);
    }

    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
        this.updateCartCount();
        this.showNotification('Item removed from cart', 'warning');
    }

    clearCart() {
        if (confirm('Are you sure you want to clear your cart?')) {
            this.cart = [];
            this.saveCart();
            this.updateCartCount();
            this.showNotification('Cart cleared', 'info');
        }
    }

    // Quick buy now function
    buyNow(productId) {
        const productItem = document.querySelector(`[data-product*='"id":${productId}']`);
        if (productItem) {
            const productData = JSON.parse(productItem.getAttribute('data-product'));
            
            // Clear cart and add only this product
            this.cart = [{
                ...productData,
                quantity: 1,
                total: productData.price
            }];
            
            this.saveCart();
            this.updateCartCount();
            
            // Redirect to checkout
            window.location.href = 'checkout.html';
        }
    }
}

// Initialize cart manager
const cartManager = new CartManager();

// Global functions for HTML onclick events
function buyNow(productId) {
    cartManager.buyNow(productId);
}

function viewCart() {
    window.location.href = 'cart.html';
}

function clearCart() {
    cartManager.clearCart();
}