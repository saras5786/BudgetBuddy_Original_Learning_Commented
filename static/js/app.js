/* ================================================================
   BUDGET BUDDY - FULL CLIENT-SIDE APPLICATION ENGINE (GitHub Pages)
   ================================================================ */

const CATEGORIES = [
  "Groceries",
  "Rent",
  "Transportation",
  "Gym",
  "Utilities",
  "Electricity Bill",
  "Internet & Mobile Bill",
  "Healthcare",
  "Insurance",
  "Investments",
  "Savings",
  "EMI/Loans",
  "Taxes",
  "Dining & Entertainment",
  "Shopping & Wants",
  "Education",
  "Other"
];

const CURRENCIES = [
  "₹ (INR)",
  "$ (USD)",
  "€ (EUR)",
  "£ (GBP)",
  "¥ (JPY)",
  "Rs (PKR/NPR)"
];

// Active Chart.js instances
const activeCharts = {};

// Helper: Format Currency
function fmtCurrency(num, curr = '₹') {
  const val = Number(num || 0);
  return `${curr}${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Helper: Flash / Toast message
function showFlash(msg, type = 'success') {
  const stack = document.getElementById('flashStack') || document.querySelector('.main');
  const el = document.createElement('div');
  el.className = 'flash ' + type;
  el.textContent = msg;
  stack.prepend(el);
  setTimeout(() => el.remove(), 2800);
}

// Helper: Date string YYYY-MM-DD
function getTodayStr() {
  const d = new Date();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${month}-${day}`;
}

// ----------------------------------------------------------------
// DATA STORE & LOCAL STORAGE
// ----------------------------------------------------------------
const Storage = {
  getSession() {
    try {
      return JSON.parse(localStorage.getItem('budgetbuddy_session'));
    } catch (e) {
      return null;
    }
  },
  setSession(user) {
    localStorage.setItem('budgetbuddy_session', JSON.stringify(user));
  },
  clearSession() {
    localStorage.removeItem('budgetbuddy_session');
  },
  getUsers() {
    try {
      return JSON.parse(localStorage.getItem('budgetbuddy_users')) || [];
    } catch (e) {
      return [];
    }
  },
  saveUser(user) {
    const users = this.getUsers();
    const idx = users.findIndex(u => u.email.toLowerCase() === user.email.toLowerCase());
    if (idx >= 0) users[idx] = user;
    else users.push(user);
    localStorage.setItem('budgetbuddy_users', JSON.stringify(users));
  },
  getExpenses() {
    try {
      const ex = localStorage.getItem('budgetbuddy_expenses');
      if (ex) return JSON.parse(ex);
    } catch (e) {}
    // Seed initial demo expenses
    const seeded = this.seedInitialExpenses();
    this.setExpenses(seeded);
    return seeded;
  },
  setExpenses(expenses) {
    localStorage.setItem('budgetbuddy_expenses', JSON.stringify(expenses));
  },
  getBudgets() {
    try {
      const b = localStorage.getItem('budgetbuddy_budgets');
      if (b) return JSON.parse(b);
    } catch (e) {}
    const defaultBudgets = {
      "Rent": 15000,
      "Groceries": 12000,
      "Dining & Entertainment": 8000,
      "Transportation": 5000,
      "Utilities": 4000,
      "Shopping & Wants": 6000,
      "Healthcare": 3000
    };
    localStorage.setItem('budgetbuddy_budgets', JSON.stringify(defaultBudgets));
    return defaultBudgets;
  },
  setBudgets(budgets) {
    localStorage.setItem('budgetbuddy_budgets', JSON.stringify(budgets));
  },
  seedInitialExpenses() {
    const today = new Date();
    const curYear = today.getFullYear();
    const curMonth = today.getMonth(); // 0-indexed

    const pad = n => String(n).padStart(2, '0');
    const makeDate = (year, month, day) => `${year}-${pad(month + 1)}-${pad(day)}`;

    return [
      { id: 1, amount: 15000, category: 'Rent', description: 'Monthly Apartment Rent', expense_date: makeDate(curYear, curMonth, 1) },
      { id: 2, amount: 3450, category: 'Groceries', description: 'Supermarket weekly basket', expense_date: makeDate(curYear, curMonth, 3) },
      { id: 3, amount: 1850, category: 'Electricity Bill', description: 'Power grid monthly bill', expense_date: makeDate(curYear, curMonth, 5) },
      { id: 4, amount: 999, category: 'Internet & Mobile Bill', description: 'High-speed fiber bill', expense_date: makeDate(curYear, curMonth, 6) },
      { id: 5, amount: 1200, category: 'Transportation', description: 'Metro pass recharge', expense_date: makeDate(curYear, curMonth, 8) },
      { id: 6, amount: 2400, category: 'Dining & Entertainment', description: 'Weekend dinner with family', expense_date: makeDate(curYear, curMonth, 10) },
      { id: 7, amount: 4100, category: 'Groceries', description: 'Organic farm produce & pantry', expense_date: makeDate(curYear, curMonth, 12) },
      { id: 8, amount: 1500, category: 'Healthcare', description: 'Pharmacy & vitamins', expense_date: makeDate(curYear, curMonth, 14) },
      { id: 9, amount: 3200, category: 'Shopping & Wants', description: 'Running shoes & apparel', expense_date: makeDate(curYear, curMonth, 16) },
      { id: 10, amount: 800, category: 'Transportation', description: 'Cab rides', expense_date: makeDate(curYear, curMonth, 18) },
      { id: 11, amount: 5000, category: 'Investments', description: 'Mutual Fund SIP investment', expense_date: makeDate(curYear, curMonth, 20) },
      { id: 12, amount: 1650, category: 'Dining & Entertainment', description: 'Cafe & coffee with friends', expense_date: makeDate(curYear, curMonth, 22) },
      // Prior month 1
      { id: 13, amount: 15000, category: 'Rent', description: 'Monthly Apartment Rent', expense_date: makeDate(curYear, curMonth - 1, 1) },
      { id: 14, amount: 7800, category: 'Groceries', description: 'Monthly grocery bulk buy', expense_date: makeDate(curYear, curMonth - 1, 4) },
      { id: 15, amount: 1750, category: 'Electricity Bill', description: 'Electricity usage', expense_date: makeDate(curYear, curMonth - 1, 6) },
      { id: 16, amount: 4200, category: 'Dining & Entertainment', description: 'Team celebrations', expense_date: makeDate(curYear, curMonth - 1, 11) },
      { id: 17, amount: 2100, category: 'Transportation', description: 'Fuel & toll charges', expense_date: makeDate(curYear, curMonth - 1, 15) },
      { id: 18, amount: 5000, category: 'Investments', description: 'Monthly SIP', expense_date: makeDate(curYear, curMonth - 1, 20) },
      // Prior month 2
      { id: 19, amount: 15000, category: 'Rent', description: 'Monthly Apartment Rent', expense_date: makeDate(curYear, curMonth - 2, 1) },
      { id: 20, amount: 6900, category: 'Groceries', description: 'Household provisions', expense_date: makeDate(curYear, curMonth - 2, 5) },
      { id: 21, amount: 3100, category: 'Shopping & Wants', description: 'Electronics accessory', expense_date: makeDate(curYear, curMonth - 2, 12) },
      { id: 22, amount: 1900, category: 'Utilities', description: 'Water & maintenance', expense_date: makeDate(curYear, curMonth - 2, 18) },
      { id: 23, amount: 5000, category: 'Investments', description: 'SIP portfolio', expense_date: makeDate(curYear, curMonth - 2, 20) }
    ];
  }
};

// ----------------------------------------------------------------
// APPLICATION CONTROLLER
// ----------------------------------------------------------------
const App = {
  user: null,

  init() {
    this.populateDropdowns();
    this.bindEvents();

    const session = Storage.getSession();
    if (session) {
      this.user = session;
      const initialHash = window.location.hash.slice(1) || 'dashboard';
      this.navigate(initialHash === 'login' ? 'dashboard' : initialHash);
    } else {
      this.navigate('login');
    }
  },

  populateDropdowns() {
    // Categories for single entry & filter & budgets
    const catOptions = CATEGORIES.map(c => `<option value="${c}">${c}</option>`).join('');
    const singleCat = document.getElementById('category');
    if (singleCat) singleCat.innerHTML = catOptions;

    const budgetCat = document.getElementById('budget-category');
    if (budgetCat) budgetCat.innerHTML = catOptions;

    const filterCat = document.getElementById('filter-category');
    if (filterCat) filterCat.innerHTML = `<option value="All">All</option>` + catOptions;

    // Currencies for profile
    const currSelect = document.getElementById('profile-currency');
    if (currSelect) {
      currSelect.innerHTML = CURRENCIES.map(c => `<option value="${c.split(' ')[0]}">${c}</option>`).join('');
    }

    const expDate = document.getElementById('expense-date');
    if (expDate) expDate.value = getTodayStr();
  },

  updateCurrencyLabels() {
    const curr = (this.user && this.user.currency) || '₹';
    document.querySelectorAll('.currency').forEach(el => el.textContent = curr);
  },

  navigate(pageId) {
    if (!this.user && pageId !== 'login') {
      pageId = 'login';
    }

    // Set body attribute
    const pageTitle = pageId.charAt(0).toUpperCase() + pageId.slice(1).replace('-', ' ');
    document.body.setAttribute('data-page', pageId === 'login' ? 'Login' : pageTitle);
    document.title = pageId === 'login' ? 'Budget Buddy · Login' : `Budget Buddy · ${pageTitle}`;

    // Toggle sidebar
    const sidebar = document.getElementById('appSidebar');
    if (sidebar) {
      sidebar.style.display = (pageId === 'login') ? 'none' : '';
    }

    // Update nav active state
    document.querySelectorAll('.nav-item').forEach(link => {
      link.classList.toggle('active', link.dataset.nav === pageId);
    });

    // Toggle views
    document.querySelectorAll('.page-view').forEach(view => {
      view.style.display = 'none';
    });
    const targetView = document.getElementById(`view-${pageId}`);
    if (targetView) {
      targetView.style.display = 'block';
    }

    // Update greeting
    if (this.user) {
      const greeting = document.getElementById('userGreeting');
      if (greeting) greeting.textContent = `Welcome, ${this.user.name || 'User'}`;
      this.updateCurrencyLabels();
    }

    // Load page data
    switch (pageId) {
      case 'dashboard':
        this.renderDashboard();
        break;
      case 'budget-planner':
        this.renderBudgetPlanner();
        break;
      case 'add-expense':
        this.setupAddExpense();
        break;
      case 'expense-history':
        this.renderExpenseHistory();
        break;
      case 'dataset-analyzer':
        // Ready for user actions
        break;
      case 'profile':
        this.renderProfile();
        break;
    }
  },

  bindEvents() {
    // Window hash changes
    window.addEventListener('hashchange', () => {
      const hash = window.location.hash.slice(1);
      if (hash === 'logout') {
        this.logout();
      } else if (hash) {
        this.navigate(hash);
      }
    });

    // Nav clicks
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const nav = item.dataset.nav;
        window.location.hash = nav;
        this.navigate(nav);
      });
    });

    // Logout button
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
      logoutBtn.onclick = (e) => {
        e.preventDefault();
        this.logout();
      };
    }

    // Tab buttons (.auth-tab and .tab)
    document.querySelectorAll('.auth-tab').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('.auth-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.auth-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const target = document.getElementById(btn.dataset.tab);
        if (target) target.classList.add('active');
      };
    });

    document.querySelectorAll('.tab').forEach(btn => {
      btn.onclick = () => {
        const parent = btn.closest('.page-view') || document;
        parent.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
        parent.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const target = document.getElementById(btn.dataset.target);
        if (target) target.classList.add('active');
      };
    });

    // Auth Forms
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
      loginForm.onsubmit = (e) => {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value.trim();
        const password = document.getElementById('loginPassword').value;
        const users = Storage.getUsers();
        let user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
        if (!user) {
          // If demo or new email, allow login directly
          user = {
            id: Date.now(),
            email: email,
            name: email.split('@')[0],
            income: 60000,
            currency: '₹'
          };
          Storage.saveUser(user);
        }
        this.user = user;
        Storage.setSession(user);
        showFlash('Signed in successfully!', 'success');
        window.location.hash = 'dashboard';
        this.navigate('dashboard');
      };
    }

    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
      signupForm.onsubmit = (e) => {
        e.preventDefault();
        const email = document.getElementById('signupEmail').value.trim();
        const password = document.getElementById('signupPassword').value;
        const confirm = document.getElementById('signupConfirm').value;
        if (password !== confirm) {
          showFlash('Passwords do not match.', 'error');
          return;
        }
        const user = {
          id: Date.now(),
          email: email,
          name: email.split('@')[0],
          income: 50000,
          currency: '₹'
        };
        Storage.saveUser(user);
        showFlash('Account created! Please sign in.', 'success');
        // Switch to signin tab
        document.querySelector('.auth-tab[data-tab="login"]').click();
        document.getElementById('loginEmail').value = email;
      };
    }

    const demoForm = document.getElementById('demoForm');
    if (demoForm) {
      demoForm.onsubmit = (e) => {
        e.preventDefault();
        const demoUser = {
          id: 1,
          email: 'demo@budgetbuddy.app',
          name: 'Demo User',
          income: 60000,
          currency: '₹'
        };
        this.user = demoUser;
        Storage.saveUser(demoUser);
        Storage.setSession(demoUser);
        showFlash('Welcome to Budget Buddy Demo Account!', 'success');
        window.location.hash = 'dashboard';
        this.navigate('dashboard');
      };
    }

    // Add Expense Single
    const expForm = document.getElementById('expense-form');
    if (expForm) {
      expForm.onsubmit = (e) => {
        e.preventDefault();
        const amount = Number(document.getElementById('amount').value);
        const category = document.getElementById('category').value;
        const expense_date = document.getElementById('expense-date').value || getTodayStr();
        const description = document.getElementById('description').value;

        if (amount <= 0) {
          showFlash('Please enter a valid expense amount.', 'error');
          return;
        }

        const expenses = Storage.getExpenses();
        const newId = expenses.length ? Math.max(...expenses.map(x => x.id || 0)) + 1 : 1;
        expenses.unshift({ id: newId, amount, category, description, expense_date });
        Storage.setExpenses(expenses);

        showFlash('Expense recorded successfully.', 'success');
        document.getElementById('amount').value = '';
        document.getElementById('description').value = '';
        document.getElementById('expense-date').value = getTodayStr();
      };
    }

    // Add Expense Batch
    const addRowBtn = document.getElementById('add-row');
    if (addRowBtn) {
      addRowBtn.onclick = () => this.addBatchRow();
    }

    const saveBatchBtn = document.getElementById('save-batch');
    if (saveBatchBtn) {
      saveBatchBtn.onclick = () => {
        const rows = document.querySelectorAll('#batch-body tr');
        const records = [];
        rows.forEach(tr => {
          const amt = Number(tr.querySelector('.r-amount')?.value || 0);
          const cat = tr.querySelector('.r-cat')?.value || 'Groceries';
          const desc = tr.querySelector('.r-desc')?.value || '';
          const dt = tr.querySelector('.r-date')?.value || getTodayStr();
          if (amt > 0) records.push({ amount: amt, category: cat, description: desc, expense_date: dt });
        });

        if (!records.length) {
          showFlash('Please enter at least one valid expense amount.', 'error');
          return;
        }

        const expenses = Storage.getExpenses();
        let nextId = expenses.length ? Math.max(...expenses.map(x => x.id || 0)) + 1 : 1;
        records.forEach(r => {
          expenses.unshift({ id: nextId++, ...r });
        });
        Storage.setExpenses(expenses);
        showFlash(`Saved ${records.length} records successfully.`, 'success');
        this.setupAddExpense();
      };
    }

    // Budget Form
    const budgetForm = document.getElementById('budget-form');
    if (budgetForm) {
      budgetForm.onsubmit = (e) => {
        e.preventDefault();
        const category = document.getElementById('budget-category').value;
        const limit = Number(document.getElementById('budget-limit').value);
        const budgets = Storage.getBudgets();
        budgets[category] = limit;
        Storage.setBudgets(budgets);
        showFlash(`Budget limit for ${category} updated.`, 'success');
        this.renderBudgetPlanner();
      };
    }

    // History Filters
    ['filter-category', 'search-query', 'min-amount', 'sort-order'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.oninput = () => this.filterExpenses();
    });

    // Profile Form
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
      profileForm.onsubmit = (e) => {
        e.preventDefault();
        this.user.name = document.getElementById('profile-name').value.trim() || 'User';
        this.user.income = Number(document.getElementById('profile-income').value) || 0;
        this.user.currency = document.getElementById('profile-currency').value || '₹';
        Storage.setSession(this.user);
        Storage.saveUser(this.user);
        this.updateCurrencyLabels();
        document.getElementById('userGreeting').textContent = `Welcome, ${this.user.name}`;
        showFlash('Profile updated successfully.', 'success');
      };
    }

    // Clear Expenses
    const clearBtn = document.getElementById('clear-expenses');
    if (clearBtn) {
      clearBtn.onclick = () => {
        if (confirm('Are you sure you want to clear all recorded expenses?')) {
          Storage.setExpenses([]);
          showFlash('All expenses cleared.', 'success');
          this.renderProfile();
        }
      };
    }

    // CSV Exports
    const csvExport = document.getElementById('csv-export');
    if (csvExport) {
      csvExport.onclick = (e) => {
        e.preventDefault();
        this.exportCSV(false);
      };
    }

    const csvExportAll = document.getElementById('csv-export-all');
    if (csvExportAll) {
      csvExportAll.onclick = (e) => {
        e.preventDefault();
        this.exportCSV(true);
      };
    }

    // Dataset Analyzer
    const loadSampleBtn = document.getElementById('load-sample');
    if (loadSampleBtn) {
      loadSampleBtn.onclick = () => this.loadSampleDataset();
    }

    const analyzeFileBtn = document.getElementById('analyze-file');
    if (analyzeFileBtn) {
      analyzeFileBtn.onclick = () => this.analyzeUploadedFile();
    }
  },

  logout() {
    Storage.clearSession();
    this.user = null;
    window.location.hash = 'login';
    showFlash('Logged out successfully.', 'success');
    this.navigate('login');
  },

  // ----------------------------------------------------------------
  // DASHBOARD
  // ----------------------------------------------------------------
  renderDashboard() {
    const expenses = Storage.getExpenses();
    const curr = (this.user && this.user.currency) || '₹';
    const income = Number(this.user?.income || 60000);

    const total = expenses.reduce((s, x) => s + Number(x.amount || 0), 0);
    const uniqueDays = new Set(expenses.map(x => x.expense_date)).size;
    const avgDaily = total / Math.max(1, uniqueDays);
    const remaining = income - total;
    const savingsRate = income > 0 ? Math.max(0, (remaining / income) * 100) : 0;
    const expenseRatio = income > 0 ? (total / income) * 100 : 0;

    let healthStatus = 'Healthy (High Savings)';
    if (total === 0) healthStatus = 'No Expenses Recorded';
    else if (income <= 0) healthStatus = 'Income Not Configured';
    else if (expenseRatio <= 50) healthStatus = 'Healthy (High Savings)';
    else if (expenseRatio <= 75) healthStatus = 'Balanced Spending';
    else if (expenseRatio <= 95) healthStatus = 'High Utilization';
    else healthStatus = 'Deficit (Expenses Exceed Income)';

    // Category breakdown
    const catMap = {};
    expenses.forEach(x => {
      catMap[x.category] = (catMap[x.category] || 0) + Number(x.amount || 0);
    });
    const sortedCats = Object.entries(catMap).sort((a, b) => b[1] - a[1]);
    const topCat = sortedCats.length ? `${sortedCats[0][0]} (${fmtCurrency(sortedCats[0][1], curr)})` : 'None';

    // Render KPIs
    const kpiData = [
      ['Monthly Income', fmtCurrency(income, curr)],
      ['Total Expenses', fmtCurrency(total, curr)],
      ['Net Balance', fmtCurrency(remaining, curr)],
      ['Savings Rate', `${savingsRate.toFixed(1)}%`],
      ['Top Category', topCat],
      ['Daily Average Spend', fmtCurrency(avgDaily, curr)],
      ['Expense to Income', `${expenseRatio.toFixed(1)}%`],
      ['Financial Health', healthStatus]
    ];

    const kpisEl = document.getElementById('kpis');
    if (kpisEl) {
      kpisEl.innerHTML = kpiData.map(k => `
        <div class="kpi">
          <small>${k[0]}</small>
          <strong>${k[1]}</strong>
        </div>
      `).join('');
    }

    // Render Charts
    this.renderDashboardCharts(sortedCats, expenses, income);
  },

  destroyChart(id) {
    if (activeCharts[id]) {
      activeCharts[id].destroy();
      delete activeCharts[id];
    }
  },

  renderDashboardCharts(categoryList, expenses, income) {
    const labels = categoryList.map(c => c[0]);
    const data = categoryList.map(c => c[1]);

    // 1. Donut Chart
    const donutEl = document.getElementById('donutChart');
    if (donutEl) {
      this.destroyChart('donut');
      activeCharts['donut'] = new Chart(donutEl, {
        type: 'doughnut',
        data: {
          labels: labels.length ? labels : ['No Expenses'],
          datasets: [{
            data: data.length ? data : [1],
            backgroundColor: [
              '#2563eb', '#38bdf8', '#34d399', '#f59e0b', '#ec4899',
              '#8b5cf6', '#64748b', '#10b981', '#f97316', '#a855f7'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } }
        }
      });
    }

    // 2. Bar Chart (Spending by Category)
    const barEl = document.getElementById('barChart');
    if (barEl) {
      this.destroyChart('bar');
      activeCharts['bar'] = new Chart(barEl, {
        type: 'bar',
        data: {
          labels: [...labels].reverse(),
          datasets: [{
            label: 'Amount',
            data: [...data].reverse(),
            backgroundColor: '#2563eb'
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } }
        }
      });
    }

    // Group expenses by Month (YYYY-MM)
    const monthlyMap = {};
    expenses.forEach(x => {
      const ym = (x.expense_date || '').slice(0, 7) || '2026-09';
      monthlyMap[ym] = (monthlyMap[ym] || 0) + Number(x.amount || 0);
    });
    const months = Object.keys(monthlyMap).sort();
    const monthlyExpenses = months.map(m => monthlyMap[m]);

    // 3. Trend Chart (Monthly Expense vs Income)
    const trendEl = document.getElementById('trendChart');
    if (trendEl) {
      this.destroyChart('trend');
      activeCharts['trend'] = new Chart(trendEl, {
        type: 'bar',
        data: {
          labels: months.length ? months : ['Current'],
          datasets: [
            {
              type: 'bar',
              label: 'Expenses',
              data: monthlyExpenses.length ? monthlyExpenses : [0],
              backgroundColor: '#38bdf8'
            },
            {
              type: 'line',
              label: 'Income',
              data: (months.length ? months : ['Current']).map(() => income),
              borderColor: '#10b981',
              backgroundColor: '#10b981',
              tension: 0.1
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } }
        }
      });
    }

    // 4. Savings Chart (Cumulative Savings Trajectory)
    const savingsEl = document.getElementById('savingsChart');
    if (savingsEl) {
      this.destroyChart('savings');
      let cum = 0;
      const cumSavings = monthlyExpenses.map(exp => {
        cum += (income - exp);
        return cum;
      });

      activeCharts['savings'] = new Chart(savingsEl, {
        type: 'line',
        data: {
          labels: months.length ? months : ['Current'],
          datasets: [{
            label: 'Cumulative Savings',
            data: cumSavings.length ? cumSavings : [0],
            borderColor: '#2563eb',
            backgroundColor: 'rgba(37, 99, 235, 0.1)',
            fill: true,
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } }
        }
      });
    }
  },

  // ----------------------------------------------------------------
  // BUDGET PLANNER
  // ----------------------------------------------------------------
  renderBudgetPlanner() {
    const expenses = Storage.getExpenses();
    const budgets = Storage.getBudgets();
    const curr = (this.user && this.user.currency) || '₹';
    const income = Number(this.user?.income || 60000);

    // Sum by category for active budgets
    const catSpent = {};
    expenses.forEach(x => {
      catSpent[x.category] = (catSpent[x.category] || 0) + Number(x.amount || 0);
    });

    const totalAllocated = Object.values(budgets).reduce((a, b) => a + Number(b || 0), 0);
    const meta = document.getElementById('budget-meta');
    if (meta) {
      meta.textContent = `Total Allocated Budget: ${fmtCurrency(totalAllocated, curr)} | Monthly Income: ${fmtCurrency(income, curr)}`;
    }

    const list = document.getElementById('budget-list');
    if (list) {
      const budgetKeys = Object.keys(budgets);
      if (!budgetKeys.length) {
        list.innerHTML = '<p class="muted">No budgets configured yet.</p>';
        return;
      }

      list.innerHTML = budgetKeys.map(cat => {
        const limit = Number(budgets[cat] || 0);
        const spent = Number(catSpent[cat] || 0);
        const remaining = limit - spent;
        const pct = limit > 0 ? (spent / limit) * 100 : 0;
        let status = 'Within Budget';
        let barColor = '#2563eb';
        if (pct > 100) {
          status = 'Exceeded';
          barColor = '#b91c1c';
        } else if (pct > 80) {
          status = 'Near Limit';
          barColor = '#f59e0b';
        }

        return `
          <div class="budget-row">
            <div class="budget-row-head">
              <b>${cat}</b>
              <span>${status} (${pct.toFixed(1)}%)</span>
            </div>
            <div class="progress">
              <span style="width: ${Math.min(100, Math.max(0, pct))}%; background: ${barColor};"></span>
            </div>
            <small class="muted">Spent: ${fmtCurrency(spent, curr)} of ${fmtCurrency(limit, curr)} · Remaining: ${fmtCurrency(remaining, curr)}</small>
          </div>
        `;
      }).join('');
    }
  },

  // ----------------------------------------------------------------
  // ADD EXPENSE
  // ----------------------------------------------------------------
  setupAddExpense() {
    const batchBody = document.getElementById('batch-body');
    if (batchBody) {
      batchBody.innerHTML = '';
      for (let i = 0; i < 3; i++) {
        this.addBatchRow();
      }
    }
  },

  addBatchRow() {
    const batchBody = document.getElementById('batch-body');
    if (!batchBody) return;
    const catOptions = CATEGORIES.map(c => `<option value="${c}">${c}</option>`).join('');
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input class="r-amount" type="number" min="0" step="50" value="0"></td>
      <td><select class="r-cat">${catOptions}</select></td>
      <td><input class="r-desc" placeholder="Details..."></td>
      <td><input class="r-date" type="date" value="${getTodayStr()}"></td>
      <td><button type="button" class="batch-remove">Remove</button></td>
    `;
    tr.querySelector('.batch-remove').onclick = () => tr.remove();
    batchBody.appendChild(tr);
  },

  // ----------------------------------------------------------------
  // EXPENSE HISTORY
  // ----------------------------------------------------------------
  renderExpenseHistory() {
    this.filterExpenses();
  },

  filterExpenses() {
    const expenses = Storage.getExpenses();
    const curr = (this.user && this.user.currency) || '₹';

    const cat = document.getElementById('filter-category')?.value || 'All';
    const query = (document.getElementById('search-query')?.value || '').toLowerCase();
    const minAmount = Number(document.getElementById('min-amount')?.value || 0);
    const sortOrder = document.getElementById('sort-order')?.value || 'Newest First';

    let filtered = expenses.filter(x => {
      if (cat !== 'All' && x.category !== cat) return false;
      if (minAmount > 0 && Number(x.amount) < minAmount) return false;
      if (query) {
        const descMatch = (x.description || '').toLowerCase().includes(query);
        const catMatch = (x.category || '').toLowerCase().includes(query);
        if (!descMatch && !catMatch) return false;
      }
      return true;
    });

    filtered.sort((a, b) => {
      if (sortOrder === 'Highest Amount') return Number(b.amount) - Number(a.amount);
      if (sortOrder === 'Lowest Amount') return Number(a.amount) - Number(b.amount);
      if (sortOrder === 'Oldest First') return (a.expense_date || '').localeCompare(b.expense_date || '');
      return (b.expense_date || '').localeCompare(a.expense_date || '');
    });

    const totalSum = filtered.reduce((s, x) => s + Number(x.amount || 0), 0);
    const summaryEl = document.getElementById('history-summary');
    if (summaryEl) {
      summaryEl.textContent = `Showing ${filtered.length} records | Total Sum: ${fmtCurrency(totalSum, curr)}`;
    }

    const tbody = document.getElementById('history-body');
    if (tbody) {
      if (!filtered.length) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px;" class="muted">No matching expenses found.</td></tr>';
      } else {
        tbody.innerHTML = filtered.map(x => `
          <tr>
            <td>#${x.id}</td>
            <td><b>${fmtCurrency(x.amount, curr)}</b></td>
            <td>${x.category}</td>
            <td>${x.description || ''}</td>
            <td>${x.expense_date}</td>
            <td><button class="danger" onclick="App.deleteExpense(${x.id})">Delete</button></td>
          </tr>
        `).join('');
      }
    }

    this.currentFiltered = filtered;
  },

  deleteExpense(id) {
    if (confirm('Delete this expense record?')) {
      let expenses = Storage.getExpenses();
      expenses = expenses.filter(x => x.id !== id);
      Storage.setExpenses(expenses);
      showFlash('Expense record deleted.', 'success');
      this.filterExpenses();
    }
  },

  exportCSV(all = false) {
    const list = all ? Storage.getExpenses() : (this.currentFiltered || Storage.getExpenses());
    if (!list.length) {
      alert('No expense data to export.');
      return;
    }
    const headers = ['ID', 'Amount', 'Category', 'Description', 'Date'];
    const rows = list.map(x => [x.id, x.amount, `"${(x.category || '').replace(/"/g, '""')}"`, `"${(x.description || '').replace(/"/g, '""')}"`, x.expense_date]);
    const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = all ? 'all_expenses_export.csv' : 'filtered_expenses_export.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  // ----------------------------------------------------------------
  // PROFILE
  // ----------------------------------------------------------------
  renderProfile() {
    const expenses = Storage.getExpenses();
    const budgets = Storage.getBudgets();

    document.getElementById('profile-email').textContent = this.user?.email || 'user@example.com';
    document.getElementById('profile-name').value = this.user?.name || 'User';
    document.getElementById('profile-income').value = this.user?.income || 60000;
    document.getElementById('profile-currency').value = this.user?.currency || '₹';

    document.getElementById('profile-expenses').textContent = expenses.length.toLocaleString();
    document.getElementById('profile-budgets').textContent = Object.keys(budgets).length.toLocaleString();
  },

  // ----------------------------------------------------------------
  // DATASET ANALYZER
  // ----------------------------------------------------------------
  async loadSampleDataset() {
    try {
      showFlash('Loading 2020-2026 Sample Dataset...', 'success');
      const response = await fetch('data/sample_financial_data.csv');
      if (!response.ok) throw new Error('Sample dataset file could not be loaded.');
      const csvText = await response.text();
      this.processDatasetCSV(csvText, '2020-2026 Sample Financial Dataset');
    } catch (err) {
      showFlash('Could not fetch sample CSV, generating embedded dataset.', 'error');
      // Fallback: Generate mock financial data
      this.generateFallbackDataset();
    }
  },

  analyzeUploadedFile() {
    const fileInput = document.getElementById('dataset-file');
    const file = fileInput?.files[0];
    if (!file) {
      alert('Please choose a CSV file first.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      this.processDatasetCSV(text, file.name);
    };
    reader.readAsText(file);
  },

  processDatasetCSV(csvText, sourceName) {
    const lines = csvText.trim().split(/\r?\n/).filter(line => line.trim());
    if (lines.length < 2) {
      alert('CSV file is empty or missing headers.');
      return;
    }

    const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
    const rows = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(',').map(c => c.trim().replace(/^"|"$/g, ''));
      if (cols.length === headers.length) {
        const rowObj = {};
        headers.forEach((h, idx) => {
          const val = cols[idx];
          rowObj[h] = !isNaN(Number(val)) && val !== '' ? Number(val) : val;
        });
        rows.push(rowObj);
      }
    }

    this.renderDatasetOutput(rows, headers, sourceName);
  },

  generateFallbackDataset() {
    const headers = ['Month', 'Groceries', 'Rent', 'Transportation', 'Utilities', 'Healthcare', 'Dining & Entertainment', 'Total Expenditure', 'Income'];
    const rows = [];
    for (let yr = 2020; yr <= 2026; yr++) {
      for (let m = 1; m <= 12; m++) {
        const dt = `${yr}-${String(m).padStart(2, '0')}-01`;
        const rent = 10000;
        const groc = Math.floor(4000 + Math.random() * 3000);
        const trans = Math.floor(1000 + Math.random() * 1500);
        const util = Math.floor(1200 + Math.random() * 800);
        const health = Math.floor(500 + Math.random() * 1000);
        const dine = Math.floor(2000 + Math.random() * 2500);
        const total = rent + groc + trans + util + health + dine;
        const inc = Math.floor(35000 + (yr - 2020) * 4000);
        rows.push({
          'Month': dt,
          'Groceries': groc,
          'Rent': rent,
          'Transportation': trans,
          'Utilities': util,
          'Healthcare': health,
          'Dining & Entertainment': dine,
          'Total Expenditure': total,
          'Income': inc
        });
      }
    }
    this.renderDatasetOutput(rows, headers, 'Generated Multi-Year Financial Dataset');
  },

  renderDatasetOutput(rows, headers, sourceName) {
    const out = document.getElementById('dataset-output');
    if (!out) return;

    const curr = (this.user && this.user.currency) || '₹';
    const numRows = rows.length;
    const numCols = headers.length;

    // Detect numeric vs categorical columns
    const numericCols = headers.filter(h => rows.some(r => typeof r[h] === 'number'));
    const isFinancial = headers.some(h => /income|expenditure|rent|groceries/i.test(h));

    // Summary calculations
    let totalIncome = 0;
    let totalExpenditure = 0;
    const yearlyMap = {};
    const categoryTotals = {};

    if (isFinancial) {
      rows.forEach(r => {
        const inc = Number(r['Income'] || r['income'] || 0);
        const exp = Number(r['Total Expenditure'] || r['total_expenditure'] || r['Expenses'] || 0);
        totalIncome += inc;
        totalExpenditure += exp;

        // Group by Year
        const dateStr = String(r['Month'] || r['Date'] || '');
        const year = dateStr.includes('-') ? (dateStr.split('-')[0].length === 4 ? dateStr.split('-')[0] : dateStr.split('-')[2]) : '2025';
        if (!yearlyMap[year]) yearlyMap[year] = { year, income: 0, expenditure: 0, records: 0 };
        yearlyMap[year].income += inc;
        yearlyMap[year].expenditure += exp;
        yearlyMap[year].records++;

        // Category totals
        headers.forEach(h => {
          if (!/month|date|income|total/i.test(h) && typeof r[h] === 'number') {
            categoryTotals[h] = (categoryTotals[h] || 0) + r[h];
          }
        });
      });
    }

    const netSavings = totalIncome - totalExpenditure;

    let html = `
      <div class="status" style="margin-top: 20px;">
        Active Dataset: <b>${sourceName}</b> · ${numRows.toLocaleString()} rows · ${numCols} columns · Type: <b>${isFinancial ? 'Financial Wide Format' : 'General Tabular'}</b>
      </div>
      <div class="dataset-kpis">
        <div class="kpi"><small>Total Rows</small><strong>${numRows.toLocaleString()}</strong></div>
        <div class="kpi"><small>Total Columns</small><strong>${numCols}</strong></div>
        <div class="kpi"><small>Numeric Columns</small><strong>${numericCols.length}</strong></div>
        <div class="kpi"><small>Estimated Memory</small><strong>${(numRows * numCols * 8 / 1024).toFixed(1)} KB</strong></div>
      </div>
    `;

    if (isFinancial) {
      const years = Object.keys(yearlyMap).sort();
      const catList = Object.entries(categoryTotals).sort((a, b) => b[1] - a[1]);

      html += `
        <div class="card">
          <h2>Financial Analysis Mode</h2>
          <p>Multi-column financial structure recognized and evaluated across all recording periods.</p>
          <div class="dataset-kpis">
            <div class="kpi"><small>Total Recorded Days</small><strong>${numRows.toLocaleString()}</strong></div>
            <div class="kpi"><small>Total Income</small><strong>${fmtCurrency(totalIncome, curr)}</strong></div>
            <div class="kpi"><small>Total Expenditure</small><strong>${fmtCurrency(totalExpenditure, curr)}</strong></div>
            <div class="kpi"><small>Net Savings</small><strong>${fmtCurrency(netSavings, curr)}</strong></div>
          </div>

          <div class="grid-2">
            <div class="card chart-card">
              <h3>Yearly Income vs Expenditure</h3>
              <canvas id="dsYearChart"></canvas>
            </div>
            <div class="card chart-card">
              <h3>All-Time Category Distribution</h3>
              <canvas id="dsCatChart"></canvas>
            </div>
          </div>

          <div class="card chart-card">
            <h3>Annual Performance Breakdown</h3>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Year</th>
                    <th>Total Income</th>
                    <th>Total Expenses</th>
                    <th>Net Savings</th>
                    <th>Savings Rate</th>
                  </tr>
                </thead>
                <tbody>
                  ${years.map(y => {
                    const row = yearlyMap[y];
                    const svRate = row.income > 0 ? ((row.income - row.expenditure) / row.income * 100).toFixed(1) : '0.0';
                    return `
                      <tr>
                        <td><b>${y}</b></td>
                        <td>${fmtCurrency(row.income, curr)}</td>
                        <td>${fmtCurrency(row.expenditure, curr)}</td>
                        <td>${fmtCurrency(row.income - row.expenditure, curr)}</td>
                        <td>${svRate}%</td>
                      </tr>
                    `;
                  }).join('')}
                </tbody>
              </table>
            </div>
          </div>

          <div style="margin-top: 16px;">
            <button id="import-dataset-expenses" class="primary" type="button">Import Dataset Samples to Active Tracker</button>
          </div>
        </div>
      `;
    }

    // EDA Tabs
    html += `
      <div class="card">
        <h2>Exploratory Data Analysis</h2>
        <div class="tabs">
          <button class="tab active" data-target="eda-preview">Data Preview</button>
          <button class="tab" data-target="eda-stats">Statistical Summary</button>
        </div>

        <section id="eda-preview" class="tab-panel active">
          <h3>First 10 Records</h3>
          <div class="table-wrap">
            <table>
              <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
              <tbody>
                ${rows.slice(0, 10).map(r => `
                  <tr>${headers.map(h => `<td>${r[h] !== undefined ? r[h] : ''}</td>`).join('')}</tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </section>

        <section id="eda-stats" class="tab-panel">
          <h3>Numerical Columns Summary</h3>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Column</th>
                  <th>Total Sum</th>
                  <th>Mean / Avg</th>
                  <th>Min</th>
                  <th>Max</th>
                </tr>
              </thead>
              <tbody>
                ${numericCols.map(col => {
                  const vals = rows.map(r => Number(r[col])).filter(v => !isNaN(v));
                  const sum = vals.reduce((a, b) => a + b, 0);
                  const mean = vals.length ? sum / vals.length : 0;
                  const min = vals.length ? Math.min(...vals) : 0;
                  const max = vals.length ? Math.max(...vals) : 0;
                  return `
                    <tr>
                      <td><b>${col}</b></td>
                      <td>${sum.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                      <td>${mean.toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                      <td>${min.toLocaleString()}</td>
                      <td>${max.toLocaleString()}</td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    `;

    out.innerHTML = html;

    // Attach Import Handler
    const importBtn = document.getElementById('import-dataset-expenses');
    if (importBtn) {
      importBtn.onclick = () => {
        const expenses = Storage.getExpenses();
        let nextId = expenses.length ? Math.max(...expenses.map(x => x.id || 0)) + 1 : 1;
        let count = 0;
        rows.slice(0, 25).forEach(r => {
          headers.forEach(h => {
            if (!/month|date|income|total/i.test(h) && typeof r[h] === 'number' && r[h] > 0) {
              const dt = String(r['Month'] || r['Date'] || getTodayStr());
              expenses.unshift({
                id: nextId++,
                amount: r[h],
                category: CATEGORIES.includes(h) ? h : 'Other',
                description: `Imported (${h})`,
                expense_date: dt.includes('-') && dt.length === 10 ? dt : getTodayStr()
              });
              count++;
            }
          });
        });
        Storage.setExpenses(expenses);
        showFlash(`Imported ${count} expenses into your tracker!`, 'success');
        importBtn.disabled = true;
      };
    }

    // Tab switching for EDA
    document.querySelectorAll('#dataset-output .tab').forEach(btn => {
      btn.onclick = () => {
        document.querySelectorAll('#dataset-output .tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('#dataset-output .tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const target = document.getElementById(btn.dataset.target);
        if (target) target.classList.add('active');
      };
    });

    // Render dataset charts
    if (isFinancial) {
      const years = Object.keys(yearlyMap).sort();
      const yearInc = years.map(y => yearlyMap[y].income);
      const yearExp = years.map(y => yearlyMap[y].expenditure);

      const dsYear = document.getElementById('dsYearChart');
      if (dsYear) {
        new Chart(dsYear, {
          type: 'bar',
          data: {
            labels: years,
            datasets: [
              { label: 'Income', data: yearInc, backgroundColor: '#10b981' },
              { label: 'Expenditure', data: yearExp, backgroundColor: '#ef4444' }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
          }
        });
      }

      const catList = Object.entries(categoryTotals).sort((a, b) => b[1] - a[1]);
      const dsCat = document.getElementById('dsCatChart');
      if (dsCat) {
        new Chart(dsCat, {
          type: 'doughnut',
          data: {
            labels: catList.map(c => c[0]),
            datasets: [{
              data: catList.map(c => c[1]),
              backgroundColor: ['#2563eb', '#38bdf8', '#34d399', '#f59e0b', '#ec4899', '#8b5cf6', '#64748b']
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
          }
        });
      }
    }
  }
};

// Start application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
