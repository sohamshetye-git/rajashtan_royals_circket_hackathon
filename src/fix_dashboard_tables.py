with open('src/build_dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Batters table header
old_bat_head = """                                <th>Pressure Balls (IPL/T20I)</th>
                                <th>Runs</th>
                                <th>Pressure SR</th>
                                <th>Normal SR</th>
                                <th>SR Delta (Δ)</th>
                                <th>RAE (Runs Above Exp)</th>
                                <th>Dismissals</th>
                                <th>BPRI Score</th>
                                <th>Confidence Tier</th>
                                <th>P(Top 10)</th>"""

new_bat_head = """                                <th>Pressure Balls</th>
                                <th>Runs</th>
                                <th>Pressure SR</th>
                                <th>Normal SR</th>
                                <th>SR Delta (Δ)</th>
                                <th>RAE (Runs Above Exp)</th>
                                <th>Death Balls</th>
                                <th>Dismissals</th>
                                <th>Confidence Tier</th>"""

# Replace Bowlers table header
old_bw_head = """                                <th>Pressure Balls (IPL/T20I)</th>
                                <th>Wickets</th>
                                <th>Pressure Econ</th>
                                <th>Normal Econ</th>
                                <th>Econ Delta (Δ)</th>
                                <th>RPA (Runs Prevented)</th>
                                <th>PRI Score</th>
                                <th>Confidence Tier</th>
                                <th>P(Top 10)</th>"""

new_bw_head = """                                <th>Pressure Balls</th>
                                <th>Wickets</th>
                                <th>Pressure Econ</th>
                                <th>Normal Econ</th>
                                <th>Econ Delta (Δ)</th>
                                <th>RPA (Runs Prevented)</th>
                                <th>Death Balls</th>
                                <th>Net Impact</th>
                                <th>Confidence Tier</th>"""

# Replace Batters JS rendering
old_bat_js = """                    <td class="metric-mono">${b.balls} (${b.ipl_balls}/${b.t20i_balls})</td>
                    <td class="metric-mono">${b.runs}</td>
                    <td class="metric-mono">${b.sr}</td>
                    <td class="metric-mono">${b.norm_sr}</td>
                    <td class="metric-mono ${b.delta_sr >= 0 ? 'positive' : 'negative'}">${b.delta_sr > 0 ? '+' : ''}${b.delta_sr}</td>
                    <td class="metric-mono positive">+${b.rae}</td>
                    <td class="metric-mono">${b.dismissals}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light); font-weight: 700;">${b.bpri}</td>
                    <td><span class="badge ${b.rank <= 4 ? 'badge-green' : (b.rank <= 9 ? 'badge-blue' : 'badge-gold')}">${b.tier}</span></td>
                    <td class="metric-mono">${b.p_top10}</td>"""

new_bat_js = """                    <td class="metric-mono">${b.balls}</td>
                    <td class="metric-mono">${b.runs}</td>
                    <td class="metric-mono">${b.sr}</td>
                    <td class="metric-mono">${b.norm_sr}</td>
                    <td class="metric-mono ${b.delta_sr >= 0 ? 'positive' : 'negative'}">${b.delta_sr > 0 ? '+' : ''}${b.delta_sr}</td>
                    <td class="metric-mono positive">+${b.rae}</td>
                    <td class="metric-mono">${b.death_balls}</td>
                    <td class="metric-mono">${b.dismissals}</td>
                    <td><span class="badge ${b.rank <= 3 ? 'badge-green' : (b.rank <= 7 ? 'badge-blue' : 'badge-gold')}">${b.rank <= 3 ? 'Tier 1 (Elite)' : (b.rank <= 7 ? 'Tier 2 (High Value)' : 'Tier 3 (Proven Specialist)')}</span></td>"""

# Replace Bowlers JS rendering
old_bw_js = """                    <td class="metric-mono">${b.balls} (${b.ipl_del}/${b.t20i_del})</td>
                    <td class="metric-mono">${b.wkts}</td>
                    <td class="metric-mono">${b.econ}</td>
                    <td class="metric-mono">${b.norm_econ}</td>
                    <td class="metric-mono positive">+${b.delta_econ}</td>
                    <td class="metric-mono ${b.rpa >= 0 ? 'positive' : 'negative'}">${b.rpa > 0 ? '+' : ''}${b.rpa}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light); font-weight: 700;">${b.pri}</td>
                    <td><span class="badge ${b.rank <= 5 ? 'badge-green' : (b.rank <= 9 ? 'badge-blue' : 'badge-gold')}">${b.tier}</span></td>
                    <td class="metric-mono">${b.p_top10}</td>"""

new_bw_js = """                    <td class="metric-mono">${b.balls}</td>
                    <td class="metric-mono">${b.wickets}</td>
                    <td class="metric-mono">${b.econ}</td>
                    <td class="metric-mono">${b.norm_econ}</td>
                    <td class="metric-mono positive">+${b.delta_econ}</td>
                    <td class="metric-mono ${b.rpa >= 0 ? 'positive' : 'negative'}">${b.rpa > 0 ? '+' : ''}${b.rpa}</td>
                    <td class="metric-mono">${b.death_balls}</td>
                    <td class="metric-mono positive">+${b.net_impact}</td>
                    <td><span class="badge ${b.rank <= 3 ? 'badge-green' : (b.rank <= 7 ? 'badge-blue' : 'badge-gold')}">${b.rank <= 3 ? 'Tier 1 (Elite)' : (b.rank <= 7 ? 'Tier 2 (High Value)' : 'Tier 3 (Proven Specialist)')}</span></td>"""

print("old_bat_head found:", old_bat_head in text)
print("old_bw_head found:", old_bw_head in text)
print("old_bat_js found:", old_bat_js in text)
print("old_bw_js found:", old_bw_js in text)

text = text.replace(old_bat_head, new_bat_head)
text = text.replace(old_bw_head, new_bw_head)
text = text.replace(old_bat_js, new_bat_js)
text = text.replace(old_bw_js, new_bw_js)

with open('src/build_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied clean table updates to src/build_dashboard.py successfully!")
