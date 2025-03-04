// Define the backend API URL
const backendURL = "http://localhost:8000";

$(document).ready(function () {
  // 1) Build a 7×18 skeleton using data attributes for period and group
  buildSkeleton();

  // 2) Fetch filter options from the backend and populate the dropdowns
  fetchFilterOptions();

  // 3) Fetch the element data from the backend and update skeleton cells
  fetchAndRenderTable();

  // 4) Search / Filter functionality: by name/symbol, group, and period
  $('#search-btn').click(function () {
    let query = $('#search-input').val().toLowerCase().trim();
    let groupFilter = $('#group-filter').val();
    let periodFilter = $('#period-filter').val();

    $('.element').each(function () {
      let symbol = $(this).data('symbol') || "";
      let name = $(this).data('name') || "";
      let cellGroup = $(this).attr('data-group');
      let cellPeriod = $(this).attr('data-period');

      let matchesQuery = !query || symbol.toLowerCase() === query || name.toLowerCase().includes(query);
      let matchesGroup = !groupFilter || cellGroup === groupFilter;
      let matchesPeriod = !periodFilter || cellPeriod === periodFilter;

      if (matchesQuery && matchesGroup && matchesPeriod) {
        $(this).css('border', '2px solid red');
        this.scrollIntoView({ behavior: 'smooth', block: 'center' });
      } else {
        $(this).css('border', '1px solid #00796b');
      }
    });
  });

  // 5) Clear Filters functionality
  $('#clear-btn').click(function () {
    $('#search-input').val('');
    $('#group-filter').val('');
    $('#period-filter').val('');
    $('.element').css('border', '1px solid #00796b');
    $('#table-container')[0].scrollIntoView({ behavior: 'smooth' });
  });

  // 6) Tooltip handling with a 1-second delay
  $(document).on('mouseenter', '.element', function () {
    let element = $(this).data('element');
    if (!element) return; // Still skeleton or missing data
    // Start a timeout for 1 second (1000 ms)
    let that = $(this);
    let timeoutId = setTimeout(function () {
      let tooltip = that.find('.element-tooltip');
      tooltip.html(`
        <h3>${element.name}</h3><br>
        <br>
        Atomic Number: ${element.atomic_number}<br>
        Atomic Mass: ${element.atomic_mass}<br>
        Density: ${element.density}<br>
        Melting Point: ${element.melting_point}<br>
        Boiling Point: ${element.boiling_point}
      `);
      tooltip.fadeIn();
    }, 500);
    // Save the timeout ID to this element's data
    $(this).data('tooltipTimeout', timeoutId);
  });

  $(document).on('mouseleave', '.element', function () {
    // Clear the tooltip timeout if it exists
    let timeoutId = $(this).data('tooltipTimeout');
    if (timeoutId) {
      clearTimeout(timeoutId);
      $(this).removeData('tooltipTimeout');
    }
    $(this).find('.element-tooltip').fadeOut();
  });
});

// Builds a 7 (periods) × 18 (groups) skeleton using data attributes
function buildSkeleton() {
  $('#table-container').empty();
  for (let period = 1; period <= 7; period++) {
    for (let group = 1; group <= 18; group++) {
      let cell = $('<div class="element skeleton"></div>');
      cell.attr('data-period', period);
      cell.attr('data-group', group);
      cell.html('<strong>--</strong><br><small>--</small><div class="element-tooltip"></div>');
      $('#table-container').append(cell);
    }
  }
}

// Fetch filter options from backend; expects endpoint "/filter_options" returning {"groups": [...], "periods": [...]}
function fetchFilterOptions() {
  $.getJSON(`${backendURL}/filter_options`, function (data) {
    if (data.groups && data.periods) {
      let groupSelect = $('#group-filter');
      let periodSelect = $('#period-filter');
      $.each(data.groups, function (_, grp) {
        groupSelect.append(`<option value="${grp}">Group ${grp}</option>`);
      });
      $.each(data.periods, function (_, prd) {
        periodSelect.append(`<option value="${prd}">Period ${prd}</option>`);
      });
    }
  }).fail(function () {
    // Fallback defaults if endpoint is unavailable
    let groupSelect = $('#group-filter');
    let periodSelect = $('#period-filter');
    for (let i = 1; i <= 18; i++) {
      groupSelect.append(`<option value="${i}">Group ${i}</option>`);
    }
    for (let i = 1; i <= 7; i++) {
      periodSelect.append(`<option value="${i}">Period ${i}</option>`);
    }
  });
}

// Fetch element data from backend and update matching skeleton cells.
// Each element document must include "group" and "period" fields.
function fetchAndRenderTable() {
  $.getJSON(`${backendURL}/elements`, function (elements) {
    if (!elements.length) {
      $('#error-message').text('No element data available.');
      return;
    }
    $.each(elements, function (_, el) {
      if (!el.group || !el.period) return;
      let cell = $(`.element.skeleton[data-period="${el.period}"][data-group="${el.group}"]`).first();
      if (cell.length) {
        cell.removeClass('skeleton');
        cell.html(`
          <strong>${el.symbol}</strong><br>
          <small>${el.atomic_number}</small>
          <div class="element-tooltip"></div>
        `);
        cell.data('symbol', el.symbol);
        cell.data('name', el.name);
        cell.data('element', el);
      }
    });
  }).fail(function () {
    $('#error-message').text('Could not connect to server.');
  });
}
