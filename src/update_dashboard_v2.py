import json
import os

with open('outputs/dashboard_v2_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

json_str = json.dumps(d)

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SupeRR Selector Season 2 — Rajasthan Royals Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --rr-pink: #E91E63;
            --rr-pink-light: #FF4081;
            --rr-pink-glow: rgba(233, 30, 99, 0.25);
            --rr-navy: #0F172A;
            --rr-card-bg: #1E293B;
            --rr-border: #334155;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --accent-blue: #38BDF8;
            --accent-gold: #F59E0B;
            --accent-green: #10B981;
            --accent-red: #EF4444;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: #0B0F19;
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        header {{
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%);
            border-bottom: 2px solid var(--rr-pink);
            padding: 18px 36px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .brand-container {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .brand-logo {{
            background: var(--rr-pink);
            color: white;
            font-weight: 800;
            font-size: 18px;
            padding: 7px 12px;
            border-radius: 8px;
            letter-spacing: 1px;
            box-shadow: 0 0 15px var(--rr-pink-glow);
        }}

        .brand-text h1 {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}

        .brand-text p {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .nav-tabs {{
            display: flex;
            gap: 6px;
            background: rgba(15, 23, 42, 0.6);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--rr-border);
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 7px 14px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .tab-btn.active {{
            background: var(--rr-pink);
            color: white;
            box-shadow: 0 0 12px var(--rr-pink-glow);
        }}

        .tab-btn:hover:not(.active) {{
            color: white;
            background: rgba(255, 255, 255, 0.05);
        }}

        .dashboard-container {{
            padding: 24px 36px;
            max-width: 1600px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }}

        .kpi-card {{
            background: #141E33;
            border: 1px solid var(--rr-border);
            border-radius: 8px;
            padding: 16px;
            position: relative;
            overflow: hidden;
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 4px;
            background: var(--rr-pink);
        }}

        .kpi-card.blue::before {{ background: var(--accent-blue); }}
        .kpi-card.green::before {{ background: var(--accent-green); }}
        .kpi-card.gold::before {{ background: var(--accent-gold); }}

        .kpi-label {{
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .kpi-val {{
            font-size: 24px;
            font-weight: 800;
            margin: 4px 0;
            font-family: 'JetBrains Mono', monospace;
        }}

        .kpi-sub {{
            font-size: 11.5px;
            color: var(--text-muted);
        }}

        .card {{
            background: var(--rr-card-bg);
            border-radius: 10px;
            border: 1px solid var(--rr-border);
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 10px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .card-title {{
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .badge {{
            font-size: 10.5px;
            padding: 3px 7px;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .badge-pink {{ background: rgba(233, 30, 99, 0.2); color: var(--rr-pink-light); border: 1px solid var(--rr-pink); }}
        .badge-blue {{ background: rgba(56, 189, 248, 0.2); color: var(--accent-blue); border: 1px solid var(--accent-blue); }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-gold {{ background: rgba(245, 158, 11, 0.2); color: var(--accent-gold); border: 1px solid var(--accent-gold); }}

        .table-responsive {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13px;
        }}

        thead th {{
            background: #151D2F;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 10.5px;
            padding: 10px 12px;
            border-bottom: 2px solid var(--rr-border);
            white-space: nowrap;
        }}

        tbody tr {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            transition: background 0.15s ease;
        }}

        tbody tr:hover {{
            background: rgba(233, 30, 99, 0.05);
        }}

        tbody td {{
            padding: 10px 12px;
            white-space: nowrap;
        }}

        .player-rank {{
            background: #0B0F19;
            border: 1px solid var(--rr-border);
            width: 26px;
            height: 26px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
        }}

        .rank-top3 {{
            border-color: var(--rr-pink);
            color: var(--rr-pink-light);
            background: rgba(233, 30, 99, 0.15);
        }}

        .metric-mono {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }}

        .positive {{ color: var(--accent-green); }}
        .negative {{ color: var(--accent-red); }}

        .search-box {{
            background: #111827;
            border: 1px solid var(--rr-border);
            border-radius: 6px;
            padding: 7px 12px;
            color: white;
            font-size: 12.5px;
            width: 240px;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--rr-pink);
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 16px;
        }}

        @media (max-width: 1024px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
            .dashboard-container {{ padding: 16px; }}
            header {{ padding: 12px 16px; }}
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand-container">
            <div class="brand-logo">RR</div>
            <div class="brand-text">
                <h1>SupeRR Selector Season 2 — Rajasthan Royals Analytics</h1>
                <p>CRISP-X V2 Top 20 Pressure Performers & Format-Adjusted Franchise Valuation</p>
            </div>
        </div>
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('batters', event)">Top 20 Batters</button>
            <button class="tab-btn" onclick="switchTab('bowlers', event)">Top 20 Bowlers</button>
            <button class="tab-btn" onclick="switchTab('ipl_only', event)">IPL-Only Top 20</button>
            <button class="tab-btn" onclick="switchTab('comparisons', event)">Player Matchups</button>
            <button class="tab-btn" onclick="switchTab('models', event)">Validation & ML Models</button>
            <button class="tab-btn" onclick="switchTab('audit', event)">Data Reconciliation</button>
        </div>
    </header>

    <div class="dashboard-container">

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Deliveries Reconciled</div>
                <div class="kpi-val">200,999</div>
                <div class="kpi-sub">192,445 Legal Deliveries (867 Matches)</div>
            </div>
            <div class="kpi-card blue">
                <div class="kpi-label">Chasing WP ROC-AUC</div>
                <div class="kpi-val">0.9059</div>
                <div class="kpi-sub">0.1368 Brier Score Calibration</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-label">Crisis Wicket Value</div>
                <div class="kpi-val">5.61 Runs</div>
                <div class="kpi-sub">Powerplay: 11.89 | Death: 2.30 Runs</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-label">Bootstrap Iterations</div>
                <div class="kpi-val">2,000</div>
                <div class="kpi-sub">Match-Clustered Monte Carlo</div>
            </div>
        </div>

        <!-- TAB 1: TOP 20 BATTERS -->
        <div id="tab-batters" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        Top 20 Pressure Batters (Combined IPL & T20I)
                        <span class="badge badge-pink">Ranked 1–20</span>
                        <span class="badge badge-blue">Min 150 Pressure Balls</span>
                    </div>
                    <div>
                        <input type="text" id="bSearch" class="search-box" placeholder="Search batter..." onkeyup="filterTable('bTable', this.value)">
                    </div>
                </div>

                <div class="table-responsive">
                    <table id="bTable">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>IPL / T20I Balls</th>
                                <th>Runs</th>
                                <th>Pressure SR</th>
                                <th>Delta (Δ)</th>
                                <th>RAE (Runs Above Exp)</th>
                                <th>Rating</th>
                                <th>95% CI</th>
                                <th>P(Top 20)</th>
                                <th>Evidence Tier</th>
                            </tr>
                        </thead>
                        <tbody id="bTableBody"></tbody>
                    </table>
                </div>
            </div>

            <div class="charts-grid">
                <div class="card">
                    <div class="card-header"><div class="card-title">Batting Runs Above Expected (RAE)</div></div>
                    <canvas id="chartBatRAE"></canvas>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">Pressure Strike Rate Elevation (Δ)</div></div>
                    <canvas id="chartBatDelta"></canvas>
                </div>
            </div>
        </div>

        <!-- TAB 2: TOP 20 BOWLERS -->
        <div id="tab-bowlers" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        Top 20 Pressure Bowlers (Combined IPL & T20I)
                        <span class="badge badge-pink">Ranked 1–20</span>
                        <span class="badge badge-blue">Min 150 Pressure Balls</span>
                    </div>
                    <div>
                        <input type="text" id="bwSearch" class="search-box" placeholder="Search bowler..." onkeyup="filterTable('bwTable', this.value)">
                    </div>
                </div>

                <div class="table-responsive">
                    <table id="bwTable">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>IPL / T20I Balls</th>
                                <th>Wickets</th>
                                <th>Pressure Econ</th>
                                <th>Runs Prevented (RPA)</th>
                                <th>Wicket Impact</th>
                                <th>Rating</th>
                                <th>95% CI</th>
                                <th>P(Top 20)</th>
                                <th>Evidence Tier</th>
                            </tr>
                        </thead>
                        <tbody id="bwTableBody"></tbody>
                    </table>
                </div>
            </div>

            <div class="charts-grid">
                <div class="card">
                    <div class="card-header"><div class="card-title">Runs Prevented Above Expected (RPA)</div></div>
                    <canvas id="chartBowlRPA"></canvas>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">Pressure Economy vs Pressure Wickets</div></div>
                    <canvas id="chartBowlScatter"></canvas>
                </div>
            </div>
        </div>

        <!-- TAB 3: IPL-ONLY -->
        <div id="tab-ipl_only" class="tab-content" style="display: none;">
            <div class="charts-grid">
                <div class="card">
                    <div class="card-header"><div class="card-title">Top 20 IPL-Only Batters (Min 80 Balls)</div></div>
                    <div class="table-responsive">
                        <table id="iplBatTable">
                            <thead>
                                <tr><th>Rank</th><th>Player</th><th>Balls</th><th>Runs</th><th>SR</th><th>RAE</th><th>Rating</th></tr>
                            </thead>
                            <tbody id="iplBatTableBody"></tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header"><div class="card-title">Top 20 IPL-Only Bowlers (Min 80 Balls)</div></div>
                    <div class="table-responsive">
                        <table id="iplBowlTable">
                            <thead>
                                <tr><th>Rank</th><th>Player</th><th>Balls</th><th>Wkts</th><th>Econ</th><th>RPA</th><th>Rating</th></tr>
                            </thead>
                            <tbody id="iplBowlTableBody"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: HEAD TO HEAD -->
        <div id="tab-comparisons" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header"><div class="card-title">Key Player Head-to-Head Investigations</div><span class="badge badge-green">Adversarial Decisions</span></div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr><th>Matchup</th><th>Role</th><th>Data-Driven Winner</th><th>Margin</th><th>Analytics Rationale</th></tr>
                        </thead>
                        <tbody id="compTableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 5: MODELS -->
        <div id="tab-models" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header"><div class="card-title">Out-of-Sample Expected Runs & Win Probability Validation</div><span class="badge badge-green">2026 Holdout</span></div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr><th>Model Architecture</th><th>Target</th><th>Holdout MAE</th><th>Holdout RMSE</th><th>Brier / Calib</th><th>Status</th></tr>
                        </thead>
                        <tbody id="modelsTableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- TAB 6: AUDIT RECONCILIATION -->
        <div id="tab-audit" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header"><div class="card-title">Canonical 200,999 Deliveries & Extras Reconciliation</div><span class="badge badge-pink">Executable Assertions</span></div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr><th>Item / Category</th><th>Delivery Count / Balls</th><th>Total Match Runs</th><th>Bowler Conceded Runs</th><th>Attribution Rule</th></tr>
                        </thead>
                        <tbody id="recTableBody"></tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>

    <script>
        const d = {json_str};

        function populateAll() {{
            // Top 20 Batters
            const bBody = document.getElementById('bTableBody');
            bBody.innerHTML = '';
            d.batters_top20.forEach(b => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><div class="player-rank ${{b.Rank <= 3 ? 'rank-top3' : ''}}">${{b.Rank}}</div></td>
                    <td style="font-weight: 700; color: white;">${{b.Player}}</td>
                    <td class="metric-mono">${{b['IPL Pressure Balls']}} / ${{b['T20I Pressure Balls']}}</td>
                    <td class="metric-mono">${{b['Pressure Runs']}}</td>
                    <td class="metric-mono">${{b['Pressure SR'].toFixed(1)}}</td>
                    <td class="metric-mono ${{b['SR Difference'] >= 0 ? 'positive' : 'negative'}}">${{b['SR Difference'] > 0 ? '+' : ''}}${{b['SR Difference'].toFixed(1)}}</td>
                    <td class="metric-mono positive">+${{b['RAE'].toFixed(1)}}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light); font-weight: 700;">${{b['Adjusted Rating'].toFixed(1)}}</td>
                    <td class="metric-mono">${{b['95% CI']}}</td>
                    <td class="metric-mono">${{b['P(Top 20)']}}</td>
                    <td><span class="badge ${{b['Evidence Tier'].includes('Tier 1') ? 'badge-green' : (b['Evidence Tier'].includes('Tier 2') ? 'badge-blue' : 'badge-gold')}}">${{b['Evidence Tier']}}</span></td>
                `;
                bBody.appendChild(tr);
            }});

            // Top 20 Bowlers
            const bwBody = document.getElementById('bwTableBody');
            bwBody.innerHTML = '';
            d.bowlers_top20.forEach(b => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><div class="player-rank ${{b.Rank <= 3 ? 'rank-top3' : ''}}">${{b.Rank}}</div></td>
                    <td style="font-weight: 700; color: white;">${{b.Player}}</td>
                    <td class="metric-mono">${{b['IPL Pressure Balls']}} / ${{b['T20I Pressure Balls']}}</td>
                    <td class="metric-mono">${{b['Pressure Wickets']}}</td>
                    <td class="metric-mono">${{b['Pressure Economy'].toFixed(2)}}</td>
                    <td class="metric-mono ${{b['Runs Prevented'] >= 0 ? 'positive' : 'negative'}}">${{b['Runs Prevented'] > 0 ? '+' : ''}}${{b['Runs Prevented'].toFixed(1)}}</td>
                    <td class="metric-mono positive">+${{b['Wicket Impact'].toFixed(1)}}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light); font-weight: 700;">${{b['Adjusted Rating'].toFixed(1)}}</td>
                    <td class="metric-mono">${{b['95% CI']}}</td>
                    <td class="metric-mono">${{b['P(Top 20)']}}</td>
                    <td><span class="badge ${{b['Evidence Tier'].includes('Tier 1') ? 'badge-green' : (b['Evidence Tier'].includes('Tier 2') ? 'badge-blue' : 'badge-gold')}}">${{b['Evidence Tier']}}</span></td>
                `;
                bwBody.appendChild(tr);
            }});

            // IPL Only Batters
            const iplBBody = document.getElementById('iplBatTableBody');
            iplBBody.innerHTML = '';
            d.ipl_batters.forEach(b => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><div class="player-rank">${{b.Rank}}</div></td>
                    <td style="font-weight: 700; color: white;">${{b.striker_name}}</td>
                    <td class="metric-mono">${{b.p_balls}}</td>
                    <td class="metric-mono">${{b.p_runs}}</td>
                    <td class="metric-mono">${{b.p_sr.toFixed(1)}}</td>
                    <td class="metric-mono positive">+${{b.p_rae.toFixed(1)}}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light);">${{b.Adjusted_Rating.toFixed(1)}}</td>
                `;
                iplBBody.appendChild(tr);
            }});

            // IPL Only Bowlers
            const iplBwBody = document.getElementById('iplBowlTableBody');
            iplBwBody.innerHTML = '';
            d.ipl_bowlers.forEach(b => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><div class="player-rank">${{b.Rank}}</div></td>
                    <td style="font-weight: 700; color: white;">${{b.bowler_name}}</td>
                    <td class="metric-mono">${{b.p_balls}}</td>
                    <td class="metric-mono">${{b.p_wkts}}</td>
                    <td class="metric-mono">${{b.p_econ.toFixed(2)}}</td>
                    <td class="metric-mono ${{b.p_rpa >= 0 ? 'positive' : 'negative'}}">${{b.p_rpa > 0 ? '+' : ''}}${{b.p_rpa.toFixed(1)}}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light);">${{b.Adjusted_Rating.toFixed(1)}}</td>
                `;
                iplBwBody.appendChild(tr);
            }});

            // Comparisons
            const compBody = document.getElementById('compTableBody');
            compBody.innerHTML = '';
            d.comparisons.forEach(c => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 700; color: white;">${{c.Comparison}}</td>
                    <td><span class="badge ${{c.Category === 'Batter' ? 'badge-pink' : 'badge-blue'}}">${{c.Category}}</span></td>
                    <td style="font-weight: 700; color: var(--accent-green);">${{c.Winner}}</td>
                    <td class="metric-mono">${{c.Margin}}</td>
                    <td style="font-size: 12px; color: #CBD5E1;">${{c.Rationale}}</td>
                `;
                compBody.appendChild(tr);
            }});

            // ML Models
            const mBody = document.getElementById('modelsTableBody');
            mBody.innerHTML = '';
            d.ml_models.forEach(m => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 600; color: white;">${{m.Candidate_Model}}</td>
                    <td class="metric-mono">${{m.Target_Variable}}</td>
                    <td class="metric-mono">${{m.MAE.toFixed(4)}}</td>
                    <td class="metric-mono">${{m.RMSE.toFixed(4)}}</td>
                    <td class="metric-mono">${{m.Brier_or_Calibration.toFixed(4)}}</td>
                    <td><span class="badge ${{m.Status.includes('SELECTED') || m.Status.includes('VALIDATED') ? 'badge-green' : (m.Status.includes('Benchmark') ? 'badge-blue' : 'badge-gold')}}">${{m.Status}}</span></td>
                `;
                mBody.appendChild(tr);
            }});

            // Reconciliation
            const recBody = document.getElementById('recTableBody');
            recBody.innerHTML = '';
            d.reconciliation.forEach(r => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 700; color: white;">${{r.Item}}</td>
                    <td class="metric-mono">${{r.Count_or_Balls.toLocaleString()}}</td>
                    <td class="metric-mono">${{r.Match_Runs.toLocaleString()}}</td>
                    <td class="metric-mono">${{r.Bowler_Runs.toLocaleString()}}</td>
                    <td style="font-size: 12px; color: var(--text-muted);">${{r.Notes}}</td>
                `;
                recBody.appendChild(tr);
            }});
        }}

        function switchTab(tab, event) {{
            document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tab).style.display = 'block';
            if (event) event.target.classList.add('active');
        }}

        function filterTable(tableId, query) {{
            const val = query.toLowerCase();
            document.querySelectorAll('#' + tableId + ' tbody tr').forEach(tr => {{
                tr.style.display = tr.innerText.toLowerCase().includes(val) ? '' : 'none';
            }});
        }}

        function initCharts() {{
            new Chart(document.getElementById('chartBatRAE'), {{
                type: 'bar',
                data: {{
                    labels: d.batters_top20.slice(0, 10).map(b => b.Player),
                    datasets: [{{
                        label: 'Runs Above Expected (RAE)',
                        data: d.batters_top20.slice(0, 10).map(b => b.RAE),
                        backgroundColor: '#E91E63',
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94A3B8', font: {{ size: 9 }} }} }},
                        y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            new Chart(document.getElementById('chartBatDelta'), {{
                type: 'bar',
                data: {{
                    labels: d.batters_top20.slice(0, 10).map(b => b.Player),
                    datasets: [{{
                        label: 'Strike Rate Elevation (Δ)',
                        data: d.batters_top20.slice(0, 10).map(b => b['SR Difference']),
                        backgroundColor: '#38BDF8',
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94A3B8', font: {{ size: 9 }} }} }},
                        y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            new Chart(document.getElementById('chartBowlRPA'), {{
                type: 'bar',
                data: {{
                    labels: d.bowlers_top20.slice(0, 10).map(b => b.Player),
                    datasets: [{{
                        label: 'Runs Prevented Above Expected (RPA)',
                        data: d.bowlers_top20.slice(0, 10).map(b => b['Runs Prevented']),
                        backgroundColor: '#10B981',
                        borderRadius: 5
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94A3B8', font: {{ size: 9 }} }} }},
                        y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            new Chart(document.getElementById('chartBowlScatter'), {{
                type: 'scatter',
                data: {{
                    datasets: [{{
                        label: 'Bowlers',
                        data: d.bowlers_top20.map(b => ({{ x: b['Pressure Economy'], y: b['Pressure Wickets'], name: b.Player }})),
                        backgroundColor: '#FF4081',
                        pointRadius: 7
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(ctx) {{
                                    return ctx.raw.name + ': Econ ' + ctx.raw.x.toFixed(2) + ', Wkts ' + ctx.raw.y;
                                }}
                            }}
                        }},
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        x: {{ title: {{ display: true, text: 'Pressure Economy (Lower is Better)', color: '#94A3B8' }}, ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }},
                        y: {{ title: {{ display: true, text: 'Pressure Wickets Taken', color: '#94A3B8' }}, ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});
        }}

        window.onload = function() {{
            populateAll();
            initCharts();
        }};
    </script>
</body>
</html>"""

with open('outputs/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Updated outputs/dashboard.html with Top 20, IPL-Only, Head-to-Head, and Reconciliation tabs.")
