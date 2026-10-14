/**
 * AadiBI Customer Churn Intelligence - Advanced Frontend Application JS
 */

document.addEventListener('DOMContentLoaded', () => {
  console.log('🚀 AadiBI Churn Intelligence Advanced Frontend Initialized.');

  // Initialize Dark / Light Theme Toggle
  initThemeToggle();

  // Initialize Animated KPI Counters
  initAnimatedCounters();

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

  // Initialize Model Retrain Action Handler
  initModelRetrainHandler();

  // Initialize Global Interactive Graph Zoom & Lightbox Inspector
  initGraphZoomViewer();
});

/* ============================================================
   DARK & LIGHT THEME TOGGLE SYSTEM
   ============================================================ */
function initThemeToggle() {
  const toggleBtn = document.getElementById('themeToggleBtn');
  const toggleIcon = document.getElementById('themeToggleIcon');
  const toggleText = document.getElementById('themeToggleText');

  const currentTheme = localStorage.getItem('aadi_theme') || 'dark';
  applyTheme(currentTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      applyTheme(newTheme);
      showToast(`Switched to ${newTheme.toUpperCase()} mode!`, 'info');
    });
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('aadi_theme', theme);

    if (toggleIcon && toggleText) {
      if (theme === 'light') {
        toggleIcon.textContent = '☀️';
        toggleText.textContent = 'Light';
      } else {
        toggleIcon.textContent = '🌙';
        toggleText.textContent = 'Dark';
      }
    }

    if (window.AadiCharts && typeof window.AadiCharts.updateTheme === 'function') {
      window.AadiCharts.updateTheme();
    }
  }
}

/* ============================================================
   ANIMATED KPI STAT COUNTERS
   ============================================================ */
function initAnimatedCounters() {
  const kpiValues = document.querySelectorAll('.kpi-value');
  kpiValues.forEach(el => {
    const rawText = el.textContent.trim();
    if (!rawText) return;

    if (rawText.startsWith('$') || rawText.startsWith('₹')) {
      const num = parseFloat(rawText.replace(/[^0-9.]/g, ''));
      if (isNaN(num)) return;
      animateNumber(el, num, (val) => '₹' + Math.round(val).toLocaleString('en-IN'));
    } else if (rawText.endsWith('%')) {
      const num = parseFloat(rawText.replace(/[^0-9.]/g, ''));
      if (isNaN(num)) return;
      animateNumber(el, num, (val) => val.toFixed(1) + '%');
    } else {
      const num = parseInt(rawText.replace(/[^0-9]/g, ''));
      if (isNaN(num)) return;
      animateNumber(el, num, (val) => Math.round(val).toLocaleString());
    }
  });

  function animateNumber(element, targetNum, formatFn) {
    const duration = 1000;
    const startTime = performance.now();

    function step(now) {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = targetNum * easeOut;

      element.textContent = formatFn(current);

      if (progress < 1) {
        requestAnimationFrame(step);
      }
    }
    requestAnimationFrame(step);
  }
}

/* ============================================================
   EXECUTIVE EXPORT STUDIO (PDF & FILTERED CSV EXPORT)
   ============================================================ */
window.exportExecutivePDF = function() {
  showToast('Preparing Executive PDF Summary Report...', 'info');
  setTimeout(() => {
    window.print();
  }, 300);
};

window.exportFilteredCSV = function() {
  const filteredData = window.activeFilteredData || [];
  if (filteredData.length === 0) {
    showToast('No customer records available to export.', 'warning');
    return;
  }

  const headers = ["ID", "State", "Tenure (months)", "Intl Plan", "Service Calls", "Total Day Mins", "Churn Probability (%)", "Risk Level", "Risk Signals", "Recommended Action"];
  const rows = filteredData.map(item => [
    item.id,
    `"${item.state}"`,
    item.accountLength,
    `"${item.intlPlan}"`,
    item.serviceCalls,
    item.dayMinutes,
    item.churnProbability,
    `"${item.risk}"`,
    `"${(item.signals || '').replace(/"/g, '""')}"`,
    `"${(item.action || '').replace(/"/g, '""')}"`
  ]);

  const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `AadiBI_Filtered_Customer_Churn_Report_${new Date().toISOString().slice(0,10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`Successfully exported ${filteredData.length} filtered customer records to CSV!`, 'success');
};

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
      else if (currentFilter === 'SVC_CALLS') matchesFilter = (item.serviceCalls >= 3);
      else if (currentFilter === 'HIGH_DAY') matchesFilter = (item.dayMinutes >= 200);

      return matchesSearch && matchesFilter;
    });

    // Save active filtered data for export
    window.activeFilteredData = filtered;

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
    if (paginatedItems.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="10" style="text-align: center; padding: 2.5rem; color: var(--text-muted);">
            🔍 <strong>No matching customer accounts found</strong>${currentSearch ? ` matching "${currentSearch}"` : ''}.<br>
            <span style="font-size: 0.82rem; opacity: 0.8; margin-top: 0.35rem; display: block;">Try clearing your search query or selecting a different filter pill.</span>
          </td>
        </tr>
      `;
    } else {
      paginatedItems.forEach(item => {
        tbody.appendChild(item.element);
        // Re-attach drawer click listener
        item.element.onclick = () => openCustomerDrawer(item);
      });
    }

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

let activeCustomerDrawerData = null;
let currentCampaignData = null;

function openCustomerDrawer(customer) {
  const backdrop = document.getElementById('drawerBackdrop');
  if (!backdrop) return;

  activeCustomerDrawerData = customer;

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

  // Setup What-If Retention Simulator Sliders inside Drawer
  const sliderCalls = document.getElementById('drawerSliderSvcCalls');
  const labelCalls = document.getElementById('drawerSliderValSvcCalls');

  const sliderDayMins = document.getElementById('drawerSliderDayMins');
  const labelDayMins = document.getElementById('drawerSliderValDayMins');

  const selectDiscount = document.getElementById('drawerSelectDiscount');
  const labelDiscount = document.getElementById('drawerValDiscount');

  if (sliderCalls) {
    sliderCalls.value = customer.serviceCalls;
    if (labelCalls) labelCalls.textContent = customer.serviceCalls;
  }

  if (sliderDayMins) {
    sliderDayMins.value = Math.min(400, Math.round(customer.dayMinutes || 180));
    if (labelDayMins) labelDayMins.textContent = `${sliderDayMins.value}m`;
  }

  if (selectDiscount) {
    selectDiscount.value = "15";
    if (labelDiscount) labelDiscount.textContent = "15% Off";
  }

  const runDrawerSimulation = async () => {
    const svcCalls = sliderCalls ? parseInt(sliderCalls.value) : customer.serviceCalls;
    const dayMins = sliderDayMins ? parseFloat(sliderDayMins.value) : customer.dayMinutes;
    const discount = selectDiscount ? parseFloat(selectDiscount.value) : 15;

    if (labelCalls) labelCalls.textContent = svcCalls;
    if (labelDayMins) labelDayMins.textContent = `${Math.round(dayMins)}m`;
    if (labelDiscount) labelDiscount.textContent = `${discount}% Off`;

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          state: customer.state,
          account_length: customer.accountLength,
          area_code: 415,
          international_plan: customer.intlPlan,
          customer_service_calls: svcCalls,
          total_day_minutes: dayMins,
          discount_percent: discount,
          original_probability: customer.churnProbability
        })
      });

      const data = await res.json();
      if (data.success) {
        const simBadge = document.getElementById('drawerSimProbBadge');
        if (simBadge) {
          const delta = data.delta_probability;
          if (delta <= 0) {
            simBadge.textContent = `⬇️ ${Math.abs(delta).toFixed(1)}% Risk Reduced`;
            simBadge.className = 'badge badge-success';
          } else {
            simBadge.textContent = `⬆️ +${delta.toFixed(1)}% Risk Increase`;
            simBadge.className = 'badge badge-danger';
          }
        }

        // Update probability display
        const drawerProb = document.getElementById('drawerProb');
        const drawerRisk = document.getElementById('drawerRisk');
        if (drawerProb) drawerProb.textContent = `${data.churn_probability}%`;
        if (drawerRisk) drawerRisk.textContent = data.risk_level;

        // Update AI Campaign Voucher Box
        if (data.campaign) {
          currentCampaignData = data.campaign;
          const codeBadge = document.getElementById('drawerVoucherCodeBadge');
          const titleEl = document.getElementById('drawerCampaignTitle');
          const detailsEl = document.getElementById('drawerCampaignDetails');

          if (codeBadge) codeBadge.textContent = data.campaign.voucher_code;
          if (titleEl) titleEl.textContent = data.campaign.title;
          if (detailsEl) detailsEl.textContent = `${data.campaign.details} (${data.campaign.discount_offer})`;
        }
      }
    } catch (e) {
      console.error('Drawer simulation error:', e);
    }
  };

  if (sliderCalls) sliderCalls.oninput = runDrawerSimulation;
  if (sliderDayMins) sliderDayMins.oninput = runDrawerSimulation;
  if (selectDiscount) selectDiscount.onchange = runDrawerSimulation;

  // Voucher Copy & Download Brief Action Event Listeners
  const btnCopy = document.getElementById('btnCopyVoucher');
  const btnDownload = document.getElementById('btnDownloadBrief');

  if (btnCopy) {
    btnCopy.onclick = () => {
      const code = currentCampaignData ? currentCampaignData.voucher_code : 'LOYALTY-HERO-15';
      navigator.clipboard.writeText(code);
      showToast(`Voucher Code "${code}" copied to clipboard!`, 'success');
    };
  }

  if (btnDownload) {
    btnDownload.onclick = () => {
      downloadCampaignBrief(customer, currentCampaignData);
    };
  }

  // Initial simulation run
  runDrawerSimulation();

  backdrop.classList.add('active');
}

function closeCustomerDrawer() {
  const backdrop = document.getElementById('drawerBackdrop');
  if (backdrop) backdrop.classList.remove('active');
}

function downloadCampaignBrief(customer, campaign) {
  const code = campaign ? campaign.voucher_code : 'LOYALTY-HERO-15';
  const title = campaign ? campaign.title : 'Customer Retention Brief';
  const copyText = campaign ? campaign.campaign_copy : 'Standard retention voucher.';

  const briefContent = `
============================================================
AadiBI CUSTOMER RETENTION CAMPAIGN BRIEF
============================================================
Generated: ${new Date().toLocaleString()}
Target Customer ID: #${customer.id} (State: ${customer.state})
Tenure: ${customer.accountLength} months
Base Churn Risk: ${customer.churnProbability}% (${customer.risk})

RETAINMENT PACKAGE OVERVIEW
------------------------------------------------------------
Campaign Package: ${title}
Voucher Code: ${code}
Actionable Strategy: ${customer.action}

AUTOMATED MARKETING & RETENTION COPY
------------------------------------------------------------
${copyText}

============================================================
AadiBI Intelligence System - Confidential Retention Document
============================================================
  `.trim();

  const blob = new Blob([briefContent], { type: 'text/plain;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `AadiBI_Retention_Brief_Cust_${customer.id}_${code}.txt`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showToast(`Downloaded Retention Campaign Brief for Customer #${customer.id}!`, 'success');
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
      <div class="driver-tag">
        ${driver}
      </div>
    `).join('');
  }

  if (recommendationBox) {
    recommendationBox.textContent = res.recommendation;
  }

  // Update AI Campaign Voucher Code
  const predictVoucherCode = document.getElementById('predictVoucherCode');
  const btnCopyPredictVoucher = document.getElementById('btnCopyPredictVoucher');
  const btnDownloadPredictBrief = document.getElementById('btnDownloadPredictBrief');

  const code = (res.risk_level === 'HIGH') ? 'PRIORITY-VIP-CARE' : ((res.risk_level === 'MEDIUM') ? 'DAYTIME-SAVER-15' : 'LOYALTY-HERO-10');
  if (predictVoucherCode) predictVoucherCode.textContent = code;

  if (btnCopyPredictVoucher) {
    btnCopyPredictVoucher.onclick = () => {
      navigator.clipboard.writeText(code);
      showToast(`Voucher code "${code}" copied to clipboard!`, 'success');
    };
  }

  if (btnDownloadPredictBrief) {
    btnDownloadPredictBrief.onclick = () => {
      downloadCampaignBrief(
        { id: 'PREDICT-ACC', state: 'US', accountLength: 12, churnProbability: res.churn_probability, risk: res.risk_level, action: res.recommendation },
        { voucher_code: code, title: 'Single Account Retention Brief', campaign_copy: `Voucher Code: ${code}\nRecommended Action: ${res.recommendation}` }
      );
    };
  }
}

/* ============================================================
   UNIVERSAL DATASET SCHEMA MAPPER & BATCH WIZARD
   ============================================================ */
let uploadWizardState = {
  tempFileId: null,
  filename: '',
  columns: [],
  preview: [],
  suggestedMapping: {},
  confidenceScores: {},
  matchDetails: {},
  canonicalFeatures: {},
  results: null
};

window.switchWizardStep = function(step) {
  const step1 = document.getElementById('step1Container');
  const step2 = document.getElementById('step2Container');
  const step3 = document.getElementById('step3Container');
  const node1 = document.getElementById('wizardNode1');
  const node2 = document.getElementById('wizardNode2');
  const node3 = document.getElementById('wizardNode3');

  if (!step1) return;

  if (step === 2 && !uploadWizardState.tempFileId) {
    showToast('Please upload a dataset file in Step 1 first.', 'warning');
    return;
  }
  if (step === 3 && !uploadWizardState.results) {
    showToast('Please run predictions in Step 2 first.', 'warning');
    return;
  }

  // Helper to update stepper node class & badge text
  function updateStepNode(node, stepNum, state) {
    if (!node) return;
    node.className = ('light-step-item wizard-step-node ' + state).trim();
    const badge = node.querySelector('.step-badge') || node.querySelector('.step-circle');
    if (badge) {
      if (state.includes('completed') && !state.includes('active')) {
        badge.textContent = '✓';
      } else {
        badge.textContent = stepNum;
      }
    }
  }

  // Update Containers
  if (step === 1) {
    step1.style.display = 'block';
    if (step2) step2.style.display = 'none';
    if (step3) step3.style.display = 'none';

    updateStepNode(node1, 1, 'active');
    updateStepNode(node2, 2, uploadWizardState.tempFileId ? 'completed' : '');
    updateStepNode(node3, 3, uploadWizardState.results ? 'completed' : '');
  } else if (step === 2) {
    if (step1) step1.style.display = 'none';
    step2.style.display = 'block';
    if (step3) step3.style.display = 'none';

    updateStepNode(node1, 1, 'completed');
    updateStepNode(node2, 2, 'active');
    updateStepNode(node3, 3, uploadWizardState.results ? 'completed' : '');
  } else if (step === 3) {
    if (step1) step1.style.display = 'none';
    if (step2) step2.style.display = 'none';
    step3.style.display = 'block';

    updateStepNode(node1, 1, 'completed');
    updateStepNode(node2, 2, 'completed');
    updateStepNode(node3, 3, 'active');
  }
};

function initDragAndDrop() {
  const dropzone = document.getElementById('uploadDropzone');
  const fileInput = document.getElementById('datasetFileInput');
  const fileInfoBox = document.getElementById('selectedFileInfoBox');
  const fileInfoText = document.getElementById('fileInfoText');
  const fileSizeBadge = document.getElementById('fileSizeBadge');
  const btnUploadAndDetect = document.getElementById('btnUploadAndDetect');

  const btnResetToAutoMatch = document.getElementById('btnResetToAutoMatch');
  const btnTogglePreview = document.getElementById('btnTogglePreview');
  const previewTableContainer = document.getElementById('previewTableContainer');
  const btnBackToStep1 = document.getElementById('btnBackToStep1');
  const btnRunMappedPredictions = document.getElementById('btnRunMappedPredictions');
  const btnScoreAnother = document.getElementById('btnScoreAnother');

  if (!dropzone || !fileInput) return;

  // Drag & Drop event bindings
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, e => {
      e.preventDefault();
      e.stopPropagation();
    }, false);
  });

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      fileInput.files = dt.files;
      handleFileSelected(dt.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  function handleFileSelected(file) {
    if (fileInfoBox && fileInfoText && fileSizeBadge) {
      fileInfoText.innerHTML = `📄 <strong>Selected:</strong> ${file.name}`;
      const sizeKb = (file.size / 1024).toFixed(1);
      fileSizeBadge.textContent = sizeKb > 1024 ? `${(sizeKb / 1024).toFixed(2)} MB` : `${sizeKb} KB`;
      fileInfoBox.style.display = 'block';
    }
  }

  // Step 1: Upload & Auto-Detect Schema
  if (btnUploadAndDetect) {
    btnUploadAndDetect.addEventListener('click', async () => {
      if (!fileInput.files || fileInput.files.length === 0) {
        showToast('Please select or drop a dataset file first.', 'warning');
        return;
      }

      btnUploadAndDetect.disabled = true;
      btnUploadAndDetect.innerHTML = '⌛ Scanning & Auto-Matching Columns...';

      const formData = new FormData();
      formData.append('dataset', fileInput.files[0]);

      try {
        const response = await fetch('/api/upload_preview', {
          method: 'POST',
          body: formData
        });

        const res = await response.json();
        if (!res.success) {
          showToast(res.error || 'Failed to parse dataset schema.', 'error');
          return;
        }

        // Store state
        uploadWizardState.tempFileId = res.temp_file_id;
        uploadWizardState.filename = res.filename;
        uploadWizardState.columns = res.columns || [];
        uploadWizardState.preview = res.preview || [];
        uploadWizardState.suggestedMapping = res.suggested_mapping || {};
        uploadWizardState.confidenceScores = res.confidence_scores || {};
        uploadWizardState.matchDetails = res.match_details || {};
        uploadWizardState.canonicalFeatures = res.canonical_features || {};

        // Render Schema Mapper Table
        renderSchemaMapperTable();

        // Render Data Preview
        renderDataPreview();

        // Update Step 2 Summary text
        const summaryEl = document.getElementById('schemaDetectionSummary');
        if (summaryEl) {
          const matchedCount = Object.keys(uploadWizardState.suggestedMapping).length;
          const totalTargets = Object.keys(uploadWizardState.canonicalFeatures).length;
          summaryEl.innerHTML = `Scanned <strong>${res.filename}</strong> (${res.row_count} records, ${res.columns.length} columns). <strong>${matchedCount} of ${totalTargets}</strong> predictive signals auto-aligned.`;
        }

        showToast('Dataset columns successfully detected & auto-matched!', 'success');
        switchWizardStep(2);
      } catch (err) {
        console.error(err);
        showToast('Error uploading dataset to schema mapper.', 'error');
      } finally {
        btnUploadAndDetect.disabled = false;
        btnUploadAndDetect.innerHTML = '⚡ Upload & Auto-Detect Schema →';
      }
    });
  }

  // Render Mapping Table
  function renderSchemaMapperTable() {
    const tbody = document.getElementById('schemaMappingBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    const userCols = uploadWizardState.columns;
    const canonical = uploadWizardState.canonicalFeatures;
    const suggested = uploadWizardState.suggestedMapping;

    Object.keys(canonical).forEach(featureKey => {
      const feat = canonical[featureKey];
      const tr = document.createElement('tr');

      // Column 1: Feature Target + Concept
      const tdTarget = document.createElement('td');
      tdTarget.innerHTML = `
        <div style="font-weight: 700; color: var(--text-main); font-size: 0.88rem;">${feat.display_name || featureKey}</div>
        <div class="concept-badge">${feat.domain_concept || 'Canonical Feature'}</div>
        <div style="font-size: 0.74rem; color: var(--text-muted); margin-top: 0.2rem;">${feat.description || ''}</div>
      `;

      // Column 2: User Column Selector
      const tdSelect = document.createElement('td');
      const select = document.createElement('select');
      select.className = 'schema-select';
      select.setAttribute('data-canonical-key', featureKey);

      // Option: None / Fallback default
      const optNone = document.createElement('option');
      optNone.value = '__NONE__';
      optNone.textContent = `(None / Use Default: ${feat.default})`;
      select.appendChild(optNone);

      // Add all user CSV columns
      const matchedUserCol = suggested[featureKey];
      userCols.forEach(uc => {
        const opt = document.createElement('option');
        opt.value = uc;
        opt.textContent = uc;
        if (matchedUserCol && matchedUserCol === uc) {
          opt.selected = true;
        }
        select.appendChild(opt);
      });

      tdSelect.appendChild(select);

      // Column 3: Match Badge
      const tdBadge = document.createElement('td');
      tdBadge.id = `badge-${featureKey.replace(/[^a-zA-Z0-9]/g, '_')}`;
      updateBadgeElement(tdBadge, featureKey, select.value);

      // When user changes select dropdown
      select.addEventListener('change', () => {
        updateBadgeElement(tdBadge, featureKey, select.value);
      });

      // Column 4: Fallback Default
      const tdDefault = document.createElement('td');
      tdDefault.style.fontSize = '0.82rem';
      tdDefault.style.color = 'var(--text-muted)';
      tdDefault.innerHTML = `<span class="mono">${feat.default}</span>`;

      tr.appendChild(tdTarget);
      tr.appendChild(tdSelect);
      tr.appendChild(tdBadge);
      tr.appendChild(tdDefault);
      tbody.appendChild(tr);
    });
  }

  function updateBadgeElement(badgeCell, featureKey, selectedValue) {
    const details = uploadWizardState.matchDetails[featureKey];
    if (selectedValue === '__NONE__') {
      badgeCell.innerHTML = `<span class="schema-badge default">Default Fallback</span>`;
    } else if (details && details.user_col === selectedValue) {
      if (details.match_type === 'exact') {
        badgeCell.innerHTML = `<span class="schema-badge exact">✓ Exact (100%)</span>`;
      } else if (details.match_type === 'synonym') {
        badgeCell.innerHTML = `<span class="schema-badge synonym">⚡ Synonym (${Math.round(details.confidence * 100)}%)</span>`;
      } else {
        badgeCell.innerHTML = `<span class="schema-badge fuzzy">≈ Fuzzy (${Math.round(details.confidence * 100)}%)</span>`;
      }
    } else {
      badgeCell.innerHTML = `<span class="schema-badge exact">✎ User Mapped</span>`;
    }
  }

  // Render Data Preview
  function renderDataPreview() {
    const head = document.getElementById('previewTableHead');
    const body = document.getElementById('previewTableBody');
    const countEl = document.getElementById('previewRowCount');
    if (!head || !body) return;

    head.innerHTML = '';
    body.innerHTML = '';

    const cols = uploadWizardState.columns;
    const rows = uploadWizardState.preview;

    if (countEl) {
      countEl.textContent = `Showing ${rows.length} sample rows (${cols.length} columns)`;
    }

    // Header row
    const trHead = document.createElement('tr');
    cols.forEach(c => {
      const th = document.createElement('th');
      th.style.padding = '0.5rem 0.75rem';
      th.style.whiteSpace = 'nowrap';
      th.textContent = c;
      trHead.appendChild(th);
    });
    head.appendChild(trHead);

    // Body rows
    rows.forEach(r => {
      const tr = document.createElement('tr');
      cols.forEach(c => {
        const td = document.createElement('td');
        td.style.padding = '0.45rem 0.75rem';
        td.style.whiteSpace = 'nowrap';
        td.textContent = r[c] !== null && r[c] !== undefined ? r[c] : '—';
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
  }

  // Step 2 Action: Toggle Preview Drawer
  if (btnTogglePreview && previewTableContainer) {
    btnTogglePreview.addEventListener('click', () => {
      const isVisible = previewTableContainer.style.display !== 'none';
      previewTableContainer.style.display = isVisible ? 'none' : 'block';
      btnTogglePreview.textContent = isVisible ? '👁️ Preview Data (First 5 Rows)' : '▲ Hide Data Preview';
    });
  }

  // Step 2 Action: Reset Auto Match
  if (btnResetToAutoMatch) {
    btnResetToAutoMatch.addEventListener('click', () => {
      const selects = document.querySelectorAll('.schema-select');
      const suggested = uploadWizardState.suggestedMapping;
      selects.forEach(sel => {
        const featKey = sel.getAttribute('data-canonical-key');
        if (suggested[featKey]) {
          sel.value = suggested[featKey];
        } else {
          sel.value = '__NONE__';
        }
        const badgeCell = document.getElementById(`badge-${featKey.replace(/[^a-zA-Z0-9]/g, '_')}`);
        if (badgeCell) updateBadgeElement(badgeCell, featKey, sel.value);
      });
      showToast('Reset all columns to AI auto-match values.', 'info');
    });
  }

  // Step 2 Action: Back to Step 1
  if (btnBackToStep1) {
    btnBackToStep1.addEventListener('click', () => {
      switchWizardStep(1);
    });
  }

  // Step 2 Action: Run Mapped Predictions
  if (btnRunMappedPredictions) {
    btnRunMappedPredictions.addEventListener('click', async () => {
      if (!uploadWizardState.tempFileId) {
        showToast('No active uploaded file session.', 'error');
        return;
      }

      // Collect user mapping
      const mapping = {};
      const selects = document.querySelectorAll('.schema-select');
      selects.forEach(sel => {
        const featKey = sel.getAttribute('data-canonical-key');
        if (sel.value && sel.value !== '__NONE__') {
          mapping[featKey] = sel.value;
        }
      });

      btnRunMappedPredictions.disabled = true;
      btnRunMappedPredictions.innerHTML = '⌛ Generating Predictions & Risk Signals...';

      try {
        const response = await fetch('/api/process_mapped_dataset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            temp_file_id: uploadWizardState.tempFileId,
            mapping: mapping
          })
        });

        const res = await response.json();
        if (!res.success) {
          showToast(res.error || 'Failed to process dataset scoring.', 'error');
          return;
        }

        uploadWizardState.results = res;

        // Populate Step 3 KPI results
        const totalEl = document.getElementById('resTotalRecords');
        const churnRateEl = document.getElementById('resChurnRate');
        const churnCountEl = document.getElementById('resChurnCount');
        const revRiskEl = document.getElementById('resRevenueRisk');

        if (totalEl) totalEl.textContent = res.total_records.toLocaleString();
        if (churnRateEl) churnRateEl.textContent = `${res.churn_rate}%`;
        if (churnCountEl) churnCountEl.textContent = res.churn_count.toLocaleString();
        if (revRiskEl) {
          const revVal = res.churn_count * 5400;
          revRiskEl.textContent = '₹' + revVal.toLocaleString('en-IN');
        }

        showToast('Batch predictions complete! Results ready for export.', 'success');
        switchWizardStep(3);
      } catch (err) {
        console.error(err);
        showToast('Error scoring mapped dataset.', 'error');
      } finally {
        btnRunMappedPredictions.disabled = false;
        btnRunMappedPredictions.innerHTML = '🚀 Run Predictions & Analytics →';
      }
    });
  }

  // Step 3 Action: Score Another Dataset
  if (btnScoreAnother) {
    btnScoreAnother.addEventListener('click', () => {
      uploadWizardState = {
        tempFileId: null,
        filename: '',
        columns: [],
        preview: [],
        suggestedMapping: {},
        confidenceScores: {},
        matchDetails: {},
        canonicalFeatures: {},
        results: null
      };
      if (fileInput) fileInput.value = '';
      if (fileInfoBox) fileInfoBox.style.display = 'none';
      switchWizardStep(1);
      showToast('Wizard reset. Select a new dataset to begin.', 'info');
    });
  }
}

/* ============================================================
   MODEL RETRAINING ACTION HANDLER
   ============================================================ */
function initModelRetrainHandler() {
  const btnBulk = document.getElementById('btnTriggerRetrainBulk');
  const btnAbout = document.getElementById('btnTriggerRetrainAbout');
  const resultBoxBulk = document.getElementById('retrainResultBoxBulk');

  const handleRetrain = async (btn) => {
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⌛ Retraining Random Forest...';
    }

    try {
      showToast('Initiating ML pipeline retraining on dataset...', 'info');
      const res = await fetch('/api/retrain', { method: 'POST' });
      const data = await res.json();

      if (data.success) {
        showToast('ML Model retrained & plots updated successfully!', 'success');
        if (resultBoxBulk) {
          resultBoxBulk.style.display = 'block';
          resultBoxBulk.innerHTML = `
            <div style="color: #34D399; font-weight: 700; margin-bottom: 0.5rem;">✅ Retraining Complete! Evaluation Metrics:</div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 0.5rem; font-family: var(--font-mono); font-size: 0.85rem;">
              <div>Accuracy: <strong>${(data.metrics.accuracy * 100).toFixed(1)}%</strong></div>
              <div>Precision: <strong>${(data.metrics.precision * 100).toFixed(1)}%</strong></div>
              <div>Recall: <strong>${(data.metrics.recall * 100).toFixed(1)}%</strong></div>
              <div>F1 Score: <strong>${(data.metrics.f1_score * 100).toFixed(1)}%</strong></div>
              <div>ROC-AUC: <strong>${data.metrics.roc_auc.toFixed(3)}</strong></div>
            </div>
          `;
        }
        if (window.location.pathname.includes('/about')) {
          setTimeout(() => { window.location.reload(); }, 1200);
        }
      } else {
        showToast(data.error || 'Retraining failed.', 'error');
      }
    } catch (err) {
      showToast('Error connecting to ML retrain pipeline.', 'error');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = '🔄 Trigger Model Retraining';
      }
    }
  };

  if (btnBulk) btnBulk.addEventListener('click', () => handleRetrain(btnBulk));
  if (btnAbout) btnAbout.addEventListener('click', () => handleRetrain(btnAbout));
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

/* ==========================================================================
   Interactive Graph Zoom & Lightbox System
   ========================================================================== */
function initGraphZoomViewer() {
  const modal = document.getElementById('graphZoomModal');
  const backdrop = document.getElementById('graphZoomBackdrop');
  const closeBtn = document.getElementById('btnGraphZoomClose');
  const imgElement = document.getElementById('graphZoomImage');
  const titleElement = document.getElementById('graphZoomTitle');
  const levelElement = document.getElementById('graphZoomLevel');
  const wrapper = document.getElementById('graphZoomWrapper');
  const viewport = document.getElementById('graphZoomViewport');
  const btnZoomIn = document.getElementById('btnGraphZoomIn');
  const btnZoomOut = document.getElementById('btnGraphZoomOut');
  const btnReset = document.getElementById('btnGraphZoomReset');
  const btnDownload = document.getElementById('btnGraphZoomDownload');

  if (!modal || !imgElement || !viewport || !wrapper) return;

  let scale = 1.0;
  let translateX = 0;
  let translateY = 0;
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;

  function updateTransform() {
    if (scale <= 1.0) {
      translateX = 0;
      translateY = 0;
      wrapper.style.cursor = 'zoom-in';
    } else {
      wrapper.style.cursor = isDragging ? 'grabbing' : 'grab';
    }
    wrapper.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    if (levelElement) {
      levelElement.textContent = `${Math.round(scale * 100)}%`;
    }
  }

  function setScale(newScale) {
    scale = Math.max(0.5, Math.min(4.0, Math.round(newScale * 100) / 100));
    updateTransform();
  }

  function resetZoom() {
    scale = 1.0;
    translateX = 0;
    translateY = 0;
    updateTransform();
  }

  window.openGraphZoom = function(src, title) {
    if (!src) return;
    imgElement.src = src;
    if (titleElement) titleElement.textContent = title || 'Graph Visualization';
    if (btnDownload) {
      btnDownload.href = src;
      const filename = (title || 'graph').toLowerCase().replace(/[^a-z0-9]/g, '_') + '.png';
      btnDownload.setAttribute('download', filename);
    }
    resetZoom();
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  window.closeGraphZoom = function() {
    modal.classList.remove('open');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    setTimeout(resetZoom, 200);
  };

  // Close handlers
  if (closeBtn) closeBtn.addEventListener('click', window.closeGraphZoom);
  if (backdrop) backdrop.addEventListener('click', window.closeGraphZoom);

  // Zoom control buttons
  if (btnZoomIn) {
    btnZoomIn.addEventListener('click', (e) => {
      e.stopPropagation();
      setScale(scale + 0.25);
    });
  }
  if (btnZoomOut) {
    btnZoomOut.addEventListener('click', (e) => {
      e.stopPropagation();
      setScale(scale - 0.25);
    });
  }
  if (btnReset) {
    btnReset.addEventListener('click', (e) => {
      e.stopPropagation();
      resetZoom();
    });
  }

  // Mouse wheel zoom
  viewport.addEventListener('wheel', (e) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 0.15 : -0.15;
    setScale(scale + zoomFactor);
  }, { passive: false });

  // Drag & pan interactions when zoomed
  wrapper.addEventListener('mousedown', (e) => {
    if (scale <= 1.0) return;
    isDragging = true;
    dragStartX = e.clientX - translateX;
    dragStartY = e.clientY - translateY;
    wrapper.style.cursor = 'grabbing';
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    translateX = e.clientX - dragStartX;
    translateY = e.clientY - dragStartY;
    updateTransform();
  });

  window.addEventListener('mouseup', () => {
    if (isDragging) {
      isDragging = false;
      updateTransform();
    }
  });

  // Double click toggles 1x and 2x zoom
  wrapper.addEventListener('dblclick', (e) => {
    e.preventDefault();
    if (scale > 1.0) {
      resetZoom();
    } else {
      setScale(2.0);
    }
  });

  // Keyboard navigation
  window.addEventListener('keydown', (e) => {
    if (!modal.classList.contains('open')) return;
    if (e.key === 'Escape') {
      window.closeGraphZoom();
    } else if (e.key === '+' || e.key === '=') {
      setScale(scale + 0.25);
    } else if (e.key === '-' || e.key === '_') {
      setScale(scale - 0.25);
    } else if (e.key === '0') {
      resetZoom();
    }
  });

  // Auto-bind click to all zoomable images & containers across the app
  document.querySelectorAll('.zoom-img-container, .zoomable-graph-img, [data-zoomable="true"]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      const img = el.tagName === 'IMG' ? el : el.querySelector('img');
      if (img && img.src) {
        const title = el.getAttribute('data-graph-title') || img.alt || img.title || 'Graph Plot';
        openGraphZoom(img.src, title);
      }
    });
  });

  // Also support clicking Chart.js canvas charts to inspect in high resolution
  document.querySelectorAll('.chart-card canvas, canvas.zoomable-canvas').forEach(canvas => {
    canvas.style.cursor = 'zoom-in';
    canvas.title = 'Click to expand & zoom graph';
    canvas.addEventListener('click', () => {
      try {
        const dataUrl = canvas.toDataURL('image/png');
        const parentCard = canvas.closest('.card');
        const titleEl = parentCard ? parentCard.querySelector('.section-title, h3, h4') : null;
        const title = titleEl ? titleEl.textContent.trim() : 'Analytics Chart';
        openGraphZoom(dataUrl, title);
      } catch (err) {
        console.warn('Could not export canvas to image:', err);
      }
    });
  });
}
