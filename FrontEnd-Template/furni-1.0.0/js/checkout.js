// Checkout Manager Class
class CheckoutManager {
    constructor() {
        this.cart = JSON.parse(localStorage.getItem('cart')) || [];
        this.discount = 0;
        this.appliedCoupon = null;
        this.init();
    }

    init() {
        this.loadCartFromStorage();
        this.setupEventListeners();
    }

    loadCartFromStorage() {
        const cartData = localStorage.getItem('cart');
        if (!cartData) {
            this.showEmptyCart();
            return;
        }

        try {
            this.cart = JSON.parse(cartData);
            if (this.cart.length === 0) {
                this.showEmptyCart();
                return;
            }
            this.renderOrderSummary();
        } catch (error) {
            console.error('Error loading cart:', error);
            this.showEmptyCart();
        }
    }

    showEmptyCart() {
        const container = document.getElementById('order-summary-container');
        if (!container) return;
        
        container.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-shopping-cart fa-3x text-muted mb-3"></i>
                <h4 class="text-muted mb-3">Your cart is empty</h4>
                <p class="text-muted mb-4">Add items to your cart before checking out</p>
                <a href="shop.html" class="btn btn-primary">Continue Shopping</a>
            </div>
        `;
        
        const placeOrderBtn = document.getElementById('place-order');
        if (placeOrderBtn) {
            placeOrderBtn.disabled = true;
            placeOrderBtn.innerHTML = 'Cart is Empty';
        }
    }

    renderOrderSummary() {
        const container = document.getElementById('order-summary-container');
        if (!container) return;
        
        let subtotal = 0;
        let html = '';

        this.cart.forEach(item => {
            const itemTotal = item.price * item.quantity;
            subtotal += itemTotal;
            
            html += `
                <div class="order-summary-item">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <div>
                            <strong>${item.name}</strong>
                            <div class="small text-muted">Quantity: ${item.quantity}</div>
                        </div>
                        <strong>$${itemTotal.toFixed(2)}</strong>
                    </div>
                </div>
            `;
        });

        const shipping = this.calculateShipping(subtotal);
        const totalBeforeDiscount = subtotal + shipping;
        const finalTotal = totalBeforeDiscount - this.discount;

        html += `
            <div class="order-summary-item pt-3 border-top">
                <div class="d-flex justify-content-between">
                    <span>Subtotal</span>
                    <span>$${subtotal.toFixed(2)}</span>
                </div>
            </div>
            
            <div class="order-summary-item">
                <div class="d-flex justify-content-between">
                    <span>Shipping</span>
                    <span>$${shipping.toFixed(2)}</span>
                </div>
            </div>
            
            ${this.discount > 0 ? `
            <div class="order-summary-item">
                <div class="d-flex justify-content-between">
                    <span>Discount ${this.appliedCoupon ? `(${this.appliedCoupon})` : ''}</span>
                    <span class="text-success">-$${this.discount.toFixed(2)}</span>
                </div>
            </div>
            ` : ''}
            
            <div class="order-summary-item pt-3 border-top">
                <div class="d-flex justify-content-between">
                    <strong class="h5">Total</strong>
                    <strong class="h5" id="order-total">$${finalTotal.toFixed(2)}</strong>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    calculateShipping(subtotal) {
        if (subtotal >= 100) {
            return 0;
        }
        return 10.00;
    }

    setupEventListeners() {
        // Shipping address toggle
        const shippingCheckbox = document.getElementById('shipping_address');
        const shippingSection = document.getElementById('shipping-address-section');
        
        if (shippingCheckbox && shippingSection) {
            shippingCheckbox.addEventListener('change', () => {
                shippingSection.classList.toggle('d-none', !shippingCheckbox.checked);
            });
        }

        // Payment method selection
        document.querySelectorAll('.payment-method').forEach(method => {
            method.addEventListener('click', () => {
                const radioBtn = method.querySelector('input[type="radio"]');
                if (radioBtn) {
                    radioBtn.checked = true;
                    
                    const cardDetails = document.getElementById('card-details');
                    if (cardDetails) {
                        cardDetails.style.display = radioBtn.value === 'card' ? 'block' : 'none';
                    }
                }
            });
        });

        // Initialize card details visibility
        const cardDetails = document.getElementById('card-details');
        if (cardDetails) {
            cardDetails.style.display = 'block';
        }

        // Place order button
        const placeOrderBtn = document.getElementById('place-order');
        if (placeOrderBtn) {
            placeOrderBtn.addEventListener('click', () => this.placeOrder());
        }

        // Form validation
        const billingForm = document.getElementById('billing-form');
        if (billingForm) {
            billingForm.addEventListener('submit', (e) => e.preventDefault());
        }

        // Card input formatting
        const cardNumberInput = document.getElementById('card_number');
        const cardExpiryInput = document.getElementById('card_expiry');
        const cardCvcInput = document.getElementById('card_cvc');
        
        if (cardNumberInput) {
            cardNumberInput.addEventListener('input', this.formatCardNumber);
        }
        if (cardExpiryInput) {
            cardExpiryInput.addEventListener('input', this.formatExpiryDate);
        }
        if (cardCvcInput) {
            cardCvcInput.addEventListener('input', this.formatCVC);
        }
    }

    formatCardNumber(e) {
        let value = e.target.value.replace(/\D/g, '');
        value = value.replace(/(\d{4})/g, '$1 ').trim();
        e.target.value = value.substring(0, 19);
    }

    formatExpiryDate(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        e.target.value = value.substring(0, 5);
    }

    formatCVC(e) {
        e.target.value = e.target.value.replace(/\D/g, '').substring(0, 3);
    }

    placeOrder() {
        // Check if cart is empty
        if (this.cart.length === 0) {
            alert('Your cart is empty. Please add items before placing an order.');
            window.location.href = 'shop.html';
            return;
        }

        // Validate terms
        const termsCheckbox = document.getElementById('terms');
        if (!termsCheckbox?.checked) {
            alert('Please agree to the terms and conditions');
            return;
        }

        // Validate billing form
        const billingForm = document.getElementById('billing-form');
        if (!billingForm?.checkValidity()) {
            alert('Please fill in all required fields in the billing details');
            return;
        }

        // Validate card details if card payment is selected
        if (document.getElementById('credit_card')?.checked) {
            if (!this.validateCardDetails()) {
                return;
            }
        }

        // Get order data
        const orderData = this.collectOrderData();

        // Show loading state
        const placeOrderBtn = document.getElementById('place-order');
        if (placeOrderBtn) {
            placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing Order...';
            placeOrderBtn.disabled = true;
        }

        // Simulate API call
        setTimeout(() => {
            this.saveOrder(orderData);
            
            // Clear cart
            localStorage.removeItem('cart');
            
            // Redirect to thank you page
            const orderDetails = encodeURIComponent(JSON.stringify({
                orderNumber: orderData.order.orderNumber,
                total: orderData.order.total
            }));
            window.location.href = `thankyou.html?order=${orderDetails}`;
        }, 2000);
    }

    collectOrderData() {
        return {
            customer: {
                firstName: document.getElementById('c_fname')?.value || '',
                lastName: document.getElementById('c_lname')?.value || '',
                email: document.getElementById('c_email')?.value || '',
                phone: document.getElementById('c_phone')?.value || '',
                address: document.getElementById('c_address')?.value || '',
                city: document.getElementById('c_city')?.value || '',
                postcode: document.getElementById('c_postcode')?.value || '',
                country: document.getElementById('c_country')?.value || '',
                company: document.getElementById('c_company')?.value || '',
                notes: document.getElementById('order_notes')?.value || ''
            },
            shipping: document.getElementById('shipping_address')?.checked ? {
                address: document.getElementById('s_address')?.value || '',
                city: document.getElementById('s_city')?.value || '',
                postcode: document.getElementById('s_postcode')?.value || ''
            } : null,
            payment: {
                method: document.querySelector('input[name="payment_method"]:checked')?.value || 'card',
                cardDetails: document.getElementById('credit_card')?.checked ? {
                    number: document.getElementById('card_number')?.value || '',
                    expiry: document.getElementById('card_expiry')?.value || '',
                    cvc: document.getElementById('card_cvc')?.value || ''
                } : null
            },
            order: {
                items: this.cart,
                subtotal: this.calculateSubtotal(),
                shipping: this.calculateShipping(this.calculateSubtotal()),
                discount: this.discount,
                total: parseFloat(document.getElementById('order-total')?.textContent?.replace('$', '') || '0'),
                coupon: this.appliedCoupon,
                orderNumber: this.generateOrderNumber(),
                date: new Date().toISOString()
            }
        };
    }

    validateCardDetails() {
        const cardNumber = document.getElementById('card_number')?.value.replace(/\s/g, '') || '';
        const expiry = document.getElementById('card_expiry')?.value || '';
        const cvc = document.getElementById('card_cvc')?.value || '';

        if (!cardNumber || cardNumber.length < 16) {
            alert('Please enter a valid 16-digit card number');
            return false;
        }

        if (!expiry || !expiry.match(/^\d{2}\/\d{2}$/)) {
            alert('Please enter a valid expiry date (MM/YY)');
            return false;
        }

        if (!cvc || cvc.length < 3) {
            alert('Please enter a valid CVC code');
            return false;
        }

        return true;
    }

    calculateSubtotal() {
        return this.cart.reduce((total, item) => total + (item.price * item.quantity), 0);
    }

    generateOrderNumber() {
        return 'ORD-' + Date.now().toString().slice(-8) + Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    }

    saveOrder(orderData) {
        const orders = JSON.parse(localStorage.getItem('orders')) || [];
        orders.push(orderData);
        localStorage.setItem('orders', JSON.stringify(orderData));
        sessionStorage.setItem('currentOrder', JSON.stringify(orderData));
    }

    hasCartItems() {
        return this.cart.length > 0;
    }
}

// Initialize checkout manager
const checkoutManager = new CheckoutManager();