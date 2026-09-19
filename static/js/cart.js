document.addEventListener('DOMContentLoaded', function() {

  document.querySelectorAll('.cart-item').forEach(function(item) {

    const minusBtn = item.querySelector('.minus');
    const plusBtn = item.querySelector('.plus');
    const qtyInput = item.querySelector('.qty');
    const removeBtn = item.querySelector('.remove');

    plusBtn.addEventListener('click', function() {
      let val = parseInt(qtyInput.value) || 1;
      qtyInput.value = val + 1;
      updateTotal();
    });

    minusBtn.addEventListener('click', function() {
      let val = parseInt(qtyInput.value) || 1;
      if (val > 1) {
        qtyInput.value = val - 1;
        updateTotal();
      }
    });

    qtyInput.addEventListener('change', function() {
      let val = parseInt(this.value) || 1;
      if (val < 1) val = 1;
      this.value = val;
      updateTotal();
    });

    removeBtn.addEventListener('click', function() {
      item.style.opacity = '0';
      item.style.transform = 'translateX(50px)';
      setTimeout(function() {
        item.remove();
        updateTotal();
      }, 300);
    });

  });

  function updateTotal() {
    let total = 0;

    document.querySelectorAll('.cart-item').forEach(function(item) {
      const price = parseInt(item.dataset.price) || 0;
      const qty = parseInt(item.querySelector('.qty').value) || 1;
      total += price * qty;
    });

    const totalSpan = document.getElementById('total');
    if (totalSpan) {
      totalSpan.innerHTML = total.toLocaleString('fa-IR');
    }

    if (document.querySelectorAll('.cart-item').length === 0) {
      document.querySelector('.cart-items').innerHTML = `
        <div style="text-align:center;padding:60px 20px;color:#888;">
          <div style="font-size:60px;margin-bottom:20px;">🛒</div>
          <h3 style="color:#aaa;">سبد خرید شما خالی است</h3>
          <p style="margin-top:10px;">برای مشاهده محصولات به صفحه اصلی بروید</p>
          <a href="/" style="display:inline-block;margin-top:20px;background:#c1121f;color:white;padding:12px 30px;border-radius:10px;text-decoration:none;">مشاهده محصولات</a>
        </div>
      `;
    }
  }

});