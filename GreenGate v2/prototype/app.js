/* ========================================
   GreenGate v2 — Application Logic
   ======================================== */

(function () {
  "use strict";

  /* ----------------------------------------
     NAVIGATION
     ---------------------------------------- */
  var navButtons = document.querySelectorAll(".sidebar__link");
  var views = document.querySelectorAll(".view");

  function switchView(viewId) {
    views.forEach(function (v) {
      v.classList.remove("view--active");
      v.style.opacity = "0";
    });
    navButtons.forEach(function (b) {
      b.classList.remove("sidebar__link--active");
      b.removeAttribute("aria-current");
    });

    var target = document.getElementById("view-" + viewId);
    var btn = document.querySelector('[data-view="' + viewId + '"]');
    if (target) {
      target.classList.add("view--active");
      /* Re-trigger fade animation */
      target.style.animation = "none";
      /* Force reflow */
      void target.offsetHeight;
      target.style.animation = "";
    }
    if (btn) {
      btn.classList.add("sidebar__link--active");
      btn.setAttribute("aria-current", "page");
    }

    /* Animate KPI gauges when switching to overview */
    if (viewId === "overview") {
      animateGauges();
      renderSparkline();
    }

    /* Close mobile sidebar */
    var sidebar = document.getElementById("sidebar");
    var overlay = document.getElementById("sidebarOverlay");
    if (sidebar) sidebar.classList.remove("open");
    if (overlay) overlay.classList.remove("active");
  }

  navButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var viewId = btn.getAttribute("data-view");
      switchView(viewId);
    });
  });

  /* ----------------------------------------
     MOBILE MENU
     ---------------------------------------- */
  var menuToggle = document.getElementById("menuToggle");
  var sidebar = document.getElementById("sidebar");
  var sidebarOverlay = document.getElementById("sidebarOverlay");

  if (menuToggle) {
    menuToggle.addEventListener("click", function () {
      sidebar.classList.toggle("open");
      sidebarOverlay.classList.toggle("active");
    });
  }

  if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", function () {
      sidebar.classList.remove("open");
      sidebarOverlay.classList.remove("active");
    });
  }

  /* ----------------------------------------
     THEME TOGGLE
     ---------------------------------------- */
  var themeToggle = document.getElementById("themeToggle");

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark";
      setTheme(next);
    });
  }

  /* ----------------------------------------
     ACTIVITY FEED (Overview)
     ---------------------------------------- */
  var activityData = [
    {
      time: "11:34 AM",
      agent: "Progress Tracker",
      dotColor: "amber",
      desc: "Collecting March 2026 energy consumption from Xero integration",
      result: "Processing...",
      resultType: "processing",
      live: true,
    },
    {
      time: "11:32 AM",
      agent: "Progress Tracker",
      dotColor: "amber",
      desc: "Flagged: 3 suppliers haven't responded to Scope 3 data request",
      result: "Auto-reminder sent",
      resultType: "info",
      live: false,
    },
    {
      time: "11:28 AM",
      agent: "Progress Tracker",
      dotColor: "amber",
      desc: "Monthly emissions data for February 2026 verified against baseline",
      result: "4,230 tCO\u2082e (\u21938% vs target)",
      resultType: "success",
      live: false,
    },
    {
      time: "10:15 AM",
      agent: "Strategy Builder",
      dotColor: "blue",
      desc: "Carbon Reduction Plan v3 updated with Q1 progress",
      result: "Governance check: PASSED \u2713",
      resultType: "success",
      live: false,
    },
    {
      time: "09:00 AM",
      agent: "Carbon Auditor",
      dotColor: "green",
      desc: "Scheduled re-scan of supplier invoices \u2014 12 new entries found",
      result: "Scope 3 inventory updated",
      resultType: "success",
      live: false,
    },
    {
      time: "08:45 AM",
      agent: "Carbon Auditor",
      dotColor: "green",
      desc: "DEFRA 2025 emission factors loaded successfully",
      result: "Emission Factor DB refreshed",
      resultType: "info",
      live: false,
    },
    {
      time: "08:30 AM",
      agent: "Progress Tracker",
      dotColor: "amber",
      desc: "Auto-alert sent to 3 non-responsive Scope 3 suppliers",
      result: "Reminder batch #14 dispatched",
      resultType: "info",
      live: false,
    },
    {
      time: "Yesterday",
      agent: "Strategy Builder",
      dotColor: "blue",
      desc: "SBTi near-term target recalculated based on latest baseline data",
      result: "42% reduction by 2030 confirmed",
      resultType: "success",
      live: false,
    },
  ];

  function buildActivityFeed() {
    var feed = document.getElementById("activityFeed");
    if (!feed) return;
    feed.innerHTML = "";

    activityData.forEach(function (entry, index) {
      var el = document.createElement("div");
      el.className = "activity-entry animate-in" + (entry.live ? " activity-entry--live" : "");
      el.style.animationDelay = index * 80 + "ms";

      var dotsHtml = entry.live
        ? '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>'
        : "";

      el.innerHTML =
        '<div class="activity-entry__time">' + entry.time + "</div>" +
        '<div class="activity-entry__body">' +
          '<div class="activity-entry__agent">' +
            '<span class="activity-entry__dot activity-entry__dot--' + entry.dotColor + '"></span>' +
            entry.agent +
          "</div>" +
          '<div class="activity-entry__desc">' + entry.desc + "</div>" +
          '<div class="activity-entry__result activity-entry__result--' + entry.resultType + '">' +
            "\u27F6 " + entry.result + dotsHtml +
          "</div>" +
        "</div>";

      feed.appendChild(el);
    });
  }

  buildActivityFeed();

  /* ----------------------------------------
     KPI GAUGE ANIMATION
     ---------------------------------------- */
  function animateGauges() {
    var fills = document.querySelectorAll(".kpi-card__gauge-fill");
    fills.forEach(function (fill) {
      var value = fill.getAttribute("data-value") || "0";
      fill.style.width = "0%";
      setTimeout(function () {
        fill.style.width = value + "%";
      }, 200);
    });
  }

  /* Initial animation */
  animateGauges();

  /* ----------------------------------------
     SPARKLINE CHART
     ---------------------------------------- */
  function renderSparkline() {
    var canvas = document.getElementById("sparklineActions");
    if (!canvas) return;
    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    /* Destroy existing chart if any */
    if (canvas._chartInstance) {
      canvas._chartInstance.destroy();
    }

    var computedStyle = getComputedStyle(document.documentElement);
    var primaryColor = computedStyle.getPropertyValue("--color-primary").trim() || "#1B6B3A";

    canvas._chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: ["", "", "", "", "", "", "", "", "", "", "", ""],
        datasets: [
          {
            data: [18, 22, 19, 28, 32, 29, 35, 38, 42, 39, 44, 47],
            borderColor: primaryColor,
            borderWidth: 2,
            fill: true,
            backgroundColor: primaryColor + "1A",
            tension: 0.4,
            pointRadius: 0,
            pointHitRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false },
        },
        scales: {
          x: { display: false },
          y: { display: false },
        },
        animation: {
          duration: 800,
          easing: "easeInOutQuart",
        },
      },
    });
  }

  renderSparkline();

  /* ----------------------------------------
     COUNTDOWN TIMER
     ---------------------------------------- */
  function updateCountdown() {
    var deadline = new Date("2026-06-14T23:59:59Z");
    var now = new Date();
    var diff = deadline - now;

    if (diff <= 0) return;

    var days = Math.floor(diff / (1000 * 60 * 60 * 24));
    var hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    var cdDays = document.getElementById("cdDays");
    var cdHours = document.getElementById("cdHours");
    var cdMins = document.getElementById("cdMins");

    if (cdDays) cdDays.textContent = days;
    if (cdHours) cdHours.textContent = hours;
    if (cdMins) cdMins.textContent = mins;
  }

  updateCountdown();
  setInterval(updateCountdown, 60000);

  /* ----------------------------------------
     AGENT CARDS — EXPAND/COLLAPSE
     ---------------------------------------- */
  var agentCards = document.querySelectorAll(".agent-card");

  agentCards.forEach(function (card) {
    var header = card.querySelector(".agent-card__header");
    var toggle = card.querySelector(".agent-card__toggle");

    function toggleCard() {
      /* Don't expand locked cards */
      if (card.classList.contains("agent-card--locked")) return;
      card.classList.toggle("agent-card--expanded");
    }

    if (header) {
      header.addEventListener("click", toggleCard);
    }
    if (toggle) {
      toggle.addEventListener("click", function (e) {
        e.stopPropagation();
        toggleCard();
      });
    }
  });

  /* Auto-expand the current (Progress Tracker) agent */
  var currentAgent = document.querySelector(".agent-card--current");
  if (currentAgent) {
    currentAgent.classList.add("agent-card--expanded");
  }

  /* ----------------------------------------
     GATE JOURNEY — EXPAND/COLLAPSE
     ---------------------------------------- */
  var journeyGates = document.querySelectorAll(".journey-gate");

  journeyGates.forEach(function (gate) {
    var content = gate.querySelector(".journey-gate__content");
    if (content) {
      content.addEventListener("click", function () {
        gate.classList.toggle("journey-gate--expanded");
      });
    }
  });

  /* Auto-expand passed and current gates */
  document.querySelectorAll(".journey-gate--passed, .journey-gate--current").forEach(function (g) {
    g.classList.add("journey-gate--expanded");
  });

  /* ----------------------------------------
     GOVERNANCE LOG FILTERS
     ---------------------------------------- */
  var govFilterBtns = document.querySelectorAll("#govFilters .filter-pill");
  var govLogEntries = document.querySelectorAll("#govLog .gov-log__entry");

  govFilterBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var filter = btn.getAttribute("data-filter");

      govFilterBtns.forEach(function (b) { b.classList.remove("filter-pill--active"); });
      btn.classList.add("filter-pill--active");

      govLogEntries.forEach(function (entry) {
        var type = entry.getAttribute("data-type");
        if (filter === "all" || type === filter) {
          entry.classList.remove("hidden");
        } else {
          entry.classList.add("hidden");
        }
      });
    });
  });

  /* ----------------------------------------
     EVIDENCE TABLE FILTERS
     ---------------------------------------- */
  var evidenceFilterBtns = document.querySelectorAll("#evidenceFilters .filter-pill");
  var evidenceRows = document.querySelectorAll("#evidenceTableBody tr");

  evidenceFilterBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var filter = btn.getAttribute("data-filter");

      evidenceFilterBtns.forEach(function (b) { b.classList.remove("filter-pill--active"); });
      btn.classList.add("filter-pill--active");

      evidenceRows.forEach(function (row) {
        var status = row.getAttribute("data-status");
        if (filter === "all" || status === filter) {
          row.style.display = "";
        } else {
          row.style.display = "none";
        }
      });
    });
  });

  /* ----------------------------------------
     SIMULATED LIVE AGENT ACTIVITY
     Periodically "add" a new entry to the top
     ---------------------------------------- */
  var liveMessages = [
    {
      agent: "Progress Tracker",
      dotColor: "amber",
      desc: "Verifying energy supplier API response for March data",
      result: "Validating...",
      resultType: "processing",
    },
    {
      agent: "Carbon Auditor",
      dotColor: "green",
      desc: "Cross-checking Scope 2 emissions against grid emission factors",
      result: "Data integrity check passed",
      resultType: "success",
    },
    {
      agent: "Progress Tracker",
      dotColor: "amber",
      desc: "Supplier #7 (anonymised) responded with Scope 3 data",
      result: "Processing response...",
      resultType: "processing",
    },
    {
      agent: "Strategy Builder",
      dotColor: "blue",
      desc: "Quick win opportunity detected: office heating schedule optimisation",
      result: "Est. saving: 4.2 tCO\u2082e/yr",
      resultType: "info",
    },
  ];

  var liveIndex = 0;

  function addLiveEntry() {
    var feed = document.getElementById("activityFeed");
    if (!feed) return;

    /* Only if overview is visible */
    var overviewView = document.getElementById("view-overview");
    if (!overviewView || !overviewView.classList.contains("view--active")) return;

    var msg = liveMessages[liveIndex % liveMessages.length];
    liveIndex++;

    var now = new Date();
    var timeStr = now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });

    /* Remove live state from previous entries */
    var prevLive = feed.querySelectorAll(".activity-entry--live");
    prevLive.forEach(function (el) {
      el.classList.remove("activity-entry--live");
      /* Update the result to show completed */
      var resultEl = el.querySelector(".activity-entry__result");
      if (resultEl && resultEl.classList.contains("activity-entry__result--processing")) {
        resultEl.classList.remove("activity-entry__result--processing");
        resultEl.classList.add("activity-entry__result--success");
        resultEl.innerHTML = "\u27F6 Complete \u2713";
      }
    });

    var el = document.createElement("div");
    el.className = "activity-entry activity-entry--live";

    el.innerHTML =
      '<div class="activity-entry__time">' + timeStr + "</div>" +
      '<div class="activity-entry__body">' +
        '<div class="activity-entry__agent">' +
          '<span class="activity-entry__dot activity-entry__dot--' + msg.dotColor + '"></span>' +
          msg.agent +
        "</div>" +
        '<div class="activity-entry__desc">' + msg.desc + "</div>" +
        '<div class="activity-entry__result activity-entry__result--' + msg.resultType + '">' +
          '\u27F6 ' + msg.result + '<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>' +
        "</div>" +
      "</div>";

    feed.insertBefore(el, feed.firstChild);

    /* Remove old entries to keep feed manageable */
    while (feed.children.length > 10) {
      feed.removeChild(feed.lastChild);
    }
  }

  /* Add a new live entry every 12 seconds */
  setInterval(addLiveEntry, 12000);
})();
