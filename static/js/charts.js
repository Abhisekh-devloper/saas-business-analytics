// SaaS Business Analytics - Interactive Visualization Engine (Chart.js & Plotly)

const ChartEngine = (() => {
  let instances = {
    trends: null,
    categoryDonut: null,
    categoryBar: null,
    region: null,
    topProducts: null,
    marginDist: null
  };

  let activeEngine = 'chartjs'; // 'chartjs' or 'plotly'

  // Modern SaaS palette
  const colors = {
    cyan: '#38BDF8',
    cyanFade: 'rgba(56, 189, 248, 0.15)',
    indigo: '#6366F1',
    indigoFade: 'rgba(99, 102, 241, 0.15)',
    emerald: '#10B981',
    emeraldFade: 'rgba(16, 185, 129, 0.15)',
    amber: '#F59E0B',
    rose: '#F43F5E',
    purple: '#A855F7',
    palette: [
      '#38BDF8', '#6366F1', '#10B981', '#F59E0B', '#EC4899',
      '#8B5CF6', '#14B8A6', '#F97316', '#06B6D4', '#84CC16'
    ]
  };

  const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#94A3B8',
          font: { family: "'Plus Jakarta Sans', sans-serif", size: 12 }
        }
      },
      tooltip: {
        backgroundColor: '#0F172A',
        titleColor: '#F8FAFC',
        bodyColor: '#94A3B8',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 10,
        boxPadding: 4,
        usePointStyle: true
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
        ticks: { color: '#64748B', font: { family: "'Plus Jakarta Sans', sans-serif" } }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
        ticks: {
          color: '#64748B',
          font: { family: "'Plus Jakarta Sans', sans-serif" },
          callback: (value) => `$${value >= 1000 ? (value / 1000).toFixed(0) + 'k' : value}`
        }
      }
    }
  };

  function setEngine(engine) {
    activeEngine = engine;
  }

  function getEngine() {
    return activeEngine;
  }

  function destroyChart(key) {
    if (instances[key]) {
      instances[key].destroy();
      instances[key] = null;
    }
  }

  // 1. Monthly Trends Chart (Revenue & Profit Area)
  function renderTrends(data) {
    const ctx = document.getElementById('chart-trends');
    if (!ctx) return;

    if (activeEngine === 'plotly' && window.Plotly) {
      destroyChart('trends');
      const trace1 = {
        x: data.labels,
        y: data.revenue,
        name: 'Revenue ($)',
        type: 'scatter',
        mode: 'lines+markers',
        fill: 'tozeroy',
        line: { color: colors.cyan, width: 3 },
        marker: { size: 6 }
      };
      const trace2 = {
        x: data.labels,
        y: data.profit,
        name: 'Profit ($)',
        type: 'scatter',
        mode: 'lines+markers',
        fill: 'tozeroy',
        line: { color: colors.emerald, width: 3 },
        marker: { size: 6 }
      };
      const layout = {
        paper_bgcolor: 'transparent',
        plot_bgcolor: 'transparent',
        font: { color: '#94A3B8', family: 'Plus Jakarta Sans' },
        margin: { l: 50, r: 20, t: 30, b: 40 },
        legend: { orientation: 'h', y: 1.15 },
        xaxis: { gridcolor: 'rgba(255,255,255,0.05)' },
        yaxis: { gridcolor: 'rgba(255,255,255,0.05)' }
      };
      Plotly.newPlot('chart-trends-plotly', [trace1, trace2], layout, { responsive: true, displayModeBar: false });
      return;
    }

    destroyChart('trends');
    instances.trends = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Revenue',
            data: data.revenue,
            borderColor: colors.cyan,
            backgroundColor: colors.cyanFade,
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: colors.cyan,
            pointRadius: 4,
            pointHoverRadius: 6
          },
          {
            label: 'Net Profit',
            data: data.profit,
            borderColor: colors.emerald,
            backgroundColor: colors.emeraldFade,
            borderWidth: 2.5,
            fill: true,
            tension: 0.35,
            pointBackgroundColor: colors.emerald,
            pointRadius: 4,
            pointHoverRadius: 6
          }
        ]
      },
      options: {
        ...chartDefaults,
        interaction: { mode: 'index', intersect: false }
      }
    });
  }

  // 2. Category Performance (Donut & Grouped Bar)
  function renderCategoryDonut(data) {
    const ctx = document.getElementById('chart-category-donut');
    if (!ctx) return;
    destroyChart('categoryDonut');

    instances.categoryDonut = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.revenue,
          backgroundColor: colors.palette.slice(0, data.labels.length),
          borderWidth: 2,
          borderColor: '#131B2A'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '72%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              color: '#94A3B8',
              font: { family: "'Plus Jakarta Sans', sans-serif", size: 11 },
              boxWidth: 12,
              padding: 10
            }
          },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const val = ctx.raw;
                const share = data.shares[ctx.dataIndex] || 0;
                return ` ${ctx.label}: $${val.toLocaleString()} (${share}%)`;
              }
            }
          }
        }
      }
    });
  }

  function renderCategoryBar(data) {
    const ctx = document.getElementById('chart-category-bar');
    if (!ctx) return;
    destroyChart('categoryBar');

    instances.categoryBar = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Revenue',
            data: data.revenue,
            backgroundColor: colors.cyan,
            borderRadius: 6
          },
          {
            label: 'Profit',
            data: data.profit,
            backgroundColor: colors.indigo,
            borderRadius: 6
          }
        ]
      },
      options: {
        ...chartDefaults,
        plugins: {
          ...chartDefaults.plugins,
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => {
                if (ctx.datasetIndex === 1) {
                  return ` Margin: ${data.margin[ctx.dataIndex]}%`;
                }
              }
            }
          }
        }
      }
    });
  }

  // 3. Regional Performance
  function renderRegion(data) {
    const ctx = document.getElementById('chart-region');
    if (!ctx) return;
    destroyChart('region');

    instances.region = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Revenue ($)',
            data: data.revenue,
            backgroundColor: colors.palette.slice(2, 2 + data.labels.length),
            borderRadius: 8
          }
        ]
      },
      options: {
        ...chartDefaults,
        indexAxis: 'y',
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#64748B',
              callback: (v) => `$${v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v}`
            }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#94A3B8', font: { weight: 500 } }
          }
        }
      }
    });
  }

  // 4. Top 10 Selling Products
  function renderTopProducts(products) {
    const ctx = document.getElementById('chart-top-products');
    if (!ctx) return;
    destroyChart('topProducts');

    const top10 = products.slice(0, 8);
    const names = top10.map(p => p.name.length > 22 ? p.name.substring(0, 20) + '...' : p.name);
    const revs = top10.map(p => p.revenue);
    const margins = top10.map(p => p.margin);

    instances.topProducts = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: names,
        datasets: [{
          label: 'Revenue ($)',
          data: revs,
          backgroundColor: '#38BDF8',
          borderRadius: 6
        }]
      },
      options: {
        ...chartDefaults,
        indexAxis: 'y',
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#64748B',
              callback: (v) => `$${v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v}`
            }
          },
          y: {
            grid: { display: false },
            ticks: { color: '#CBD5E1', font: { size: 11 } }
          }
        },
        plugins: {
          ...chartDefaults.plugins,
          tooltip: {
            callbacks: {
              label: (ctx) => ` Revenue: $${ctx.raw.toLocaleString()}`,
              afterLabel: (ctx) => ` Margin: ${margins[ctx.dataIndex]}%`
            }
          }
        }
      }
    });
  }

  // 5. Margin % Distribution by Category
  function renderMarginDist(data) {
    const ctx = document.getElementById('chart-margin-dist');
    if (!ctx) return;
    destroyChart('marginDist');

    const bgColors = data.margin.map(m => m >= 25 ? '#10B981' : (m >= 12 ? '#38BDF8' : '#F59E0B'));

    instances.marginDist = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Profit Margin (%)',
          data: data.margin,
          backgroundColor: bgColors,
          borderRadius: 6
        }]
      },
      options: {
        ...chartDefaults,
        scales: {
          ...chartDefaults.scales,
          y: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: {
              color: '#64748B',
              callback: (v) => `${v}%`
            }
          }
        }
      }
    });
  }

  function renderAll(dashboardData) {
    const metrics = dashboardData.metrics;
    if (!metrics) return;

    renderTrends(metrics.monthly_trends);
    renderCategoryDonut(metrics.category_performance);
    renderCategoryBar(metrics.category_performance);
    renderRegion(metrics.region_performance);
    renderTopProducts(metrics.top_products);
    renderMarginDist(metrics.category_performance);
  }

  return {
    setEngine,
    getEngine,
    renderAll,
    renderTrends,
    renderCategoryDonut,
    renderCategoryBar,
    renderRegion,
    renderTopProducts,
    renderMarginDist
  };
})();

