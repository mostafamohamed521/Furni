// Cart Manager Class
class CartManager {
    constructor() {
        // استخدم cart من localStorage ولو فاضية استخدم array فاضي
        this.cart = JSON.parse(localStorage.getItem('cart')) || [];
        this.discount = 0;
        this.couponApplied = false;
        this.init();
    }

    init() {
        this.updateCartDisplay();
        this.calculateTotals();
        this.setupEventListeners();
        
        // شوف لو العربة فاضية
        if (this.cart.length === 0) {
            console.log('Cart is empty, loading default items...');
            this.loadDefaultCartItems();
        }
    }

    loadDefaultCartItems() {
        // فقط لو العربة فاضية تماماً
        if (this.cart.length === 0) {
            // ممكن تضيف هنا منتجات افتراضية للعرض
            console.log('No items in cart');
        }
    }

    updateCartDisplay() {
        const cartItemsContainer = document.getElementById('cart-items');
        const emptyCartMessage = document.getElementById('empty-cart-message');
        
        if (!cartItemsContainer) return;
        
        if (this.cart.length === 0) {
            // لو العربة فاضية، نظهر الرسالة
            cartItemsContainer.innerHTML = '';
            if (emptyCartMessage) {
                emptyCartMessage.style.display = '';
            }
            return;
        }
        
        // نخفي رسالة العربة الفاضية
        if (emptyCartMessage) {
            emptyCartMessage.style.display = 'none';
        }
        
        let cartHTML = '';
        
        this.cart.forEach(item => {
            cartHTML += `
            <tr id="item-${item.id}">
                <td class="product-thumbnail">
                    <img src="${item.image || 'images/product-1.png'}" alt="${item.name}" class="img-fluid" style="width: 80px;">
                </td>
                <td class="product-name">
                    <h2 class="h5 text-black">${item.name}</h2>
                </td>
                <td class="product-price">$${item.price ? item.price.toFixed(2) : '0.00'}</td>
                <td class="product-quantity">
                    <div class="input-group mb-3 d-flex align-items-center quantity-container" style="max-width: 120px;">
                        <div class="input-group-prepend">
                            <button class="btn btn-outline-black decrease" type="button" onclick="cartManager.decreaseQuantity(${item.id})">&minus;</button>
                        </div>
                        <input type="number" class="form-control text-center quantity-amount" 
                               id="quantity-${item.id}" 
                               value="${item.quantity || 1}" 
                               min="1" 
                               max="10"
                               onchange="cartManager.updateItemQuantity(${item.id}, this.value)">
                        <div class="input-group-append">
                            <button class="btn btn-outline-black increase" type="button" onclick="cartManager.increaseQuantity(${item.id})">&plus;</button>
                        </div>
                    </div>
                </td>
                <td class="product-total" id="item-total-${item.id}">$${((item.price || 0) * (item.quantity || 1)).toFixed(2)}</td>
                <td class="product-remove">
                    <button class="btn btn-black btn-sm" onclick="cartManager.removeItem(${item.id})">
                        <i class="fas fa-times"></i>
                    </button>
                </td>
            </tr>
            `;
        });
        
        cartItemsContainer.innerHTML = cartHTML;
    }

    increaseQuantity(itemId) {
        const item = this.cart.find(item => item.id === itemId);
        if (item) {
            item.quantity = (item.quantity || 1) + 1;
            if (item.quantity > 10) item.quantity = 10;
            item.total = (item.price || 0) * item.quantity;
            this.saveCart();
            this.updateItemDisplay(itemId);
            this.calculateTotals();
        }
    }

    decreaseQuantity(itemId) {
        const item = this.cart.find(item => item.id === itemId);
        if (item && (item.quantity || 1) > 1) {
            item.quantity = (item.quantity || 1) - 1;
            item.total = (item.price || 0) * item.quantity;
            this.saveCart();
            this.updateItemDisplay(itemId);
            this.calculateTotals();
        }
    }

    updateItemQuantity(itemId, newQuantity) {
        let quantity = parseInt(newQuantity);
        if (isNaN(quantity) || quantity < 1) {
            quantity = 1;
        }
        if (quantity > 10) {
            quantity = 10;
        }
        
        const item = this.cart.find(item => item.id === itemId);
        if (item) {
            item.quantity = quantity;
            item.total = (item.price || 0) * quantity;
            this.saveCart();
            this.updateItemDisplay(itemId);
            this.calculateTotals();
        }
    }

    updateItemDisplay(itemId) {
        const item = this.cart.find(item => item.id === itemId);
        if (item) {
            const quantityInput = document.getElementById(`quantity-${itemId}`);
            const totalElement = document.getElementById(`item-total-${itemId}`);
            
            if (quantityInput) quantityInput.value = item.quantity || 1;
            if (totalElement) totalElement.textContent = `$${((item.price || 0) * (item.quantity || 1)).toFixed(2)}`;
        }
    }

    removeItem(itemId) {
        if (confirm('Are you sure you want to remove this item from your cart?')) {
            this.cart = this.cart.filter(item => item.id !== itemId);
            this.saveCart();
            this.updateCartDisplay();
            this.calculateTotals();
            this.showNotification('Item removed from cart', 'warning');
            
            // عدل عداد العربة في كل الصفحات
            this.updateCartCountGlobally();
        }
    }

    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.cart));
        this.updateCartCountGlobally();
    }

    updateCartCountGlobally() {
        // عدل عداد العربة في كل نوافذ المتصفح المفتوحة
        const cartCount = this.cart.reduce((total, item) => total + (item.quantity || 1), 0);
        
        // تحديث العداد في الصفحة الحالية
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = cartCount;
        }
        
        // إرسال إشعار لجميع التبويبات المفتوحة
        if (typeof BroadcastChannel !== 'undefined') {
            const channel = new BroadcastChannel('cart_channel');
            channel.postMessage({
                type: 'cart_updated',
                count: cartCount
            });
            channel.close();
        }
    }

    calculateTotals() {
        let subtotal = 0;
        
        this.cart.forEach(item => {
            subtotal += (item.total || ((item.price || 0) * (item.quantity || 1)));
        });
        
        let total = subtotal - this.discount;
        
        // Update display
        const subtotalElement = document.getElementById('subtotal');
        const totalElement = document.getElementById('total');
        const discountRow = document.getElementById('discount-row');
        const discountElement = document.getElementById('discount');
        
        if (subtotalElement) subtotalElement.textContent = `$${subtotal.toFixed(2)}`;
        if (totalElement) totalElement.textContent = `$${total.toFixed(2)}`;
        
        // Show/hide discount row
        if (discountRow && discountElement) {
            if (this.discount > 0) {
                discountRow.style.display = '';
                discountElement.textContent = `-$${this.discount.toFixed(2)}`;
            } else {
                discountRow.style.display = 'none';
            }
        }
    }

    applyCoupon() {
        const couponCode = document.getElementById('coupon')?.value.trim().toUpperCase();
        const couponMessage = document.getElementById('coupon-message');
        
        if (!couponMessage) return;
        
        couponMessage.innerHTML = '';
        
        const validCoupons = {
            'SAVE10': 0.10,
            'SAVE20': 0.20,
            'FURNITURE25': 0.25
        };
        
        if (couponCode in validCoupons) {
            if (this.couponApplied) {
                couponMessage.innerHTML = '<div class="alert alert-warning">Coupon already applied!</div>';
                return;
            }
            
            const discountPercentage = validCoupons[couponCode];
            let subtotal = 0;
            this.cart.forEach(item => {
                subtotal += (item.total || ((item.price || 0) * (item.quantity || 1)));
            });
            
            this.discount = subtotal * discountPercentage;
            this.couponApplied = true;
            couponMessage.innerHTML = `<div class="alert alert-success">Coupon applied! You saved $${this.discount.toFixed(2)}</div>`;
            this.calculateTotals();
            
            // Disable coupon input and button
            const couponInput = document.getElementById('coupon');
            const couponButton = document.querySelector('#coupon-section .btn-black');
            if (couponInput) couponInput.disabled = true;
            if (couponButton) couponButton.disabled = true;
            
        } else {
            couponMessage.innerHTML = '<div class="alert alert-danger">Invalid coupon code!</div>';
        }
    }

    updateCart() {
        this.showNotification('Cart updated successfully!', 'success');
        this.saveCart();
    }

    proceedToCheckout() {
        if (this.cart.length === 0) {
            alert('Your cart is empty! Please add items before checkout.');
            return;
        }
        
        this.saveCart();
        window.location.href = 'checkout.html';
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.cart-notification');
        existingNotifications.forEach(notification => notification.remove());
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show cart-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
        `;
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

    clearCart() {
        if (confirm('Are you sure you want to clear your cart?')) {
            this.cart = [];
            this.discount = 0;
            this.couponApplied = false;
            this.saveCart();
            this.updateCartDisplay();
            this.calculateTotals();
            this.showNotification('Cart cleared', 'info');
            
            // Reset coupon field
            const couponInput = document.getElementById('coupon');
            const couponButton = document.querySelector('#coupon-section .btn-black');
            const couponMessage = document.getElementById('coupon-message');
            
            if (couponInput) {
                couponInput.value = '';
                couponInput.disabled = false;
            }
            if (couponButton) couponButton.disabled = false;
            if (couponMessage) couponMessage.innerHTML = '';
        }
    }

    setupEventListeners() {
        // استمع لتحديثات العربة من الصفحات الأخرى
        if (typeof BroadcastChannel !== 'undefined') {
            const channel = new BroadcastChannel('cart_channel');
            channel.onmessage = (event) => {
                if (event.data.type === 'cart_updated') {
                    this.cart = JSON.parse(localStorage.getItem('cart')) || [];
                    this.updateCartDisplay();
                    this.calculateTotals();
                }
            };
        }
        
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('quantity-amount')) {
                const value = parseInt(e.target.value);
                if (isNaN(value) || value < 1) {
                    e.target.value = 1;
                }
                if (value > 10) {
                    e.target.value = 10;
                }
            }
        });
    }
}

// Initialize cart manager
const cartManager = new CartManager();

// Global functions for HTML onclick events
function updateCart() {
    cartManager.updateCart();
}

function applyCoupon() {
    cartManager.applyCoupon();
}

function proceedToCheckout() {
    cartManager.proceedToCheckout();
}

function clearCart() {
    cartManager.clearCart();
}

// استمع لتحديثات العربة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تحقق من تحديث العربة من localStorage
    const cartData = localStorage.getItem('cart');
    if (cartData) {
        cartManager.cart = JSON.parse(cartData);
        cartManager.updateCartDisplay();
        cartManager.calculateTotals();
    }
});