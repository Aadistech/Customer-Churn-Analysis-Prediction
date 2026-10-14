/**
 * AadiBI Churn Analytics - Chart.js Visualization Module
 * Adaptive Dark & Light Theme Support
 */

window.AadiCharts = {
  instances: {},

  getThemeColors: function () {
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    return {
      isLight: isLight,
      textColor: isLight ? '#334155' : '#9CA3AF',
      gridColor: isLight ? 'rgba(0, 0, 0, 0.08)' : 'rgba(255, 255, 255, 0.05)',
      tooltipBg: isLight ? 'rgba(255, 255, 255, 0.98)' : 'rgba(17, 24, 39, 0.95)',
      tooltipTitle: isLight ? '#0F172A' : '#FFFFFF',
      tooltipBody: isLight ? '#334155' : '#9CA3AF',
      tooltipBorder: isLight ? 'rgba(203, 213, 225, 0.9)' : 'rgba(99, 102, 241, 0.3)',
      radarGrid: isLight ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.08)',
      radarAngle: isLight ? 'rgba(0, 0, 0, 0.12)' : 'rgba(255, 255, 255, 0.1)',
      radarLabels: isLight ? '#1E293B' : '#9CA3AF',
      doughnutBorder: isLight ? '#FFFFFF' : '#111827'
    };
  },

  getThemeDefaults: function () {
    const colors = this.getThemeColors();
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: colors.textColor,
            font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 },
            padding: 16,
            usePointStyle: true,
            pointStyleWidth: 10
          }
        },
        tooltip: {
          backgroundColor: colors.tooltipBg,
          titleColor: colors.tooltipTitle,
          bodyColor: colors.tooltipBody,
          borderColor: colors.tooltipBorder,
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
          grid: { color: colors.gridColor, drawBorder: false },
          ticks: { color: colors.textColor, font: { family: 'Plus Jakarta Sans', size: 11 } }
        },
        y: {
          grid: { color: colors.gridColor, drawBorder: false },
          ticks: { color: colors.textColor, font: { family: 'Plus Jakarta Sans', size: 11 } }
        }
      }
    };
  },

  initDoughnut: function (canvasId, stayCount, churnCount) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }

    const colors = this.getThemeColors();
    const chart = new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: ['Predicted Stay', 'Predicted Churn'],
        datasets: [{
          data: [stayCount, churnCount],
          backgroundColor: ['#10B981', '#EF4444'],
          borderColor: colors.doughnutBorder,
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
              color: colors.textColor,
              font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 },
              padding: 16,
              usePointStyle: true
            }
          },
          tooltip: this.getThemeDefaults().plugins.tooltip
        }
      }
    });

    this.instances[canvasId] = chart;
    return chart;
  },

  initBarChart: function (canvasId, labels, dataPoints, labelText, barColor = '#3B82F6') {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }

    const defaults = this.getThemeDefaults();
    const chart = new Chart(canvas, {
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
        ...defaults,
        plugins: {
          ...defaults.plugins,
          legend: { display: false }
        },
        scales: {
          ...defaults.scales,
          y: {
            ...defaults.scales.y,
            ticks: {
              ...defaults.scales.y.ticks,
              callback: (value) => value + '%'
            }
          }
        }
      }
    });

    this.instances[canvasId] = chart;
    return chart;
  },

  initFeatureImportanceChart: function (canvasId, featureImportanceList) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    if (this.instances[canvasId]) {
      this.instances[canvasId].destroy();
    }

    const labels = featureImportanceList.map(item => item.feature);
    const scores = featureImportanceList.map(item => item.importance);
    const defaults = this.getThemeDefaults();

    const chart = new Chart(canvas, {
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
        ...defaults,
        plugins: {
          ...defaults.plugins,
          legend: { display: false }
        },
        scales: {
          ...defaults.scales,
          x: {
            ...defaults.scales.x,
            ticks: {
              ...defaults.scales.x.ticks,
              callback: (val) => val + '%'
            }
          }
        }
      }
    });

    this.instances[canvasId] = chart;
    return chart;
  },

  initCustomerRadarChart: function (canvasId, metrics) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

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

    const colors = this.getThemeColors();
    const chart = new Chart(canvas, {
      type: 'radar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Account Behavioral Intensity',
          data: dataPoints,
          backgroundColor: colors.isLight ? 'rgba(79, 70, 229, 0.15)' : 'rgba(99, 102, 241, 0.25)',
          borderColor: colors.isLight ? '#4F46E5' : '#818CF8',
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
          tooltip: this.getThemeDefaults().plugins.tooltip
        },
        scales: {
          r: {
            angleLines: { color: colors.radarAngle },
            grid: { color: colors.radarGrid },
            pointLabels: {
              color: colors.radarLabels,
              font: { family: 'Plus Jakarta Sans', size: 11, weight: 600 }
            },
            ticks: { display: false, max: 100 }
          }
        }
      }
    });

    window.customerRadarChartInstance = chart;
    this.instances[canvasId] = chart;
    return chart;
  },

  updateTheme: function () {
    const colors = this.getThemeColors();
    const defaults = this.getThemeDefaults();

    Object.keys(this.instances).forEach(canvasId => {
      const chart = this.instances[canvasId];
      if (!chart) return;

      if (chart.config.type === 'doughnut') {
        if (chart.data.datasets[0]) {
          chart.data.datasets[0].borderColor = colors.doughnutBorder;
        }
        if (chart.options.plugins && chart.options.plugins.legend) {
          chart.options.plugins.legend.labels.color = colors.textColor;
        }
        if (chart.options.plugins && chart.options.plugins.tooltip) {
          Object.assign(chart.options.plugins.tooltip, defaults.plugins.tooltip);
        }
      } else if (chart.config.type === 'radar') {
        if (chart.options.scales && chart.options.scales.r) {
          chart.options.scales.r.angleLines.color = colors.radarAngle;
          chart.options.scales.r.grid.color = colors.radarGrid;
          chart.options.scales.r.pointLabels.color = colors.radarLabels;
        }
        if (chart.data.datasets[0]) {
          chart.data.datasets[0].backgroundColor = colors.isLight ? 'rgba(79, 70, 229, 0.15)' : 'rgba(99, 102, 241, 0.25)';
          chart.data.datasets[0].borderColor = colors.isLight ? '#4F46E5' : '#818CF8';
        }
        if (chart.options.plugins && chart.options.plugins.tooltip) {
          Object.assign(chart.options.plugins.tooltip, defaults.plugins.tooltip);
        }
      } else if (chart.options.scales) {
        if (chart.options.scales.x) {
          chart.options.scales.x.grid.color = colors.gridColor;
          if (chart.options.scales.x.ticks) chart.options.scales.x.ticks.color = colors.textColor;
        }
        if (chart.options.scales.y) {
          chart.options.scales.y.grid.color = colors.gridColor;
          if (chart.options.scales.y.ticks) chart.options.scales.y.ticks.color = colors.textColor;
        }
        if (chart.options.plugins && chart.options.plugins.tooltip) {
          Object.assign(chart.options.plugins.tooltip, defaults.plugins.tooltip);
        }
      }

      chart.update();
    });
  }
};
