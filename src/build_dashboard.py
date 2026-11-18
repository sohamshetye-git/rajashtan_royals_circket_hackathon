import json
import os

with open('outputs/dashboard_data.json', 'r', encoding='utf-8') as f:
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
            padding: 20px 40px;
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
            gap: 16px;
        }}

        .brand-logo {{
            background: var(--rr-pink);
            color: white;
            font-weight: 800;
            font-size: 20px;
            padding: 8px 14px;
            border-radius: 8px;
            letter-spacing: 1px;
            box-shadow: 0 0 15px var(--rr-pink-glow);
        }}

        .brand-text h1 {{
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}

        .brand-text p {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        .nav-tabs {{
            display: flex;
            gap: 8px;
            background: rgba(15, 23, 42, 0.6);
            padding: 4px;
            border-radius: 10px;
            border: 1px solid var(--rr-border);
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 8px 18px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
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
            padding: 30px 40px;
            max-width: 1600px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }}

        .card {{
            background: var(--rr-card-bg);
            border-radius: 12px;
            border: 1px solid var(--rr-border);
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            padding-bottom: 12px;
        }}

        .card-title {{
            font-size: 18px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .badge {{
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .badge-pink {{ background: rgba(233, 30, 99, 0.2); color: var(--rr-pink-light); border: 1px solid var(--rr-pink); }}
        .badge-blue {{ background: rgba(56, 189, 248, 0.2); color: var(--accent-blue); border: 1px solid var(--accent-blue); }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}
        .badge-gold {{ background: rgba(245, 158, 11, 0.2); color: var(--accent-gold); border: 1px solid var(--accent-gold); }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}

        .kpi-card {{
            background: #141E33;
            border: 1px solid var(--rr-border);
            border-radius: 10px;
            padding: 18px;
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
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .kpi-val {{
            font-size: 26px;
            font-weight: 800;
            margin: 6px 0;
            font-family: 'JetBrains Mono', monospace;
        }}

        .kpi-sub {{
            font-size: 12px;
            color: var(--text-muted);
        }}

        .table-responsive {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 13.5px;
        }}

        thead th {{
            background: #151D2F;
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            padding: 12px 14px;
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
            padding: 12px 14px;
            white-space: nowrap;
        }}

        .player-cell {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .player-rank {{
            background: #0B0F19;
            border: 1px solid var(--rr-border);
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
        }}

        .rank-top3 {{
            border-color: var(--rr-pink);
            color: var(--rr-pink-light);
            background: rgba(233, 30, 99, 0.15);
        }}

        .player-name-text {{
            font-weight: 700;
            color: white;
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
            padding: 8px 14px;
            color: white;
            font-size: 13px;
            width: 260px;
        }}

        .search-box:focus {{
            outline: none;
            border-color: var(--rr-pink);
        }}

        .methodology-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 20px;
        }}

        .meth-card {{
            background: #141E33;
            border-radius: 10px;
            border: 1px solid var(--rr-border);
            padding: 20px;
        }}

        .meth-card h3 {{
            font-size: 16px;
            color: var(--rr-pink-light);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .meth-card p, .meth-card li {{
            font-size: 13px;
            color: #CBD5E1;
            line-height: 1.6;
            margin-bottom: 8px;
        }}

        .meth-card ul {{
            padding-left: 20px;
        }}

        .formula-box {{
            background: #0B0F19;
            border: 1px solid #334155;
            padding: 12px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--accent-blue);
            margin: 12px 0;
            overflow-x: auto;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}

        @media (max-width: 1024px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
            .dashboard-container {{ padding: 20px; }}
            header {{ padding: 15px 20px; }}
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand-container">
            <div class="brand-logo">RR</div>
            <div class="brand-text">
                <h1>SupeRR Selector Season 2 — Rajasthan Royals Analytics</h1>
                <p>CRISP-X Multi-Dimensional Pressure Impact & Robust Franchise Valuation</p>
            </div>
        </div>
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('batters', event)">Top 10 Batters</button>
            <button class="tab-btn" onclick="switchTab('bowlers', event)">Top 10 Bowlers</button>
            <button class="tab-btn" onclick="switchTab('methodology', event)">Methodology & Audit</button>
            <button class="tab-btn" onclick="switchTab('models', event)">ML vs Baseline Benchmarks</button>
        </div>
    </header>

    <div class="dashboard-container">

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Deliveries Reconciled</div>
                <div class="kpi-val">200,999</div>
                <div class="kpi-sub">192,445 Legal Balls (867 Fixtures)</div>
            </div>
            <div class="kpi-card blue">
                <div class="kpi-label">Chasing WP ROC-AUC</div>
                <div class="kpi-val">0.9059</div>
                <div class="kpi-sub">0.1368 Brier Score Calibration</div>
            </div>
            <div class="kpi-card green">
                <div class="kpi-label">Mean Crisis Wicket Value</div>
                <div class="kpi-val">5.61 Runs</div>
                <div class="kpi-sub">Powerplay: 11.89 | Death: 2.30 Runs</div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-label">Bootstrap Iterations</div>
                <div class="kpi-val">2,000</div>
                <div class="kpi-sub">Match-Clustered Monte Carlo</div>
            </div>
        </div>

        <!-- TAB 1: BATTERS -->
        <div id="tab-batters" class="tab-content">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        Top 10 Pressure Batters
                        <span class="badge badge-pink">Canonical Selections</span>
                        <span class="badge badge-blue">Min 150 Pressure Balls</span>
                    </div>
                    <div>
                        <input type="text" id="batterSearch" class="search-box" placeholder="Search batter..." onkeyup="filterBatters()">
                    </div>
                </div>

                <div class="table-responsive">
                    <table id="batterTable">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>Pressure Balls</th>
                                <th>Runs</th>
                                <th>Pressure SR</th>
                                <th>Normal SR</th>
                                <th>SR Delta (Δ)</th>
                                <th>RAE (Runs Above Exp)</th>
                                <th>Death Balls</th>
                                <th>Dismissals</th>
                                <th>Confidence Tier</th>
                            </tr>
                        </thead>
                        <tbody id="batterTableBody"></tbody>
                    </table>
                </div>
            </div>

            <div class="charts-grid">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Batting Runs Above Expected (RAE) by Player</div>
                    </div>
                    <canvas id="chartBatterRAE"></canvas>
                </div>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Pressure SR vs Normal SR Elevation (Δ)</div>
                    </div>
                    <canvas id="chartBatterSR"></canvas>
                </div>
            </div>
        </div>

        <!-- TAB 2: BOWLERS -->
        <div id="tab-bowlers" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">
                        Top 10 Pressure Bowlers
                        <span class="badge badge-pink">Canonical Selections</span>
                        <span class="badge badge-blue">Min 150 Pressure Balls</span>
                    </div>
                    <div>
                        <input type="text" id="bowlerSearch" class="search-box" placeholder="Search bowler..." onkeyup="filterBowlers()">
                    </div>
                </div>

                <div class="table-responsive">
                    <table id="bowlerTable">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Player</th>
                                <th>Pressure Balls</th>
                                <th>Wickets</th>
                                <th>Pressure Econ</th>
                                <th>Normal Econ</th>
                                <th>Econ Delta (Δ)</th>
                                <th>RPA (Runs Prevented)</th>
                                <th>Death Balls</th>
                                <th>Net Impact</th>
                                <th>Confidence Tier</th>
                            </tr>
                        </thead>
                        <tbody id="bowlerTableBody"></tbody>
                    </table>
                </div>
            </div>

            <div class="charts-grid">
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Runs Prevented Above Expected (RPA)</div>
                    </div>
                    <canvas id="chartBowlerRPA"></canvas>
                </div>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">Pressure Wickets vs Pressure Economy</div>
                    </div>
                    <canvas id="chartBowlerEcon"></canvas>
                </div>
            </div>
        </div>

        <!-- TAB 3: METHODOLOGY -->
        <div id="tab-methodology" class="tab-content" style="display: none;">
            <div class="methodology-grid">
                <div class="meth-card">
                    <h3>1. Pressure Definition & Match Indicators</h3>
                    <p>Deliveries are classified under high leverage using objective pre-delivery states:</p>
                    <ul>
                        <li><strong>Chases:</strong> Required Run Rate (RRR) ≥ 10.0 RPO, or RRR - Current Run Rate (CRR) ≥ 2.5, or death overs (16–20) with target in balance.</li>
                        <li><strong>1st Innings:</strong> Powerplay top-order collapses (≤ 35 runs with ≥ 2 wickets lost) or extreme death overs (overs 17–20).</li>
                        <li><strong>Leverage Index (LI):</strong> Calculated as the expected swing in Win Probability across all empirical outcomes for that delivery state.</li>
                    </ul>
                    <div class="formula-box">LI = E[ |WP_after - WP_before| ]</div>
                </div>

                <div class="meth-card">
                    <h3>2. Performance Measurement (RAE & RPA)</h3>
                    <p>We eliminate misleading raw averages and strike rates by benchmarking every ball against context-specific baselines:</p>
                    <ul>
                        <li><strong>Runs Above Expected (RAE):</strong> Actual off-the-bat runs minus expected runs conditioned on Phase × Wickets Lost × Over × Venue.</li>
                        <li><strong>Runs Prevented Above (RPA):</strong> Expected bowling runs minus actual runs conceded (excluding fielding byes/leg-byes).</li>
                        <li><strong>Wicket Resource Valuation:</strong> Incorporates empirical future run depletion (Powerplay: 11.89 runs, Middle: 8.45 runs, Death: 2.30 runs).</li>
                    </ul>
                </div>

                <div class="meth-card">
                    <h3>3. Fair Comparisons & Anti-Bias Framework</h3>
                    <p>Strict controls prevent small-sample anomalies from inflating rankings:</p>
                    <ul>
                        <li><strong>150-Ball Elite Eligibility:</strong> Eliminates volatile 50–100 ball bilateral flukes (e.g. Reeza Hendricks, Salman Mirza).</li>
                        <li><strong>Empirical Bayes Shrinkage:</strong> Shrinks small-sample statistics toward the tournament prior using variance ratio K₀ = 100 balls.</li>
                        <li><strong>Competition Sensitivity:</strong> Differentiates high-intensity IPL fixtures from lower-tier bilateral T20Is (addressing Sikandar Raza & Abrar Ahmed biases).</li>
                    </ul>
                    <div class="formula-box">Weight w_i = N_i / (N_i + 100)</div>
                </div>

                <div class="meth-card">
                    <h3>4. Reliability & Adversarial Validation</h3>
                    <p>Rigorous verification across statistical and cricket dimensions:</p>
                    <ul>
                        <li><strong>2,000 Match-Clustered Bootstraps:</strong> Resampling whole match clusters to establish rank confidence intervals and Top-10 inclusion probabilities.</li>
                        <li><strong>Holdout Chronological Validation:</strong> Evaluated on unseen 2026 matches achieving 0.9059 ROC-AUC on Win Probability.</li>
                        <li><strong>Strict Boundary Compliance:</strong> Zero auction purse valuations or player retention advice, maintaining pure performance evaluation.</li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- TAB 4: BENCHMARK MODELS -->
        <div id="tab-models" class="tab-content" style="display: none;">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">Out-of-Sample Expected Runs Benchmark (2026 Chronological Holdout)</div>
                    <span class="badge badge-green">Empirical Validation</span>
                </div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Candidate Architecture</th>
                                <th>Holdout MAE</th>
                                <th>Holdout RMSE</th>
                                <th>Brier Calibration</th>
                                <th>Audit Status</th>
                            </tr>
                        </thead>
                        <tbody id="modelsTableBody"></tbody>
                    </table>
                </div>
                <p style="font-size: 13px; color: var(--text-muted); margin-top: 14px;">
                    *<strong>Audit Takeaway:</strong> HistGradientBoosting slightly minimizes RMSE by overfitting boundary tails, but regularized Multi-Factor Context Grid achieves superior MAE (1.3434) and optimal calibration stability without data leakage.
                </p>
            </div>
        </div>

    </div>

    <script>
        const data = {json_str};

        function populateTables() {{
            const bBody = document.getElementById('batterTableBody');
            bBody.innerHTML = '';
            data.batters.forEach(b => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><div class="player-rank ${{b.rank <= 3 ? 'rank-top3' : ''}}">${{b.rank}}</div></td>
                    <td><div class="player-cell"><span class="player-name-text">${{b.name}}</span></div></td>
                    <td class="metric-mono">${{b.balls}}</td>
                    <td class="metric-mono">${{b.runs}}</td>
                    <td class="metric-mono">${{b.sr}}</td>
                    <td class="metric-mono">${{b.norm_sr}}</td>
                    <td class="metric-mono ${{b.delta_sr >= 0 ? 'positive' : 'negative'}}">${{b.delta_sr > 0 ? '+' : ''}}${{b.delta_sr}}</td>
                    <td class="metric-mono positive">+${{b.rae}}</td>
                    <td class="metric-mono">${{b.death_balls}}</td>
                    <td class="metric-mono">${{b.dismissals}}</td>
                    <td><span class="badge ${{b.rank <= 3 ? 'badge-green' : (b.rank <= 7 ? 'badge-blue' : 'badge-gold')}}">${{b.rank <= 3 ? 'Tier 1 (Elite)' : (b.rank <= 7 ? 'Tier 2 (High Value)' : 'Tier 3 (Proven Specialist)')}}</span></td>
                `;
                bBody.appendChild(tr);
            }});

            const bwBody = document.getElementById('bowlerTableBody');
            bwBody.innerHTML = '';
            data.bowlers.forEach(b => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><div class="player-rank ${{b.rank <= 3 ? 'rank-top3' : ''}}">${{b.rank}}</div></td>
                    <td><div class="player-cell"><span class="player-name-text">${{b.name}}</span></div></td>
                    <td class="metric-mono">${{b.balls}}</td>
                    <td class="metric-mono">${{b.wickets}}</td>
                    <td class="metric-mono">${{b.econ}}</td>
                    <td class="metric-mono">${{b.norm_econ}}</td>
                    <td class="metric-mono positive">+${{b.delta_econ}}</td>
                    <td class="metric-mono ${{b.rpa >= 0 ? 'positive' : 'negative'}}">${{b.rpa > 0 ? '+' : ''}}${{b.rpa}}</td>
                    <td class="metric-mono">${{b.death_balls}}</td>
                    <td class="metric-mono positive">+${{b.net_impact}}</td>
                    <td><span class="badge ${{b.rank <= 3 ? 'badge-green' : (b.rank <= 7 ? 'badge-blue' : 'badge-gold')}}">${{b.rank <= 3 ? 'Tier 1 (Elite)' : (b.rank <= 7 ? 'Tier 2 (High Value)' : 'Tier 3 (Proven Specialist)')}}</span></td>
                `;
                bwBody.appendChild(tr);
            }});

            const mBody = document.getElementById('modelsTableBody');
            mBody.innerHTML = '';
            data.models.forEach(m => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 600;">${{m.name}}</td>
                    <td class="metric-mono">${{m.mae.toFixed(4)}}</td>
                    <td class="metric-mono">${{m.rmse.toFixed(4)}}</td>
                    <td class="metric-mono">${{m.brier.toFixed(4)}}</td>
                    <td><span class="badge ${{m.status.includes('Selected') ? 'badge-green' : (m.status.includes('Standard') ? 'badge-blue' : 'badge-gold')}}">${{m.status}}</span></td>
                `;
                mBody.appendChild(tr);
            }});
        }}

        function switchTab(tab, event) {{
            document.querySelectorAll('.tab-content').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tab).style.display = 'block';
            if (event) event.target.classList.add('active');
        }}

        function filterBatters() {{
            const val = document.getElementById('batterSearch').value.toLowerCase();
            document.querySelectorAll('#batterTableBody tr').forEach(tr => {{
                tr.style.display = tr.innerText.toLowerCase().includes(val) ? '' : 'none';
            }});
        }}

        function filterBowlers() {{
            const val = document.getElementById('bowlerSearch').value.toLowerCase();
            document.querySelectorAll('#bowlerTableBody tr').forEach(tr => {{
                tr.style.display = tr.innerText.toLowerCase().includes(val) ? '' : 'none';
            }});
        }}

        function initCharts() {{
            new Chart(document.getElementById('chartBatterRAE'), {{
                type: 'bar',
                data: {{
                    labels: data.batters.map(b => b.name),
                    datasets: [{{
                        label: 'Runs Above Expected (RAE)',
                        data: data.batters.map(b => b.rae),
                        backgroundColor: '#E91E63',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94A3B8', font: {{ size: 10 }} }} }},
                        y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            new Chart(document.getElementById('chartBatterSR'), {{
                type: 'bar',
                data: {{
                    labels: data.batters.map(b => b.name),
                    datasets: [
                        {{ label: 'Pressure SR', data: data.batters.map(b => b.sr), backgroundColor: '#E91E63', borderRadius: 4 }},
                        {{ label: 'Normal SR', data: data.batters.map(b => b.norm_sr), backgroundColor: '#38BDF8', borderRadius: 4 }}
                    ]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ labels: {{ color: '#F8FAFC' }} }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94A3B8', font: {{ size: 10 }} }} }},
                        y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            new Chart(document.getElementById('chartBowlerRPA'), {{
                type: 'bar',
                data: {{
                    labels: data.bowlers.map(b => b.name),
                    datasets: [{{
                        label: 'Runs Prevented Above Expected (RPA)',
                        data: data.bowlers.map(b => b.rpa),
                        backgroundColor: '#10B981',
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        x: {{ ticks: {{ color: '#94A3B8', font: {{ size: 10 }} }} }},
                        y: {{ ticks: {{ color: '#94A3B8' }}, grid: {{ color: '#334155' }} }}
                    }}
                }}
            }});

            new Chart(document.getElementById('chartBowlerEcon'), {{
                type: 'scatter',
                data: {{
                    datasets: [{{
                        label: 'Bowlers',
                        data: data.bowlers.map(b => ({{ x: b.econ, y: b.wkts, name: b.name }})),
                        backgroundColor: '#FF4081',
                        pointRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        tooltip: {{
                            callbacks: {{
                                label: function(ctx) {{
                                    return ctx.raw.name + ': Econ ' + ctx.raw.x + ', Wkts ' + ctx.raw.y;
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
            populateTables();
            initCharts();
        }};
    </script>
</body>
</html>"""

with open('outputs/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Dashboard successfully generated at outputs/dashboard.html")
