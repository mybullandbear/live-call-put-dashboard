import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def process_chain_data(df):
    """Clean & compute ratios."""
    if df.empty:
        return df, {}
    
    # Pivot for calls/puts
    pivot = df.pivot(index='strike', columns='type', values=['ltp', 'volume', 'oi'])
    pivot.columns = ['_'.join(col).strip() for col in pivot.columns.values]
    
    # Compute PCR (Put/Call Ratio)
    pivot['pcr_oi'] = pivot['oi_Put'] / pivot['oi_Call']
    pivot['pcr_volume'] = pivot['volume_Put'] / pivot['volume_Call']
    
    # Ratios dict for table
    ratios = {
        'pcr_oi': pivot['pcr_oi'].mean(),
        'pcr_volume': pivot['pcr_volume'].mean(),
        'total_call_oi': pivot['oi_Call'].sum(),
        'total_put_oi': pivot['oi_Put'].sum()
    }
    
    return pivot.reset_index(), ratios

def create_plots(df, ratios):
    """Generate Plotly figures: Bar (OI), Line (PCR), Table."""
    if df.empty:
        return {}, {}, {}
    
    # Subplot: OI Bar (Calls vs Puts)
    fig_oi = make_subplots(specs=[[{"secondary_y": False}]])
    fig_oi.add_trace(
        go.Bar(x=df['strike'], y=df['oi_Call'], name='Call OI', marker_color='green'),
        secondary_y=False,
    )
    fig_oi.add_trace(
        go.Bar(x=df['strike'], y=df['oi_Put'], name='Put OI', marker_color='red'),
        secondary_y=False,
    )
    fig_oi.update_layout(title='Open Interest: Calls vs Puts', barmode='group')
    oi_json = fig_oi.to_json()

    # Line: PCR over strikes
    fig_pcr = go.Figure()
    fig_pcr.add_trace(go.Scatter(x=df['strike'], y=df['pcr_oi'], mode='lines+markers', name='PCR OI'))
    fig_pcr.add_hline(y=1.0, line_dash="dash", line_color="black", annotation_text="Neutral PCR")
    fig_pcr.update_layout(title='Put-Call Ratio (OI)')
    pcr_json = fig_pcr.to_json()

    # Table
    table_df = df[['strike', 'ltp_Call', 'volume_Call', 'oi_Call', 'ltp_Put', 'volume_Put', 'oi_Put', 'pcr_oi']].round(2)
    table_df.columns = ['Strike', 'Call LTP', 'Call Vol', 'Call OI', 'Put LTP', 'Put Vol', 'Put OI', 'PCR']
    table_json = table_df.to_json(orient='split')

    return oi_json, pcr_json, table_json