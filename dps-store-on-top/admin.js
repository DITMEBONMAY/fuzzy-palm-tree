document.addEventListener('DOMContentLoaded', function() {
  function bindTableInteractions() {
    const table = document.querySelector('table');
    const cells = table.querySelectorAll('td');
    cells.forEach(function(cell) {
      cell.addEventListener('mouseenter', function() {
        const columnIndex = Array.from(this.parentNode.children).indexOf(this);
        table.querySelectorAll('tr').forEach(function(row) {
          const cellToHighlight = row.children[columnIndex];
          if (cellToHighlight) {
            cellToHighlight.classList.add('highlight-column');
          }
        });
      });
      cell.addEventListener('mouseleave', function() {
        table.querySelectorAll('.highlight-column').forEach(function(highlightedCell) {
          highlightedCell.classList.remove('highlight-column');
        });
      });
    });
  }

  let currentPage = 1;
  const pageSize = 20; // 20 orders per page

  function loadOrders(page, append = false) {
    const searchVal = document.getElementById('orderSearch') ? document.getElementById('orderSearch').value.trim() : "";
    const statusVal = document.getElementById('statusFilter') ? document.getElementById('statusFilter').value : "all";
    const url = `/api/orders?page=${page}&search=${encodeURIComponent(searchVal)}&status=${statusVal}`;

    const ordersBody = document.getElementById('ordersBody');
    if (!append) {
      ordersBody.innerHTML = `<tr id="loaderRow"><td colspan="6" style="text-align: center; padding: 2rem;">
        <div class="loader">
          <div class="wrapper">
            <div class="circle"></div>
            <div class="line-1"></div>
            <div class="line-2"></div>
            <div class="line-3"></div>
            <div class="line-4"></div>
          </div>
        </div>
      </td></tr>`;
    }

    fetch(url, {
      headers: {
        "API-Code": 'KiIhrYd0G435pnHY28jo8iMsG7OQ6XaIa34V7n7XNrFHrLQv6hGrYcXU4Is0kh4Qu7Etf0k9SZDomuTpX3YN9CbSXXSOcErXQRAL'
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error("Network response was not ok");
        }
        return response.json();
      })
      .then(data => {
        if (!append) {
          ordersBody.innerHTML = "";
        }
        if (data.orders.length === 0 && page === 1) {
          ordersBody.innerHTML = `<tr><td colspan="6" style="text-align: center; padding: 1rem;">No orders found.</td></tr>`;
        } else {
          data.orders.forEach(order => {
            let statusClass = "";
            if (order.status === "Pending") {
              statusClass = "status-pending";
            } else if (order.status === "Processing") {
              statusClass = "status-processing";
            } else if (order.status === "Delivered") {
              statusClass = "status-delivered";
            } else if (order.status === "Cancelled") {
              statusClass = "status-cancelled";
            }
            const rowHtml = `
              <tr>
                <td>${order.unique_id}</td>
                <td><span class="status ${statusClass}">${order.status}</span></td>
                <td>${order.product}</td>
                <td style="text-align: center;">${order.quantity}</td>
                <td><span class="price">${order.total_price} ${order.currency}</span></td>
                <td class="action-links">
                  <a href="/process/${order.unique_id}" class="action-btn btn-process">
                    <i class="fas fa-cog"></i> <span>Process</span>
                  </a>
                  <a href="/track/${order.unique_id}" class="action-btn btn-track">
                    <i class="fas fa-map-marker-alt"></i> <span>Track</span>
                  </a>
                </td>
              </tr>
            `;
            ordersBody.insertAdjacentHTML('beforeend', rowHtml);
          });
        }
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        if (loadMoreBtn) {
          loadMoreBtn.style.display = data.has_more ? 'inline-block' : 'none';
        }
        bindTableInteractions();
      })
      .catch(error => {
        console.error('Error fetching orders:', error);
      });
  }

  if (document.getElementById('orderSearch')) {
    document.getElementById('orderSearch').addEventListener('input', function() {
      currentPage = 1;
      loadOrders(currentPage, false);
    });
  }
  if (document.getElementById('statusFilter')) {
    document.getElementById('statusFilter').addEventListener('change', function() {
      currentPage = 1;
      loadOrders(currentPage, false);
    });
  }
  if (document.getElementById('loadMoreBtn')) {
    document.getElementById('loadMoreBtn').addEventListener('click', function() {
      currentPage++;
      loadOrders(currentPage, true);
    });
  }

  loadOrders(currentPage, false);
});