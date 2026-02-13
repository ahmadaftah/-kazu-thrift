document.addEventListener('DOMContentLoaded', function() {
    // If dashboard charts exist
    if (document.getElementById('stockChart')) {
        fetch('/api/dashboard_data')
            .then(response => response.json())
            .then(data => {
                // Stock Chart
                const stockCtx = document.getElementById('stockChart').getContext('2d');
                new Chart(stockCtx, {
                    type: 'doughnut',
                    data: {
                        labels: data.stock_levels.map(item => item.category),
                        datasets: [{
                            label: 'Jumlah Stok',
                            data: data.stock_levels.map(item => item.total_stock),
                            backgroundColor: [
                                'rgba(108, 92, 231, 0.6)',
                                'rgba(162, 155, 254, 0.6)',
                                'rgba(85, 239, 196, 0.6)',
                                'rgba(255, 118, 117, 0.6)',
                                'rgba(253, 203, 110, 0.6)'
                            ],
                            borderColor: 'rgba(255, 255, 255, 0.2)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { labels: { color: 'white' } }
                        }
                    }
                });

                // Revenue Chart
                const revenueCtx = document.getElementById('revenueChart').getContext('2d');
                new Chart(revenueCtx, {
                    type: 'line',
                    data: {
                        labels: data.sales_per_day.map(item => {
                            const date = new Date(item.date);
                            return date.toLocaleDateString('id-ID', { weekday: 'short' });
                        }),
                        datasets: [{
                            label: 'Pendapatan (Rp)',
                            data: data.sales_per_day.map(item => item.revenue),
                            borderColor: '#a29bfe',
                            backgroundColor: 'rgba(162, 155, 254, 0.2)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: { ticks: { color: 'white' } },
                            x: { ticks: { color: 'white' } }
                        },
                        plugins: {
                            legend: { labels: { color: 'white' } }
                        }
                    }
                });
            });
    }

    // Search functionality (simple client-side for now)
    const searchInput = document.getElementById('inventorySearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const filter = this.value.toLowerCase();
            const rows = document.querySelectorAll('#inventoryTable tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(filter) ? '' : 'none';
            });
        });
    }
});
