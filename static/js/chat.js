/**
 * AI Career Guidance Assistant - Client-Side Interactive Logic
 * Task AI-SS-005 | Student: Sarbajit Das (DAS013423)
 */

document.addEventListener('DOMContentLoaded', () => {
  const sessionId = 'web_session_' + Math.random().toString(36).substring(2, 9);
  let allCareersData = {};
  let popularSkills = [
    'Python', 'SQL', 'Machine Learning', 'Deep Learning', 'Statistics',
    'Java', 'C++', 'Data Structures', 'React', 'Node.js', 'JavaScript',
    'HTML5/CSS3', 'Docker', 'Kubernetes', 'Linux', 'AWS', 'Terraform',
    'Network Security', 'Penetration Testing', 'Figma', 'UI/UX Design',
    'Product Strategy', 'Solidity', 'Embedded C / C++', 'Tableau', 'Power BI'
  ];
  let selectedSkills = new Set();

  // Initialize UI elements
  initTabs();
  initChat(sessionId);
  initCareerExplorer();
  initSkillMatcher();
  initMarketTrends();

  // ==========================================
  // TAB NAVIGATION
  // ==========================================
  function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const targetId = btn.getAttribute('data-tab');
        tabBtns.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        const targetContent = document.getElementById(targetId);
        if (targetContent) {
          targetContent.classList.add('active');
        }
      });
    });
  }

  // ==========================================
  // TAB 1: CHAT SYSTEM
  // ==========================================
  function initChat(session) {
    const chatMessages = document.getElementById('chatMessages');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const quickChips = document.querySelectorAll('.quick-chips .chip');

    // Send on button click
    sendBtn.addEventListener('click', () => handleSendMessage());

    // Send on Enter key
    userInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        handleSendMessage();
      }
    });

    // Quick chips
    quickChips.forEach(chip => {
      chip.addEventListener('click', () => {
        const query = chip.getAttribute('data-query');
        userInput.value = query;
        handleSendMessage();
      });
    });

    // Clear chat
    clearChatBtn.addEventListener('click', async () => {
      chatMessages.innerHTML = `
        <div class="message bot-message">
          <div class="avatar">🤖</div>
          <div class="bubble">
            <p><strong>Chat session reset.</strong> What career topic or question would you like to explore?</p>
          </div>
        </div>
      `;
      try {
        await fetch('/api/reset', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: session })
        });
      } catch (err) {
        console.error('Reset error:', err);
      }
    });

    async function handleSendMessage() {
      const text = userInput.value.trim();
      if (!text) return;

      // Append user bubble
      appendMessage('user', text);
      userInput.value = '';
      userInput.focus();

      // Show typing indicator
      const typingEl = appendTypingIndicator();

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, session_id: session })
        });
        const data = await res.json();
        typingEl.remove();

        if (data.status === 'success') {
          appendMessage('bot', data.response);
        } else {
          appendMessage('bot', '⚠️ ' + (data.response || 'An error occurred while answering.'));
        }
      } catch (error) {
        typingEl.remove();
        appendMessage('bot', '❌ Failed to connect to AI server. Please make sure Flask is running.');
      }
    }

    function appendMessage(role, content) {
      const msgDiv = document.createElement('div');
      msgDiv.className = `message ${role}-message`;

      const avatar = document.createElement('div');
      avatar.className = 'avatar';
      avatar.innerText = role === 'user' ? '👤' : '🤖';

      const bubble = document.createElement('div');
      bubble.className = 'bubble';
      bubble.innerHTML = formatMarkdown(content);

      msgDiv.appendChild(avatar);
      msgDiv.appendChild(bubble);
      chatMessages.appendChild(msgDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
      const typingDiv = document.createElement('div');
      typingDiv.className = 'message bot-message typing-indicator-msg';
      typingDiv.innerHTML = `
        <div class="avatar">🤖</div>
        <div class="bubble" style="color: #94a3b8; font-style: italic;">
          AI Assistant is thinking...
        </div>
      `;
      chatMessages.appendChild(typingDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      return typingDiv;
    }
  }

  // ==========================================
  // TAB 2: CAREER EXPLORER
  // ==========================================
  async function initCareerExplorer() {
    const grid = document.getElementById('careersGrid');
    const searchInput = document.getElementById('careerSearchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const modal = document.getElementById('careerModal');
    const closeModalBtn = document.getElementById('closeModalBtn');

    closeModalBtn.addEventListener('click', () => modal.classList.remove('active'));
    window.addEventListener('click', (e) => {
      if (e.target === modal) modal.classList.remove('active');
    });

    try {
      const res = await fetch('/api/careers');
      const data = await res.json();
      if (data.status === 'success') {
        allCareersData = data.careers;
        renderCareers(allCareersData);
      }
    } catch (err) {
      grid.innerHTML = '<p class="empty-state">Failed to load careers catalog.</p>';
    }

    searchInput.addEventListener('input', () => filterAndRender());
    categoryFilter.addEventListener('change', () => filterAndRender());

    function filterAndRender() {
      const query = searchInput.value.toLowerCase().trim();
      const selectedCat = categoryFilter.value;

      const filtered = {};
      for (const [key, c] of Object.entries(allCareersData)) {
        const matchesQuery = !query ||
          c.title.toLowerCase().includes(query) ||
          c.description.toLowerCase().includes(query) ||
          (c.core_skills && c.core_skills.some(s => s.toLowerCase().includes(query)));

        const matchesCat = selectedCat === 'all' ||
          c.category.toLowerCase().includes(selectedCat.toLowerCase());

        if (matchesQuery && matchesCat) {
          filtered[key] = c;
        }
      }
      renderCareers(filtered);
    }

    function renderCareers(careers) {
      grid.innerHTML = '';
      const keys = Object.keys(careers);
      if (keys.length === 0) {
        grid.innerHTML = '<div class="empty-state"><span class="icon">🔍</span><p>No careers matched your search criteria.</p></div>';
        return;
      }

      keys.forEach(key => {
        const c = careers[key];
        const card = document.createElement('div');
        card.className = 'career-card';

        const demandClass = (c.demand_level || '').toLowerCase().includes('very') ? 'badge-very-high' : 'badge-high';
        const skillsList = (c.core_skills || []).slice(0, 5).map(s => `<span class="skill-tag">${s}</span>`).join('');

        card.innerHTML = `
          <div>
            <div class="career-card-top">
              <div>
                <h3 class="career-card-title">${c.title}</h3>
                <span class="career-card-cat">${c.category}</span>
              </div>
              <span class="badge ${demandClass}">${c.demand_level || 'High Demand'}</span>
            </div>
            <p class="career-card-desc">${c.description}</p>
            <div class="career-card-skills">
              ${skillsList}
            </div>
          </div>
          <div class="career-card-meta">
            <span class="salary-tag">${c.salary_range ? c.salary_range.mid : '₹12-25 LPA'}</span>
            <span class="growth-tag">📈 ${c.growth_rate || '20%+ Growth'}</span>
          </div>
        `;

        card.addEventListener('click', () => openCareerModal(key, c));
        grid.appendChild(card);
      });
    }

    function openCareerModal(key, c) {
      const modalBody = document.getElementById('modalBody');
      const modal = document.getElementById('careerModal');

      const coreSkillsHtml = (c.core_skills || []).map(s => `<span class="skill-tag">${s}</span>`).join(' ');
      const toolsHtml = (c.tools_and_technologies || []).map(t => `<span class="skill-tag">${t}</span>`).join(' ');
      const companiesHtml = (c.top_hiring_companies || []).join(', ');
      const progressionHtml = (c.career_progression || []).join(' ➔ ');

      const roadmapHtml = (c.learning_roadmap || []).map(r => `<li>${r}</li>`).join('');
      const questionsHtml = (c.interview_questions || []).map(q => `<li>${q}</li>`).join('');
      const tipsHtml = (c.interview_tips || []).map(t => `<li>${t}</li>`).join('');

      modalBody.innerHTML = `
        <div style="margin-bottom: 1.5rem;">
          <h2 style="font-size: 1.6rem; color: #fff; margin-bottom: 0.25rem;">💼 ${c.title}</h2>
          <span style="color: var(--accent-cyan); font-weight: 600;">${c.category}</span>
        </div>

        <div class="modal-section">
          <h4>Role Overview</h4>
          <p style="color: var(--text-muted); font-size: 0.95rem;">${c.description}</p>
        </div>

        <div class="modal-section">
          <h4>Required Skill Stack</h4>
          <p style="margin-bottom: 0.5rem;"><strong>Core Skills:</strong> ${coreSkillsHtml}</p>
          <p><strong>Tools & Frameworks:</strong> ${toolsHtml}</p>
        </div>

        <div class="modal-section">
          <h4>Salary Compensation</h4>
          <div style="background: var(--bg-primary); padding: 0.85rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); font-size: 0.9rem;">
            <p>🟢 <strong>Entry Level (0-2 yrs):</strong> ${c.salary_range ? c.salary_range.entry : 'N/A'}</p>
            <p>🟡 <strong>Mid Level (3-6 yrs):</strong> ${c.salary_range ? c.salary_range.mid : 'N/A'}</p>
            <p>🔴 <strong>Senior Level (7+ yrs):</strong> ${c.salary_range ? c.salary_range.senior : 'N/A'}</p>
          </div>
        </div>

        <div class="modal-section">
          <h4>Top Recruiters & Progression</h4>
          <p><strong>Recruiting Companies:</strong> ${companiesHtml}</p>
          <p style="margin-top: 0.35rem;"><strong>Career Path:</strong> <span style="color: var(--accent-emerald);">${progressionHtml}</span></p>
        </div>

        <div class="modal-section">
          <h4>4-Phase Learning Roadmap</h4>
          <ul style="margin-left: 1.25rem; color: var(--text-muted); font-size: 0.88rem;">${roadmapHtml}</ul>
        </div>

        <div class="modal-section">
          <h4>Top Technical Interview Questions</h4>
          <ol style="margin-left: 1.25rem; color: var(--text-muted); font-size: 0.88rem;">${questionsHtml}</ol>
        </div>

        <div class="modal-section">
          <h4>Interview Preparation Tips</h4>
          <ul style="margin-left: 1.25rem; color: var(--text-muted); font-size: 0.88rem;">${tipsHtml}</ul>
        </div>
      `;

      modal.classList.add('active');
    }
  }

  // ==========================================
  // TAB 3: SKILL MATCHER
  // ==========================================
  function initSkillMatcher() {
    const popularContainer = document.getElementById('popularSkillsContainer');
    const customSkillsInput = document.getElementById('customSkillsInput');
    const interestsInput = document.getElementById('interestsInput');
    const calculateRecsBtn = document.getElementById('calculateRecsBtn');
    const recsOutput = document.getElementById('recsOutput');

    // Populate skill buttons
    popularSkills.forEach(skill => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'skill-pill-btn';
      btn.innerText = skill;
      btn.addEventListener('click', () => {
        if (selectedSkills.has(skill)) {
          selectedSkills.delete(skill);
          btn.classList.remove('active');
        } else {
          selectedSkills.add(skill);
          btn.classList.add('active');
        }
      });
      popularContainer.appendChild(btn);
    });

    calculateRecsBtn.addEventListener('click', async () => {
      // Collect all selected skills + custom skills
      const customVal = customSkillsInput.value.trim();
      let combined = Array.from(selectedSkills);
      if (customVal) {
        const extra = customVal.split(',').map(s => s.trim()).filter(Boolean);
        combined = Array.from(new Set([...combined, ...extra]));
      }

      const interests = interestsInput.value.trim();

      if (combined.length === 0 && !interests) {
        alert('Please select or enter at least one skill or interest!');
        return;
      }

      recsOutput.innerHTML = '<div class="empty-state"><p>Calculating career fit and skill gaps...</p></div>';

      try {
        const res = await fetch('/api/recommend', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ skills: combined, interests: interests, top_n: 4 })
        });
        const data = await res.json();

        if (data.status === 'success' && data.recommendations) {
          renderRecommendations(data.recommendations);
        } else {
          recsOutput.innerHTML = '<div class="empty-state"><p>No recommendations could be generated.</p></div>';
        }
      } catch (err) {
        recsOutput.innerHTML = '<div class="empty-state"><p>❌ Error calculating recommendations.</p></div>';
      }
    });

    function renderRecommendations(recs) {
      recsOutput.innerHTML = '';
      recs.forEach((r, idx) => {
        const card = document.createElement('div');
        card.className = 'rec-result-card';

        const matchedPills = (r.matched_skills || []).map(s => `<span class="matched-pill">✓ ${s}</span>`).join(' ') || '<span style="color: #64748b; font-size: 0.75rem;">None yet</span>';
        const missingPills = (r.missing_skills || []).map(s => `<span class="missing-pill">+ ${s}</span>`).join(' ') || '<span style="color: var(--accent-emerald); font-size: 0.75rem;">No missing core skills!</span>';

        card.innerHTML = `
          <div class="rec-card-header">
            <div>
              <span style="font-size: 0.8rem; color: var(--accent-cyan); font-weight: 600;">Rank #${idx + 1}</span>
              <h4 class="rec-title">${r.title}</h4>
            </div>
            <div class="match-score-badge">${r.match_percentage}% Fit</div>
          </div>
          <p style="font-size: 0.86rem; color: var(--text-muted); margin-bottom: 0.5rem;">${r.description}</p>
          <div style="font-size: 0.82rem; margin-bottom: 0.5rem;">
            💰 <strong>Salary:</strong> ${r.salary_range ? r.salary_range.mid : '₹12-25 LPA'} | 📈 <strong>Demand:</strong> ${r.demand_level}
          </div>
          <div class="skill-gap-section">
            <div style="margin-bottom: 0.4rem;">
              <span class="skill-gap-title">✅ Matched Skills:</span>
              <div style="display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.2rem;">${matchedPills}</div>
            </div>
            <div>
              <span class="skill-gap-title">⏳ Skill Gaps to Bridge:</span>
              <div style="display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.2rem;">${missingPills}</div>
            </div>
          </div>
        `;
        recsOutput.appendChild(card);
      });
    }
  }

  // ==========================================
  // TAB 4: MARKET TRENDS
  // ==========================================
  async function initMarketTrends() {
    const overviewEl = document.getElementById('trendsOverviewText');
    const trendsList = document.getElementById('trendsList');
    const predictionsList = document.getElementById('marketPredictionsList');
    const salarySummaryList = document.getElementById('salarySummaryList');

    try {
      const res = await fetch('/api/trends');
      const data = await res.json();
      if (data.status === 'success' && data.trends) {
        const t = data.trends;
        overviewEl.innerText = t.overview || '';

        // Top trends
        trendsList.innerHTML = '';
        (t.top_trends || []).forEach(item => {
          const div = document.createElement('div');
          div.className = 'trend-item';
          const skillsTags = (item.high_demand_skills || []).map(s => `<span class="skill-tag">${s}</span>`).join(' ');
          div.innerHTML = `
            <div class="trend-item-header">
              <span class="trend-domain">${item.rank}. ${item.domain}</span>
              <span class="trend-growth">${item.growth_rate}</span>
            </div>
            <p class="trend-drivers">${item.key_drivers}</p>
            <div style="display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.4rem;">
              ${skillsTags}
            </div>
          `;
          trendsList.appendChild(div);
        });

        // Predictions
        predictionsList.innerHTML = '';
        (t.market_predictions || []).forEach(p => {
          const li = document.createElement('li');
          li.innerText = p;
          predictionsList.appendChild(li);
        });

        // Starting packages
        salarySummaryList.innerHTML = '';
        const starting = (t.salary_insights_summary && t.salary_insights_summary.highest_starting_packages) || [];
        starting.forEach(s => {
          const li = document.createElement('li');
          li.innerText = s;
          salarySummaryList.appendChild(li);
        });
      }
    } catch (err) {
      overviewEl.innerText = 'Unable to fetch real-time trends.';
    }
  }

  // Basic markdown formatter for chatbot messages
  function formatMarkdown(text) {
    if (!text) return '';
    let html = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/### (.*?)\n/g, '<h4 style="margin: 0.5rem 0 0.2rem; color: #a5b4fc;">$1</h4>')
      .replace(/## (.*?)\n/g, '<h3 style="margin: 0.7rem 0 0.3rem; color: #fff;">$1</h3>')
      .replace(/`([^`]+)`/g, '<code style="background: rgba(0,0,0,0.3); padding: 0.1rem 0.3rem; border-radius: 3px; font-family: monospace;">$1</code>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');

    return `<p>${html}</p>`;
  }
});
