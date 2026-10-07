/**
 * AadiBI Customer Churn Intelligence - Advanced Frontend Application JS
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 AadiBI Churn Intelligence Advanced Frontend Initialized.');

  // Initialize Data Table System (Search, Filtering, Sorting, Pagination, Drawer)
  initAdvancedTableSystem();

  // Initialize Predictor Presets & Live Slider Simulator
  initPredictorPresets();

  // Initialize AJAX Real-Time Risk Scoring
  initAjaxPredictor();

  // Initialize Drag and Drop Bulk Uploader
  initDragAndDrop();

  // Initialize Drawer Controls
  initDrawerSystem();
});

/* ============================================================
   ADVANCED DATA TABLE SYSTEM (SEARCH, FILTER, SORT, PAGINATION)
   ============================================================ */
function initAdvancedTableSystem() {
  const table = document.getElementById('customerTable');
  const searchInput = document.getElementById('tableSearchInput');
  const filterPills = document.querySelectorAll('.filter-pill');
  const recordsCounter = document.getElementById('visibleRecordsCount');
  const paginationContainer = document.getElementById('paginationControls');

  if (!table) return;

  const tbody = table.querySelector('tbody');
  let allRowsData = [];

  // Parse initial table rows into objects for quick sorting & pagination
  const trElements = Array.from(tbody.querySelectorAll('tr'));
  trElements.forEach((tr, idx) => {
    const cells = tr.querySelectorAll('td');
    if (cells.length < 10) return;

    allRowsData.push({
      element: tr,
      id: parseInt(cells[0].textContent.replace('#', '')) || (idx + 1),
      state: cells[1].textContent.trim(),
      accountLength: parseInt(cells[2].textContent) || 0,
      intlPlan: cells[3].textContent.trim(),
      serviceCalls: parseInt(cells[4].textContent) || 0,
      dayMinutes: parseFloat(cells[5].textContent) || 0,
      churnProbability: parseFloat(cells[6].textContent) || 0,
      risk: tr.getAttribute('data-risk') || 'LOW',
      prediction: tr.getAttribute('data-prediction') || 'STAY',
      signals: cells[8].textContent.trim(),
      action: cells[9].textContent.trim(),
      rawRowText: tr.textContent.toLowerCase()
    });
  });

  let currentFilter = 'ALL';
  let currentSearch = '';
  let sortColumn = 'id';
  let sortDirection = 'asc';
  let currentPage = 1;
  const pageSize = 15;

  function renderTable() {
    // 1. Filter rows
    let filtered = allRowsData.filter(item => {
      const matchesSearch = !currentSearch || item.rawRowText.includes(currentSearch);
      let matchesFilter = true;

      if (currentFilter === 'HIGH') matchesFilter = (item.risk === 'HIGH');
      else if (currentFilter === 'MEDIUM') matchesFilter = (item.risk === 'MEDIUM');
      else if (currentFilter === 'LOW') matchesFilter = (item.risk === 'LOW');
      else if (currentFilter === 'CHURN') matchesFilter = (item.prediction === 'CHURN');
      else if (currentFilter === 'STAY') matchesFilter = (item.prediction === 'STAY');

      return matchesSearch && matchesFilter;
    });

    // 2. Sort rows
    filtered.sort((a, b) => {
      let valA = a[sortColumn];
      let valB = b[sortColumn];

      if (typeof valA === 'string') {
        valA = valA.toLowerCase();
        valB = valB.toLowerCase();
      }

      if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    // 3. Paginate rows
    const totalRecords = filtered.length;
    const totalPages = Math.ceil(totalRecords / pageSize) || 1;
    if (currentPage > totalPages) currentPage = totalPages;

    const startIndex = (currentPage - 1) * pageSize;
    const paginatedItems = filtered.slice(startIndex, startIndex + pageSize);

    // Render tbody
    tbody.innerHTML = '';
    paginatedItems.forEach(item => {
      tbody.appendChild(item.element);
      // Re-attach drawer click listener
      item.element.onclick = () => openCustomerDrawer(item);
    });

    // Update Counter & Pagination Controls
    if (recordsCounter) {
      recordsCounter.textContent = `Showing ${paginatedItems.length} of ${totalRecords} matching accounts (Page ${currentPage} of ${totalPages})`;
    }

    renderPaginationButtons(totalPages);
  }

  function renderPaginationButtons(totalPages) {
    if (!paginationContainer) return;

    let html = `
      <button class="page-btn" id="btnPrevPage" ${currentPage === 1 ? 'disabled' : ''}>&larr; Previous</button>
      <span style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">Page ${currentPage} of ${totalPages}</span>
      <button class="page-btn" id="btnNextPage" ${currentPage >= totalPages ? 'disabled' : ''}>Next &rarr;</button>
    `;
    paginationContainer.innerHTML = html;

    const btnPrev = document.getElementById('btnPrevPage');
    const btnNext = document.getElementById('btnNextPage');

    if (btnPrev) btnPrev.onclick = () => { if (currentPage > 1) { currentPage--; renderTable(); } };
    if (btnNext) btnNext.onclick = () => { if (currentPage < totalPages) { currentPage++; renderTable(); } };
  }

  // Column Sorting Headers
  const headers = table.querySelectorAll('th.sortable');
  headers.forEach(th => {
    th.addEventListener('click', () => {
      const colKey = th.getAttribute('data-sort');
      if (sortColumn === colKey) {
        sortDirection = (sortDirection === 'asc') ? 'desc' : 'asc';
      } else {
        sortColumn = colKey;
        sortDirection = 'desc'; // Default to desc for risk/prob
      }

      headers.forEach(h => {
        h.textContent = h.textContent.replace(' ▲', '').replace(' ▼', '');
      });
      th.textContent += sortDirection === 'asc' ? ' ▲' : ' ▼';

      renderTable();
    });
  });

  // Search input event
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value.trim().toLowerCase();
      currentPage = 1;
      renderTable();
    });
  }

  // Filter pills events
  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentFilter = pill.getAttribute('data-filter') || 'ALL';
      currentPage = 1;
      renderTable();
    });
  });

  // Initial Render
  renderTable();
}

/* ============================================================
   CUSTOMER INSPECTION DRAWER & WHAT-IF MITIGATION SIMULATOR
   ============================================================ */
function initDrawerSystem() {
  const backdrop = document.getElementById('drawerBackdrop');
  const closeBtn = document.getElementById('btnCloseDrawer');

  if (closeBtn && backdrop) {
    closeBtn.onclick = closeCustomerDrawer;
    backdrop.onclick = (e) => {
      if (e.target === backdrop) closeCustomerDrawer();
    };
  }
}

function openCustomerDrawer(customer) {
  const backdrop = document.getElementById('drawerBackdrop');
  if (!backdrop) return;

  // Set Drawer Text
  document.getElementById('drawerCustId').textContent = `#${customer.id}`;
  document.getElementById('drawerState').textContent = customer.state;
  document.getElementById('drawerTenure').textContent = `${customer.accountLength} months`;
  document.getElementById('drawerIntlPlan').textContent = customer.intlPlan;
  document.getElementById('drawerProb').textContent = `${customer.churnProbability}%`;
  document.getElementById('drawerRisk').textContent = customer.risk;
  document.getElementById('drawerSignals').textContent = customer.signals;
  document.getElementById('drawerAction').textContent = customer.action;

  // Render Radar Chart for Customer Usage
  window.AadiCharts.initCustomerRadarChart('drawerRadarCanvas', {
    dayMinutes: customer.dayMinutes,
    eveMinutes: 200,
    nightMinutes: 200,
    intlMinutes: (customer.intlPlan.toLowerCase() === 'yes') ? 12 : 5,
    serviceCalls: customer.serviceCalls
  });

  // Setup What-If Mitigation Simulator Sliders inside Drawer
  const sliderCalls = document.getElementById('drawerSliderSvcCalls');
  const sliderValueCalls = document.getElementById('drawerSliderValSvcCalls');
  const simProbBadge = document.getElementById('drawerSimProbBadge');

  if (sliderCalls && sliderValueCalls) {
    sliderCalls.value = customer.serviceCalls;
    sliderValueCalls.textContent = customer.serviceCalls;

    sliderCalls.oninput = async () => {
      const newCalls = parseInt(sliderCalls.value);
      sliderValueCalls.textContent = newCalls;

      // Run live simulation prediction
      try {
        const res = await fetch('/api/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            state: customer.state,
            account_length: customer.accountLength,
            area_code: 415,
            international_plan: customer.intlPlan,
            customer_service_calls: newCalls,
            total_day_minutes: customer.dayMinutes
          })
        });

        const data = await res.json();
        if (data.success && simProbBadge) {
          simProbBadge.textContent = `${data.churn_probability}% Risk (${data.risk_level})`;
          simProbBadge.className = data.is_churn ? 'badge badge-danger' : 'badge badge-success';
        }
      } catch (e) {
        console.error('Simulation error:', e);
      }
    };
  }

  backdrop.classList.add('active');
}

function closeCustomerDrawer() {
  const backdrop = document.getElementById('drawerBackdrop');
  if (backdrop) backdrop.classList.remove('active');
}

/* ============================================================
   PREDICTOR FORM QUICK PRESETS
   ============================================================ */
function initPredictorPresets() {
  const presetHighRisk = document.getElementById('btnPresetHighRisk');
  const presetLowRisk = document.getElementById('btnPresetLowRisk');
  const presetBorderline = document.getElementById('btnPresetBorderline');
  const form = document.getElementById('individualPredictionForm');

  if (!form) return;

  function setFormValues(data) {
    Object.keys(data).forEach(key => {
      const field = form.querySelector(`[name="${key}"]`);
      if (field) {
        field.value = data[key];
      }
    });
    showToast('Loaded preset profile parameters into form.', 'info');
  }

  if (presetHighRisk) {
    presetHighRisk.addEventListener('click', () => {
      setFormValues({
        state: 'NJ',
        account_length: 137,
        area_code: 415,
        international_plan: 'yes',
        voice_mail_plan: 'no',
        number_vmail_messages: 0,
        total_day_minutes: 268.0,
        total_day_calls: 112,
        total_day_charge: 45.56,
        total_eve_minutes: 240.0,
        total_eve_calls: 105,
        total_eve_charge: 20.40,
        total_night_minutes: 220.0,
        total_night_calls: 95,
        total_night_charge: 9.90,
        total_intl_minutes: 13.5,
        total_intl_calls: 4,
        total_intl_charge: 3.65,
        customer_service_calls: 5
      });
    });
  }

  if (presetLowRisk) {
    presetLowRisk.addEventListener('click', () => {
      setFormValues({
        state: 'CA',
        account_length: 95,
        area_code: 408,
        international_plan: 'no',
        voice_mail_plan: 'yes',
        number_vmail_messages: 32,
        total_day_minutes: 145.2,
        total_day_calls: 98,
        total_day_charge: 24.68,
        total_eve_minutes: 180.5,
        total_eve_calls: 102,
        total_eve_charge: 15.34,
        total_night_minutes: 195.0,
        total_night_calls: 108,
        total_night_charge: 8.78,
        total_intl_minutes: 8.2,
        total_intl_calls: 2,
        total_intl_charge: 2.21,
        customer_service_calls: 0
      });
    });
  }

  if (presetBorderline) {
    presetBorderline.addEventListener('click', () => {
      setFormValues({
        state: 'KS',
        account_length: 128,
        area_code: 510,
        international_plan: 'no',
        voice_mail_plan: 'no',
        number_vmail_messages: 0,
        total_day_minutes: 215.4,
        total_day_calls: 100,
        total_day_charge: 36.62,
        total_eve_minutes: 210.0,
        total_eve_calls: 95,
        total_eve_charge: 17.85,
        total_night_minutes: 210.0,
        total_night_calls: 100,
        total_night_charge: 9.45,
        total_intl_minutes: 11.0,
        total_intl_calls: 3,
        total_intl_charge: 2.97,
        customer_service_calls: 3
      });
    });
  }
}

/* ============================================================
   AJAX REAL-TIME RISK SCORING
   ============================================================ */
function initAjaxPredictor() {
  const form = document.getElementById('individualPredictionForm');
  const resultCard = document.getElementById('liveResultCard');
  const submitBtn = document.getElementById('btnSubmitPrediction');
  if (!form || !resultCard) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '⚡ Computing Risk Scores...';
    }

    const formData = new FormData(form);
    const jsonData = {};
    formData.forEach((val, key) => { jsonData[key] = val; });

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonData)
      });

      const res = await response.json();
      if (res.success) {
        renderPredictionResult(res);
        resultCard.scrollIntoView({ behavior: 'smooth' });
      } else {
        showToast(res.error || 'Prediction failed.', 'error');
      }
    } catch (err) {
      showToast('Network or server error during prediction.', 'error');
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '⚡ Run Predictive Risk Scoring';
      }
    }
  });
}

function renderPredictionResult(res) {
  const resultCard = document.getElementById('liveResultCard');
  if (!resultCard) return;

  resultCard.style.display = 'block';

  const probVal = document.getElementById('resProbVal');
  const predictionBadge = document.getElementById('resPredictionBadge');
  const riskBadge = document.getElementById('resRiskBadge');
  const driversContainer = document.getElementById('resDriversContainer');
  const recommendationBox = document.getElementById('resRecommendationBox');
  const stayProbText = document.getElementById('resStayProbText');
  const churnProbText = document.getElementById('resChurnProbText');
  const gaugeCircle = document.getElementById('gaugeCircle');

  if (probVal) probVal.textContent = `${res.churn_probability}%`;
  if (stayProbText) stayProbText.textContent = `${res.stay_probability}%`;
  if (churnProbText) churnProbText.textContent = `${res.churn_probability}%`;

  if (gaugeCircle) {
    const offset = 264 - (264 * (res.churn_probability / 100));
    gaugeCircle.style.strokeDashoffset = offset;
    gaugeCircle.style.stroke = res.is_churn ? '#EF4444' : '#10B981';
  }

  if (predictionBadge) {
    predictionBadge.textContent = res.prediction;
    predictionBadge.className = res.is_churn ? 'badge badge-danger' : 'badge badge-success';
  }

  if (riskBadge) {
    riskBadge.textContent = `${res.risk_level} RISK`;
    if (res.risk_level === 'HIGH') riskBadge.className = 'badge badge-danger';
    else if (res.risk_level === 'MEDIUM') riskBadge.className = 'badge badge-warning';
    else riskBadge.className = 'badge badge-success';
  }

  if (driversContainer) {
    driversContainer.innerHTML = res.drivers.map(driver => `
      <div style="background: rgba(255,255,255,0.04); padding: 0.5rem 0.85rem; border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.85rem; color: #E5E7EB;">
        ${driver}
      </div>
    `).join('');
  }

  if (recommendationBox) {
    recommendationBox.textContent = res.recommendation;
  }
}

/* ============================================================
   DRAG AND DROP BULK UPLOADER
   ============================================================ */
function initDragAndDrop() {
  const dropzone = document.getElementById('uploadDropzone');
  const fileInput = document.getElementById('datasetFileInput');
  const fileNameDisplay = document.getElementById('selectedFileName');
  const uploadForm = document.getElementById('bulkUploadForm');
  const uploadBtn = document.getElementById('btnSubmitBulkUpload');

  if (!dropzone || !fileInput) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      fileInput.files = files;
      updateFileName(files[0].name);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
      updateFileName(fileInput.files[0].name);
    }
  });

  function updateFileName(name) {
    if (fileNameDisplay) {
      fileNameDisplay.innerHTML = `📄 <strong>Selected File:</strong> ${name}`;
      fileNameDisplay.style.display = 'block';
    }
  }

  if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (!fileInput.files || fileInput.files.length === 0) {
        showToast('Please select a dataset file before submitting.', 'warning');
        return;
      }

      if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '⌛ Analyzing Dataset & Calculating Churn Metrics...';
      }

      const formData = new FormData(uploadForm);
      try {
        const response = await fetch('/api/bulk_predict', {
          method: 'POST',
          body: formData
        });

        const res = await response.json();
        if (res.success) {
          showToast('Dataset analyzed successfully! Redirecting to dashboard...', 'success');
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 1200);
        } else {
          showToast(res.error || 'Dataset analysis failed.', 'error');
        }
      } catch (err) {
        showToast('Error uploading dataset.', 'error');
      } finally {
        if (uploadBtn) {
          uploadBtn.disabled = false;
          uploadBtn.innerHTML = '📊 Run Batch Dataset Analytics';
        }
      }
    });
  }
}

/* ============================================================
   TOAST NOTIFICATION SYSTEM
   ============================================================ */
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const bgColors = {
    success: 'rgba(16, 185, 129, 0.95)',
    error: 'rgba(239, 68, 68, 0.95)',
    warning: 'rgba(245, 158, 11, 0.95)',
    info: 'rgba(59, 130, 246, 0.95)'
  };

  toast.style.cssText = `
    background: ${bgColors[type] || bgColors.info};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 600;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    opacity: 0;
    transform: translateY(10px);
  `;
  toast.textContent = message;

  toastContainer.appendChild(toast);
  requestAnimationFrame(() => {
    toast.style.opacity = '1';
    toast.style.transform = 'translateY(0)';
  });

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
