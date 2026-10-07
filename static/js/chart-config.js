/**
 * AadiBI Churn Analytics - Chart.js Visualization Module
 */

window.AadiCharts = {
  // Common Dark Theme Options for Chart.js
  themeDefaults: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#9CA3AF',
          font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 },
          padding: 16,
          usePointStyle: true,
          pointStyleWidth: 10
        }
      },
      tooltip: {
        backgroundColor: 'rgba(17, 24, 39, 0.95)',
        titleColor: '#FFFFFF',
        bodyColor: '#9CA3AF',
        borderColor: 'rgba(99, 102, 241, 0.3)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        titleFont: { family: 'Plus Jakarta Sans', weight: '700' },
        bodyFont: { family: 'Plus Jakarta Sans' }
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
        ticks: { color: '#9CA3AF', font: { family: 'Plus Jakarta Sans', size: 11 } }
      },
      y: {
        grid: { color: 'rgba(255, 255, 255, 0.05)', drawBorder: false },
        ticks: { color: '#9CA3AF', font: { family: 'Plus Jakarta Sans', size: 11 } }
      }
    }
  },

  initDoughnut: function (canvasId, stayCount, churnCount) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    return new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['Predicted Stay', 'Predicted Churn'],
        datasets: [{
          data: [stayCount, churnCount],
          backgroundColor: ['#10B981', '#EF4444'],
          borderColor: '#111827',
          borderWidth: 3,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '75%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: '#9CA3AF',
              font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 },
              padding: 16,
              usePointStyle: true
            }
          },
          tooltip: this.themeDefaults.plugins.tooltip
        }
      }
    });
  },

  initBarChart: function (canvasId, labels, dataPoints, labelText, barColor = '#3B82F6') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    return new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: labelText,
          data: dataPoints,
          backgroundColor: barColor,
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        ...this.themeDefaults,
        plugins: {
          ...this.themeDefaults.plugins,
          legend: { display: false }
        },
        scales: {
          ...this.themeDefaults.scales,
          y: {
            ...this.themeDefaults.scales.y,
            ticks: {
              ...this.themeDefaults.scales.y.ticks,
              callback: (value) => value + '%'
            }
          }
        }
      }
    });
  },

  initFeatureImportanceChart: function (canvasId, featureImportanceList) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const labels = featureImportanceList.map(item => item.feature);
    const scores = featureImportanceList.map(item => item.importance);

    return new Chart(canvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Predictive Importance (%)',
          data: scores,
          backgroundColor: [
            '#EF4444', '#F59E0B', '#3B82F6', '#8B5CF6', '#10B981', '#06B6D4', '#64748B'
          ],
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        ...this.themeDefaults,
        plugins: {
          ...this.themeDefaults.plugins,
          legend: { display: false }
        },
        scales: {
          ...this.themeDefaults.scales,
          x: {
            ...this.themeDefaults.scales.x,
            ticks: {
              ...this.themeDefaults.scales.x.ticks,
              callback: (val) => val + '%'
            }
          }
        }
      }
    });
  },

  initCustomerRadarChart: function (canvasId, metrics) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Normalize metrics on 0-100 scale for visual comparison
    const labels = ['Day Usage', 'Eve Usage', 'Night Usage', 'Intl Usage', 'Svc Calls'];
    const dataPoints = [
      Math.min(100, Math.round((metrics.dayMinutes / 300) * 100)),
      Math.min(100, Math.round((metrics.eveMinutes / 300) * 100)),
      Math.min(100, Math.round((metrics.nightMinutes / 300) * 100)),
      Math.min(100, Math.round((metrics.intlMinutes / 20) * 100)),
      Math.min(100, Math.round((metrics.serviceCalls / 5) * 100))
    ];

    if (window.customerRadarChartInstance) {
      window.customerRadarChartInstance.destroy();
    }

    window.customerRadarChartInstance = new Chart(canvas, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Account Behavioral Intensity',
          data: dataPoints,
          backgroundColor: 'rgba(99, 102, 241, 0.25)',
          borderColor: '#818CF8',
          borderWidth: 2,
          pointBackgroundColor: '#4F46E5',
          pointBorderColor: '#FFFFFF',
          pointHoverBackgroundColor: '#FFFFFF',
          pointHoverBorderColor: '#4F46E5'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: this.themeDefaults.plugins.tooltip
        },
        scales: {
          r: {
            angleLines: { color: 'rgba(255, 255, 255, 0.1)' },
            grid: { color: 'rgba(255, 255, 255, 0.08)' },
            pointLabels: {
              color: '#9CA3AF',
              font: { family: 'Plus Jakarta Sans', size: 11, weight: 600 }
            },
            ticks: { display: false, max: 100 }
          }
        }
      }
    });
  }
};
