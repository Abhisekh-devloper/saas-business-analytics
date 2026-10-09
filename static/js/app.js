// SaaS Business Analytics - Main Application Orchestrator

document.addEventListener('DOMContentLoaded', () => {
  // Application State
  const state = {
    user: null,
    datasets: [],
    activeDatasetId: null,
    activeDatasetName: 'No Dataset Selected',
    filters: {
      startDate: '',
      endDate: '',
      category: 'all',
      region: 'all',
      search: ''
    },
    table: {
      page: 1,
      pageSize: 15,
      ordering: '-order_date'
    },
    currentTab: 'dashboard'
  };

  // Toast System
  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'info';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'alert-triangle';

    toast.innerHTML = `
      <i data-lucide="${icon}" class="w-5 h-5 flex-shrink-0"></i>
      <span class="text-sm font-medium flex-1">${message}</span>
      <button class="opacity-60 hover:opacity-100 transition-opacity ml-2">&times;</button>
    `;
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    toast.querySelector('button').onclick = () => toast.remove();
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }

  // Formatters
  const fmtCurrency = (n) => `$${Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const fmtNumber = (n) => Number(n || 0).toLocaleString('en-US');
  const fmtPercent = (n) => `${Number(n || 0).toFixed(1)}%`;

  // UI Tab Navigation
  function switchTab(tabName) {
    state.currentTab = tabName;
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));

    const targetContent = document.getElementById(`tab-content-${tabName}`);
    const targetNav = document.getElementById(`nav-tab-${tabName}`);

    if (targetContent) targetContent.classList.remove('hidden');
    if (targetNav) targetNav.classList.add('active');

    // Trigger tab-specific loads
    if (tabName === 'dashboard') loadDashboard();
    if (tabName === 'insights') loadInsights();
    if (tabName === 'explorer') loadTableData();
    if (tabName === 'upload') loadDatasetsList();
    if (tabName === 'reports') updateReportLinks();

    if (window.lucide) lucide.createIcons();
  }

  // Setup Tab Listeners
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.getAttribute('data-tab');
      if (target) switchTab(target);
    });
  });

  // Auth Handling
  async function initAuth() {
    if (API.auth.isAuthenticated()) {
      try {
        state.user = await API.auth.fetchProfile();
        updateUserUI();
        await loadDatasetsList();
        loadDashboard();
      } catch (err) {
        console.warn('Auth check failed:', err);
        showAuthModal(true);
      }
    } else {
      // Prompt sign in or automatic demo
      showAuthModal(true);
    }
  }

  function updateUserUI() {
    const userBadge = document.getElementById('user-profile-badge');
    const authBtn = document.getElementById('btn-open-auth');
    const userMenu = document.getElementById('user-menu-dropdown');
    
    if (state.user) {
      if (userBadge) {
        userBadge.classList.remove('hidden');
        document.getElementById('user-display-name').textContent = state.user.first_name || state.user.username;
        document.getElementById('user-display-initial').textContent = (state.user.username[0] || 'U').toUpperCase();
      }
      if (authBtn) authBtn.classList.add('hidden');
    } else {
      if (userBadge) userBadge.classList.add('hidden');
      if (authBtn) authBtn.classList.remove('hidden');
    }
  }

  function showAuthModal(show = true) {
    const modal = document.getElementById('auth-modal');
    if (!modal) return;
    if (show) modal.classList.remove('hidden');
    else modal.classList.add('hidden');
  }

  // Datasets Management
  async function loadDatasetsList() {
    try {
      const datasets = await API.datasets.list();
      state.datasets = datasets;
      
      const select = document.getElementById('active-dataset-select');
      const tableBody = document.getElementById('datasets-table-body');
      
      if (select) {
        select.innerHTML = '';
        if (datasets.length === 0) {
          select.innerHTML = '<option value="">No Datasets (Upload or Load Demo)</option>';
        } else {
          datasets.forEach(ds => {
            const opt = document.createElement('option');
            opt.value = ds.id;
            opt.textContent = `${ds.name} (${fmtNumber(ds.row_count)} rows)`;
            if (ds.is_active) {
              opt.selected = true;
              state.activeDatasetId = ds.id;
              state.activeDatasetName = ds.name;
            }
            select.appendChild(opt);
          });
          if (!state.activeDatasetId && datasets.length > 0) {
            state.activeDatasetId = datasets[0].id;
            state.activeDatasetName = datasets[0].name;
          }
        }
      }

      // Populate datasets inventory table in Datasets tab
      if (tableBody) {
        tableBody.innerHTML = '';
        if (datasets.length === 0) {
          tableBody.innerHTML = `<tr><td colspan="6" class="text-center py-8 text-slate-500">No datasets uploaded yet. Load the sample dataset or upload a CSV/Excel file.</td></tr>`;
        } else {
          datasets.forEach(ds => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td class="font-semibold text-white">${ds.name} ${ds.is_active ? '<span class="badge-metric bg-emerald-500/20 text-emerald-400 ml-2">Active</span>' : ''}</td>
              <td><span class="badge-metric bg-slate-800 text-slate-300 uppercase">${ds.file_type}</span></td>
              <td>${fmtNumber(ds.row_count)} rows</td>
              <td>${(ds.file_size_bytes / 1024).toFixed(1)} KB</td>
              <td class="text-xs text-slate-400">${new Date(ds.created_at).toLocaleDateString()}</td>
              <td class="text-right">
                ${!ds.is_active ? `<button data-set-active="${ds.id}" class="text-xs px-2 py-1 rounded bg-sky-500/20 text-sky-400 hover:bg-sky-500/30 transition mr-2">Activate</button>` : ''}
                <button data-delete-id="${ds.id}" class="text-xs px-2 py-1 rounded bg-rose-500/20 text-rose-400 hover:bg-rose-500/30 transition">Delete</button>
              </td>
            `;
            tableBody.appendChild(tr);
          });

          // Add delete & activate listeners
          tableBody.querySelectorAll('[data-set-active]').forEach(btn => {
            btn.onclick = async () => {
              const id = btn.getAttribute('data-set-active');
              await API.datasets.setActive(id);
              showToast('Active dataset switched!', 'success');
              await loadDatasetsList();
              loadDashboard();
            };
          });

          tableBody.querySelectorAll('[data-delete-id]').forEach(btn => {
            btn.onclick = async () => {
              const id = btn.getAttribute('data-delete-id');
              if (confirm('Are you sure you want to delete this dataset?')) {
                await API.datasets.delete(id);
                showToast('Dataset deleted.', 'info');
                await loadDatasetsList();
                loadDashboard();
              }
            };
          });
        }
      }
    } catch (err) {
      console.error('Error fetching datasets:', err);
    }
  }

  // Dashboard Loader
  async function loadDashboard() {
    if (!API.auth.isAuthenticated()) return;
    const loader = document.getElementById('dashboard-loading-skeleton');
    if (loader) loader.classList.remove('hidden');

    try {
      const queryParams = {
        dataset_id: state.activeDatasetId || '',
        start_date: state.filters.startDate,
        end_date: state.filters.endDate,
        category: state.filters.category,
        region: state.filters.region,
        search: state.filters.search
      };

      const data = await API.analytics.getDashboard(queryParams);

      if (!data.has_dataset) {
        document.getElementById('empty-dataset-banner').classList.remove('hidden');
        document.getElementById('dashboard-main-content').classList.add('hidden');
        if (loader) loader.classList.add('hidden');
        return;
      }

      document.getElementById('empty-dataset-banner').classList.add('hidden');
      document.getElementById('dashboard-main-content').classList.remove('hidden');

      state.activeDatasetId = data.dataset_id;
      state.activeDatasetName = data.dataset_name;

      // Update KPI Cards
      const kpis = data.metrics.kpis;
      document.getElementById('kpi-revenue').textContent = fmtCurrency(kpis.total_revenue);
      document.getElementById('kpi-profit').textContent = fmtCurrency(kpis.total_profit);
      document.getElementById('kpi-margin').textContent = fmtPercent(kpis.profit_margin);
      document.getElementById('kpi-orders').textContent = fmtNumber(kpis.total_orders);
      document.getElementById('kpi-aov').textContent = fmtCurrency(kpis.avg_order_value);
      
      const momBadge = document.getElementById('kpi-mom-growth');
      if (momBadge) {
        momBadge.textContent = `${kpis.mom_growth >= 0 ? '+' : ''}${kpis.mom_growth}% MoM`;
        momBadge.className = `badge-metric ${kpis.mom_growth >= 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`;
      }

      // Populate Filters dropdown options if not already populated
      populateFilterOptions(data.filter_options);

      // Render Charts
      ChartEngine.renderAll(data);

      updateReportLinks();

    } catch (err) {
      showToast(err.message || 'Failed to load dashboard metrics', 'error');
    } finally {
      if (loader) loader.classList.add('hidden');
      if (window.lucide) lucide.createIcons();
    }
  }

  function populateFilterOptions(options) {
    if (!options) return;

    // Categories
    const catSelect = document.getElementById('filter-category');
    if (catSelect && catSelect.options.length <= 1) {
      options.categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        catSelect.appendChild(opt);
      });
    }

    // Regions
    const regSelect = document.getElementById('filter-region');
    if (regSelect && regSelect.options.length <= 1) {
      options.regions.forEach(r => {
        const opt = document.createElement('option');
        opt.value = r;
        opt.textContent = r;
        regSelect.appendChild(opt);
      });
    }

    // Date limits
    if (options.date_bounds && options.date_bounds.min && options.date_bounds.max) {
      const sInput = document.getElementById('filter-start-date');
      const eInput = document.getElementById('filter-end-date');
      if (sInput && !sInput.value) sInput.value = options.date_bounds.min;
      if (eInput && !eInput.value) eInput.value = options.date_bounds.max;
    }
  }

  // Smart Insights Loader
  async function loadInsights() {
    const container = document.getElementById('insights-container');
    if (!container) return;
    container.innerHTML = '<div class="py-12 text-center text-slate-400"><div class="animate-spin inline-block w-8 h-8 border-4 border-sky-400 border-t-transparent rounded-full mb-3"></div><p>Synthesizing Executive Business Insights & Anomaly Analysis...</p></div>';

    try {
      const res = await API.analytics.getInsights({
        dataset_id: state.activeDatasetId || '',
        start_date: state.filters.startDate,
        end_date: state.filters.endDate,
        category: state.filters.category,
        region: state.filters.region
      });

      if (!res.has_dataset) {
        container.innerHTML = '<div class="p-8 text-center text-slate-400">No active dataset found to analyze.</div>';
        return;
      }

      const ins = res.insights;
      
      let highlightsHtml = '';
      (ins.highlights || []).forEach(h => {
        highlightsHtml += `
          <div class="glass-card p-5 border-l-4 border-${h.color}-500 flex flex-col justify-between">
            <div>
              <p class="text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">${h.title}</p>
              <h4 class="text-lg font-bold text-white mb-1 truncate">${h.value}</h4>
            </div>
            <p class="text-xs font-medium text-${h.color}-400">${h.subtitle}</p>
          </div>
        `;
      });

      let recsHtml = '';
      (ins.recommendations || []).forEach(r => {
        const pBadge = r.priority === 'Critical' ? 'bg-rose-500/20 text-rose-400' : (r.priority === 'High' ? 'bg-amber-500/20 text-amber-400' : 'bg-sky-500/20 text-sky-400');
        recsHtml += `
          <div class="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3">
            <span class="badge-metric ${pBadge} flex-shrink-0 mt-0.5">${r.priority}</span>
            <div>
              <h5 class="text-sm font-bold text-slate-200 mb-1">${r.category}</h5>
              <p class="text-xs text-slate-400 leading-relaxed">${r.text}</p>
            </div>
          </div>
        `;
      });

      let anomaliesHtml = '';
      (ins.anomalies || []).forEach(a => {
        anomaliesHtml += `
          <div class="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-3">
            <i data-lucide="alert-octagon" class="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5"></i>
            <div>
              <span class="text-xs font-bold text-rose-400 uppercase tracking-wide">${a.type}</span>
              <p class="text-xs text-slate-300 mt-1 leading-relaxed">${a.message}</p>
            </div>
          </div>
        `;
      });

      if (!anomaliesHtml) {
        anomaliesHtml = `
          <div class="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-3">
            <i data-lucide="check-circle" class="w-5 h-5 text-emerald-400"></i>
            <p class="text-xs text-emerald-300 font-medium">No negative profit anomalies detected. Health indicators are sound!</p>
          </div>
        `;
      }

      container.innerHTML = `
        <div class="space-y-6 animate-fade-in">
          <!-- Executive Summary Banner -->
          <div class="glass-card p-6 border-l-4 border-sky-400">
            <div class="flex items-center justify-between mb-3">
              <h3 class="text-base font-bold text-white flex items-center gap-2">
                <i data-lucide="sparkles" class="w-5 h-5 text-sky-400"></i>
                Executive Narrative Summary
              </h3>
              <span class="badge-metric ${ins.overall_health === 'Excellent' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-sky-500/20 text-sky-400'}">
                Status: ${ins.overall_health}
              </span>
            </div>
            <p class="text-sm text-slate-300 leading-relaxed">${ins.executive_summary}</p>
          </div>

          <!-- Highlight Badges -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            ${highlightsHtml}
          </div>

          <!-- Recommendations & Risk Signals -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div class="glass-card p-6">
              <h4 class="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <i data-lucide="compass" class="w-4 h-4 text-sky-400"></i>
                Strategic Action Recommendations
              </h4>
              <div class="space-y-3">${recsHtml}</div>
            </div>

            <div class="glass-card p-6">
              <h4 class="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <i data-lucide="shield-alert" class="w-4 h-4 text-rose-400"></i>
                Anomaly & Risk Signals
              </h4>
              <div class="space-y-3">${anomaliesHtml}</div>
            </div>
          </div>
        </div>
      `;

      if (window.lucide) lucide.createIcons();

    } catch (err) {
      container.innerHTML = `<div class="p-8 text-center text-rose-400 font-semibold">${err.message || 'Failed to load insights.'}</div>`;
    }
  }

  // Data Explorer Table Loader
  async function loadTableData() {
    const tbody = document.getElementById('records-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-8 text-slate-400">Loading records...</td></tr>';

    try {
      const res = await API.analytics.getDataTable({
        dataset_id: state.activeDatasetId || '',
        start_date: state.filters.startDate,
        end_date: state.filters.endDate,
        category: state.filters.category,
        region: state.filters.region,
        search: state.filters.search,
        page: state.table.page,
        page_size: state.table.pageSize,
        ordering: state.table.ordering
      });

      tbody.innerHTML = '';
      if (!res.results || res.results.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-8 text-slate-500">No matching records found.</td></tr>';
        return;
      }

      res.results.forEach(r => {
        const tr = document.createElement('tr');
        const marginColor = r.profit_margin >= 20 ? 'text-emerald-400' : (r.profit_margin >= 5 ? 'text-sky-400' : 'text-rose-400');
        tr.innerHTML = `
          <td class="font-mono text-xs text-slate-400">${r.order_id || 'N/A'}</td>
          <td class="text-xs text-slate-300">${r.order_date || 'N/A'}</td>
          <td class="font-medium text-white">${r.product_name}</td>
          <td><span class="badge-metric bg-slate-800 text-slate-300">${r.category}</span></td>
          <td class="text-slate-300">${r.region}</td>
          <td class="font-semibold text-slate-200">${fmtCurrency(r.revenue)}</td>
          <td class="font-semibold ${r.profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}">${fmtCurrency(r.profit)}</td>
          <td class="font-bold ${marginColor}">${r.profit_margin}%</td>
        `;
        tbody.appendChild(tr);
      });

      // Pagination Controls
      document.getElementById('table-current-page').textContent = res.page;
      document.getElementById('table-total-pages').textContent = res.total_pages;
      document.getElementById('table-total-count').textContent = fmtNumber(res.count);

      const prevBtn = document.getElementById('table-prev-btn');
      const nextBtn = document.getElementById('table-next-btn');
      if (prevBtn) prevBtn.disabled = res.page <= 1;
      if (nextBtn) nextBtn.disabled = res.page >= res.total_pages;

    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-rose-400">${err.message}</td></tr>`;
    }
  }

  // Update Report Export Links
  function updateReportLinks() {
    const params = {
      dataset_id: state.activeDatasetId || '',
      start_date: state.filters.startDate,
      end_date: state.filters.endDate,
      category: state.filters.category,
      region: state.filters.region
    };

    const csvBtn = document.getElementById('btn-export-csv');
    const excelBtn = document.getElementById('btn-export-excel');
    const pdfBtn = document.getElementById('btn-export-pdf');

    if (csvBtn) csvBtn.href = API.analytics.getExportUrl('csv', params);
    if (excelBtn) excelBtn.href = API.analytics.getExportUrl('excel', params);
    if (pdfBtn) pdfBtn.href = API.analytics.getExportUrl('pdf', params);
  }

  // Filter Event Listeners
  document.getElementById('btn-apply-filters')?.addEventListener('click', () => {
    state.filters.startDate = document.getElementById('filter-start-date').value;
    state.filters.endDate = document.getElementById('filter-end-date').value;
    state.filters.category = document.getElementById('filter-category').value;
    state.filters.region = document.getElementById('filter-region').value;
    state.filters.search = document.getElementById('filter-search').value;
    state.table.page = 1;

    showToast('Filters applied!', 'info');
    loadDashboard();
    if (state.currentTab === 'insights') loadInsights();
    if (state.currentTab === 'explorer') loadTableData();
  });

  document.getElementById('btn-reset-filters')?.addEventListener('click', () => {
    document.getElementById('filter-category').value = 'all';
    document.getElementById('filter-region').value = 'all';
    document.getElementById('filter-search').value = '';
    state.filters.category = 'all';
    state.filters.region = 'all';
    state.filters.search = '';
    state.table.page = 1;

    showToast('Filters reset.', 'info');
    loadDashboard();
  });

  // Table pagination buttons
  document.getElementById('table-prev-btn')?.addEventListener('click', () => {
    if (state.table.page > 1) {
      state.table.page--;
      loadTableData();
    }
  });

  document.getElementById('table-next-btn')?.addEventListener('click', () => {
    state.table.page++;
    loadTableData();
  });

  // Dataset Switcher Listener
  document.getElementById('active-dataset-select')?.addEventListener('change', async (e) => {
    const val = e.target.value;
    if (!val) return;
    try {
      await API.datasets.setActive(val);
      state.activeDatasetId = val;
      showToast('Switched dataset successfully.', 'success');
      loadDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // 1-Click Demo Data Loader
  document.querySelectorAll('.btn-load-demo-data').forEach(btn => {
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      const originalText = btn.innerHTML;
      btn.innerHTML = `<span class="inline-block animate-spin mr-2">⟳</span> Generating 1,200 Records...`;
      try {
        const res = await API.datasets.loadSample();
        showToast(res.message, 'success');
        await loadDatasetsList();
        switchTab('dashboard');
        loadDashboard();
      } catch (err) {
        showToast(err.message || 'Failed to seed demo data', 'error');
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    });
  });

  // File Upload & Drag-and-Drop
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('file-upload-input');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelection(fileInput.files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) {
        handleFileSelection(fileInput.files[0]);
      }
    });
  }

  function handleFileSelection(file) {
    const nameEl = document.getElementById('selected-file-name');
    const sizeEl = document.getElementById('selected-file-size');
    const infoCard = document.getElementById('selected-file-card');
    const nameInput = document.getElementById('upload-dataset-name');

    if (nameEl) nameEl.textContent = file.name;
    if (sizeEl) sizeEl.textContent = `${(file.size / 1024).toFixed(1)} KB`;
    if (infoCard) infoCard.classList.remove('hidden');
    if (nameInput && !nameInput.value) {
      nameInput.value = file.name.replace(/\.[^/.]+$/, '').replace(/[_-]/g, ' ');
    }
  }

  // Upload Form Submission
  document.getElementById('dataset-upload-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) {
      showToast('Please select a CSV or Excel file to upload.', 'error');
      return;
    }

    const name = document.getElementById('upload-dataset-name').value.trim();
    const desc = document.getElementById('upload-dataset-desc').value.trim();
    const submitBtn = document.getElementById('btn-submit-upload');

    submitBtn.disabled = true;
    submitBtn.innerHTML = `<span class="inline-block animate-spin mr-2">⟳</span> Cleaning & Validating Data...`;

    try {
      const formData = new FormData();
      formData.append('file', file);
      if (name) formData.append('name', name);
      if (desc) formData.append('description', desc);

      const res = await API.datasets.upload(formData);
      showToast(res.message, 'success');

      // Show Validation Report Modal
      showValidationReportModal(res.validation_report, res.dataset);

      // Refresh datasets and go to dashboard
      await loadDatasetsList();
      fileInput.value = '';
      document.getElementById('selected-file-card').classList.add('hidden');

    } catch (err) {
      showToast(err.message || 'Upload and validation failed.', 'error');
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `Ingest & Launch Dashboard`;
    }
  });

  function showValidationReportModal(report, dataset) {
    const modal = document.getElementById('validation-report-modal');
    if (!modal) return;

    document.getElementById('val-total-rows').textContent = fmtNumber(report.total_raw_rows);
    document.getElementById('val-clean-rows').textContent = fmtNumber(report.cleaned_rows);
    document.getElementById('val-dropped-rows').textContent = fmtNumber(report.dropped_rows);
    document.getElementById('val-quality-score').textContent = `${report.data_quality_score}%`;

    const colsList = document.getElementById('val-detected-columns');
    if (colsList) {
      colsList.innerHTML = '';
      for (const [canon, orig] of Object.entries(report.detected_columns || {})) {
        const li = document.createElement('div');
        li.className = 'flex justify-between py-1 border-b border-slate-800 text-xs';
        li.innerHTML = `<span class="text-slate-400 capitalize">${canon.replace('_', ' ')}:</span> <span class="font-mono text-sky-400 font-semibold">${orig}</span>`;
        colsList.appendChild(li);
      }
    }

    modal.classList.remove('hidden');
    document.getElementById('btn-close-val-report').onclick = () => {
      modal.classList.add('hidden');
      switchTab('dashboard');
      loadDashboard();
    };
  }

  // Visualization Switcher (Chart.js / Plotly)
  document.getElementById('btn-toggle-engine')?.addEventListener('click', () => {
    const current = ChartEngine.getEngine();
    const next = current === 'chartjs' ? 'plotly' : 'chartjs';
    ChartEngine.setEngine(next);
    
    const label = document.getElementById('chart-engine-label');
    if (label) label.textContent = next === 'chartjs' ? 'Chart.js' : 'Plotly 3D';
    
    // Toggle canvas / plotly div visibility for trends chart
    const cCanvas = document.getElementById('chart-trends');
    const pDiv = document.getElementById('chart-trends-plotly');
    if (next === 'plotly') {
      cCanvas.classList.add('hidden');
      pDiv.classList.remove('hidden');
    } else {
      cCanvas.classList.remove('hidden');
      pDiv.classList.add('hidden');
    }

    showToast(`Switched chart engine to ${next.toUpperCase()}`, 'info');
    loadDashboard();
  });

  // Auth Modal Forms
  document.getElementById('btn-open-auth')?.addEventListener('click', () => showAuthModal(true));
  document.getElementById('btn-close-auth')?.addEventListener('click', () => showAuthModal(false));

  document.getElementById('auth-tab-login')?.addEventListener('click', () => {
    document.getElementById('auth-form-login').classList.remove('hidden');
    document.getElementById('auth-form-register').classList.add('hidden');
    document.getElementById('auth-tab-login').className = 'text-sky-400 font-bold border-b-2 border-sky-400 pb-2 px-4';
    document.getElementById('auth-tab-register').className = 'text-slate-400 font-medium pb-2 px-4 hover:text-white';
  });

  document.getElementById('auth-tab-register')?.addEventListener('click', () => {
    document.getElementById('auth-form-register').classList.remove('hidden');
    document.getElementById('auth-form-login').classList.add('hidden');
    document.getElementById('auth-tab-register').className = 'text-sky-400 font-bold border-b-2 border-sky-400 pb-2 px-4';
    document.getElementById('auth-tab-login').className = 'text-slate-400 font-medium pb-2 px-4 hover:text-white';
  });

  // Login Form
  document.getElementById('auth-form-login')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const u = document.getElementById('login-username').value.trim();
    const p = document.getElementById('login-password').value.trim();
    try {
      await API.auth.login(u, p);
      showToast('Logged in successfully!', 'success');
      showAuthModal(false);
      state.user = await API.auth.fetchProfile();
      updateUserUI();
      await loadDatasetsList();
      loadDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // Register Form
  document.getElementById('auth-form-register')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const u = document.getElementById('reg-username').value.trim();
    const em = document.getElementById('reg-email').value.trim();
    const p = document.getElementById('reg-password').value.trim();
    try {
      await API.auth.register(u, em, p);
      showToast('Account created and logged in!', 'success');
      showAuthModal(false);
      state.user = await API.auth.fetchProfile();
      updateUserUI();
      await loadDatasetsList();
      loadDashboard();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });

  // 1-Click Demo Login
  document.querySelectorAll('.btn-demo-login').forEach(btn => {
    btn.addEventListener('click', async () => {
      try {
        await API.auth.demoLogin();
        showToast('Logged into Executive Demo workspace!', 'success');
        showAuthModal(false);
        state.user = await API.auth.fetchProfile();
        updateUserUI();
        await loadDatasetsList();
        loadDashboard();
      } catch (err) {
        showToast(err.message, 'error');
      }
    });
  });

  // Logout
  document.getElementById('btn-logout')?.addEventListener('click', async () => {
    await API.auth.logout();
    state.user = null;
    updateUserUI();
    showToast('Logged out.', 'info');
    showAuthModal(true);
  });

  // Initialize
  initAuth();
});

