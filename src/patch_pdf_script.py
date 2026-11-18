import pandas as pd

with open('src/build_crisp_x_v2_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_bat_block = """    df_top_b = pd.read_csv('outputs/rankings/Top20_Pressure_Batters.csv')
    b_rows = [['Rank', 'Player', 'IPL Balls', 'T20I Balls', 'Runs', 'SR', 'Delta', 'RAE', 'Rating', '95% CI', 'P(Top20)', 'Tier']]
    for _, r in df_top_b.iterrows():
        b_rows.append([
            str(r['Rank']), r['Player'], str(r['IPL Pressure Balls']), str(r['T20I Pressure Balls']),
            str(r['Pressure Runs']), f"{r['Pressure SR']:.1f}", f"{r['SR Difference']:+.1f}", f"{r['RAE']:+.1f}",
            f"{r['Adjusted Rating']:.1f}", r['95% CI'], r['P(Top 20)'], r['Evidence Tier'].split('(')[0].strip()
        ])
    
    t_b = Table(b_rows, colWidths=[20, 95, 42, 42, 28, 30, 28, 34, 30, 42, 40, 117])"""

new_bat_block = """    df_top_b = pd.read_csv('outputs/rankings/final_canonical_top10_batters.csv')
    b_rows = [['Rank', 'Player', 'Balls', 'Runs', 'Press SR', 'Norm SR', 'SR Delta', 'RAE', 'Death Balls', 'Dismissals']]
    for _, r in df_top_b.iterrows():
        b_rows.append([
            str(r['Rank']), r['Player'], str(int(r['Pressure Balls'])), str(int(r['Runs'])),
            f"{r['Pressure SR']:.1f}", f"{r['Normal SR']:.1f}", f"{r['SR Delta']:+.1f}", f"{r['RAE']:+.1f}",
            str(int(r['Death Balls'])), str(int(r['Dismissals']))
        ])
    
    t_b = Table(b_rows, colWidths=[24, 114, 50, 40, 54, 52, 50, 52, 54, 58])"""

old_bw_block = """    df_top_bw = pd.read_csv('outputs/rankings/Top20_Pressure_Bowlers.csv')
    bw_rows = [['Rank', 'Player', 'IPL Balls', 'T20I Balls', 'Wkts', 'Econ', 'RPA', 'Wkt Impact', 'Rating', '95% CI', 'P(Top20)', 'Tier']]
    for _, r in df_top_bw.iterrows():
        bw_rows.append([
            str(r['Rank']), r['Player'], str(r['IPL Pressure Balls']), str(r['T20I Pressure Balls']),
            str(r['Pressure Wickets']), f"{r['Pressure Economy']:.2f}", f"{r['Runs Prevented']:+.1f}", f"{r['Wicket Impact']:.1f}",
            f"{r['Adjusted Rating']:.1f}", r['95% CI'], r['P(Top 20)'], r['Evidence Tier'].split('(')[0].strip()
        ])
    
    t_bw = Table(bw_rows, colWidths=[20, 95, 42, 42, 24, 28, 32, 42, 30, 42, 40, 111])"""

new_bw_block = """    df_top_bw = pd.read_csv('outputs/rankings/final_canonical_top10_bowlers.csv')
    bw_rows = [['Rank', 'Player', 'Balls', 'Wkts', 'Press Econ', 'Norm Econ', 'Econ Delta', 'RPA', 'Death Balls', 'Net Impact']]
    for _, r in df_top_bw.iterrows():
        bw_rows.append([
            str(r['Rank']), r['Player'], str(int(r['Pressure Balls'])), str(int(r['Wickets'])),
            f"{r['Pressure Econ']:.2f}", f"{r['Normal Econ']:.2f}", f"{r['Econ Delta']:+.2f}", f"{r['RPA']:+.1f}",
            str(int(r['Death Balls'])), f"{r['Net Impact']:+.1f}"
        ])
    
    t_bw = Table(bw_rows, colWidths=[24, 114, 50, 40, 56, 54, 52, 50, 52, 56])"""

text_mod = text.replace(old_bat_block, new_bat_block).replace(old_bw_block, new_bw_block)

text_mod = text_mod.replace(
    '6. Definitive Top 20 Pressure Batters (Combined IPL & T20I)',
    '6. Definitive Top 10 Pressure Batters (Audited Canonical Selection)'
).replace(
    '7. Definitive Top 20 Pressure Bowlers (Combined IPL & T20I)',
    '7. Definitive Top 10 Pressure Bowlers (Audited Canonical Selection)'
)

with open('src/build_crisp_x_v2_pdf.py', 'w', encoding='utf-8') as f:
    f.write(text_mod)

print("Patch applied to src/build_crisp_x_v2_pdf.py successfully!")
