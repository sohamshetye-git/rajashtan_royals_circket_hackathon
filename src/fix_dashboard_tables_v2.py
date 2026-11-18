with open('src/build_dashboard.py', 'r', encoding='utf-8') as f:
    text = f.read()

# In f-string, double braces {{ and }} are used.
old_bat_js = """                    <td class="metric-mono">${{b.balls}} (${{b.ipl_balls}}/${{b.t20i_balls}})</td>
                    <td class="metric-mono">${{b.runs}}</td>
                    <td class="metric-mono">${{b.sr}}</td>
                    <td class="metric-mono">${{b.norm_sr}}</td>
                    <td class="metric-mono ${{b.delta_sr >= 0 ? 'positive' : 'negative'}}">${{b.delta_sr > 0 ? '+' : ''}}${{b.delta_sr}}</td>
                    <td class="metric-mono positive">+${{b.rae}}</td>
                    <td class="metric-mono">${{b.dismissals}}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light); font-weight: 700;">${{b.bpri}}</td>
                    <td><span class="badge ${{b.rank <= 4 ? 'badge-green' : (b.rank <= 9 ? 'badge-blue' : 'badge-gold')}}">${{b.tier}}</span></td>
                    <td class="metric-mono">${{b.p_top10}}</td>"""

new_bat_js = """                    <td class="metric-mono">${{b.balls}}</td>
                    <td class="metric-mono">${{b.runs}}</td>
                    <td class="metric-mono">${{b.sr}}</td>
                    <td class="metric-mono">${{b.norm_sr}}</td>
                    <td class="metric-mono ${{b.delta_sr >= 0 ? 'positive' : 'negative'}}">${{b.delta_sr > 0 ? '+' : ''}}${{b.delta_sr}}</td>
                    <td class="metric-mono positive">+${{b.rae}}</td>
                    <td class="metric-mono">${{b.death_balls}}</td>
                    <td class="metric-mono">${{b.dismissals}}</td>
                    <td><span class="badge ${{b.rank <= 3 ? 'badge-green' : (b.rank <= 7 ? 'badge-blue' : 'badge-gold')}}">${{b.rank <= 3 ? 'Tier 1 (Elite)' : (b.rank <= 7 ? 'Tier 2 (High Value)' : 'Tier 3 (Proven Specialist)')}}</span></td>"""

old_bw_js = """                    <td class="metric-mono">${{b.balls}} (${{b.ipl_del}}/${{b.t20i_del}})</td>
                    <td class="metric-mono">${{b.wkts}}</td>
                    <td class="metric-mono">${{b.econ}}</td>
                    <td class="metric-mono">${{b.norm_econ}}</td>
                    <td class="metric-mono positive">+${{b.delta_econ}}</td>
                    <td class="metric-mono ${{b.rpa >= 0 ? 'positive' : 'negative'}}">${{b.rpa > 0 ? '+' : ''}}${{b.rpa}}</td>
                    <td class="metric-mono" style="color: var(--rr-pink-light); font-weight: 700;">${{b.pri}}</td>
                    <td><span class="badge ${{b.rank <= 5 ? 'badge-green' : (b.rank <= 9 ? 'badge-blue' : 'badge-gold')}}">${{b.tier}}</span></td>
                    <td class="metric-mono">${{b.p_top10}}</td>"""

new_bw_js = """                    <td class="metric-mono">${{b.balls}}</td>
                    <td class="metric-mono">${{b.wickets}}</td>
                    <td class="metric-mono">${{b.econ}}</td>
                    <td class="metric-mono">${{b.norm_econ}}</td>
                    <td class="metric-mono positive">+${{b.delta_econ}}</td>
                    <td class="metric-mono ${{b.rpa >= 0 ? 'positive' : 'negative'}}">${{b.rpa > 0 ? '+' : ''}}${{b.rpa}}</td>
                    <td class="metric-mono">${{b.death_balls}}</td>
                    <td class="metric-mono positive">+${{b.net_impact}}</td>
                    <td><span class="badge ${{b.rank <= 3 ? 'badge-green' : (b.rank <= 7 ? 'badge-blue' : 'badge-gold')}}">${{b.rank <= 3 ? 'Tier 1 (Elite)' : (b.rank <= 7 ? 'Tier 2 (High Value)' : 'Tier 3 (Proven Specialist)')}}</span></td>"""

print("old_bat_js found:", old_bat_js in text)
print("old_bw_js found:", old_bw_js in text)

text = text.replace(old_bat_js, new_bat_js)
text = text.replace(old_bw_js, new_bw_js)

with open('src/build_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Applied replacements to src/build_dashboard.py!")
