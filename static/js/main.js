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
      <div style="background: rgba(255,255,255,0.04); padding: 0.5rem 0.85rem; border-radius: 6px; border: 1px solid var(--border-color); font-size: 0.85rem; color: #E5E7EB;">
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
