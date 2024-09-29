import plotly.graph_objects as go
import logging
import datetime
from plotly.subplots import make_subplots

import sys
import pandas as pd

from pathlib import Path

server_path = Path(__file__).parent.parent / 'garmin_server'
sys.path.append(str(server_path))

# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_trend(df_fitness, df_raw_trend_data, start_date):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_plot_real = df_fitness.loc[df_fitness.Date <= str(datetime.date.today())]
    df_plot_projected = df_fitness.loc[df_fitness.Date >= str(datetime.date.today())]

    df_plot_real['avg_TSS_m'] = df_plot_real['TSS'].rolling(min_periods=1, center=False, window=30).mean()
    df_plot_real['avg_TSS_10'] = df_plot_real['TSS'].rolling(min_periods=1, center=False, window=10).mean()

    fig.add_trace(go.Bar(x=df_plot_real['Date'], y=df_plot_real['TSS'], name='TSS', hoverinfo='skip'), secondary_y=True)
    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['avg_TSS_m'], name='TSS (Month)', mode='lines', hovertemplate='%{y:.1f}'), secondary_y=True)
    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['avg_TSS_10'], name='TSS (10d)', mode='lines', hovertemplate='%{y:.1f}'), secondary_y=True)

    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['Fatigue'], name='Fatigue', mode='lines', hovertemplate='%{y:.1f}'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['Fitness'], name='Fitness', mode='lines', hovertemplate='%{y:.1f}'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['Form'], name='Form', mode='lines', fill='tozeroy', fillcolor='rgba(0.1,0.7,0.1,0.2)', hovertemplate='%{y:.1f}'), secondary_y=False)

    fig.add_trace(go.Scatter(x=df_raw_trend_data['dates'], y=df_raw_trend_data['vo2max'], name='vo2max', mode='lines', hovertemplate='%{y:.1f}'), secondary_y=False)

    fig.add_trace(go.Scatter(x=df_plot_projected['Date'], y=df_plot_projected['Fatigue'], name='Fatigue', line={'dash': 'dash'}, mode='lines', showlegend=False, hoverinfo='skip'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_projected['Date'], y=df_plot_projected['Fitness'], name='Fitness', line={'dash': 'dash'}, mode='lines', showlegend=False, hoverinfo='skip'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_projected['Date'], y=df_plot_projected['Form'], name='Form', line={'dash': 'dash'}, mode='lines', showlegend=False, hoverinfo='skip', fill='tozeroy', fillcolor='rgba(0.1,0.7,0.1,0.2)'), secondary_y=False)

    ys = df_plot_real['Fatigue'].tolist() + df_plot_real['Fitness'].tolist() + df_plot_real['Form'].tolist() + [-30.0, 25.0]
    y_min = min(ys)*1.1
    y_max = max(ys)*1.2

    # Set x-axis title
    fig.update_xaxes(title_text="date", range=[start_date, max(df_fitness.Date)])
    fig.update_yaxes(title_text="Fatigue/Fitness/Form", secondary_y=False, range=[y_min, y_max],
                     zerolinecolor='rgb(0.9,0.9,0.9)', gridcolor='rgb(0.9,0.9,0.9)')
    fig.update_layout(bargap=0.0)

    fig.update_traces(marker_color='rgba(0.9,0.7,0,0.3)',
                      marker_line_color='rgba(0.9,0.7,0,0.7)',
                      selector=dict(name="TSS"))

    fig.update_traces(line=dict(width=1.0), secondary_y=False)
    fig.update_traces(marker_color='rgba(0.7,0.1,0.2,0.8)', selector=dict(name="Fatigue"))
    fig.update_traces(marker_color='rgba(0.1,0.1,0.7,0.8)', selector=dict(name="Fitness"))
    fig.update_traces(marker_color='rgba(0.1,0.7,0.1,0.8)', selector=dict(name="Form"))

    fig.add_hline(y=25, line_dash="dash", line=dict(width=1.5), line_color='dark grey',
                  label=dict(text="Freshness",
                             textposition="start",
                             font=dict(size=14, color="dark grey"),
                             yanchor="top"))
    fig.add_hline(y=5, line_dash="dash", line=dict(width=1.5), line_color='dark grey',
                  label=dict(text="Neutral",
                             textposition="start",
                             font=dict(size=14, color="dark grey"),
                             yanchor="top"))
    fig.add_hline(y=-10, line_dash="dash", line=dict(width=1.5), line_color='dark grey',
                  label=dict(text="Optimal",
                             textposition="start",
                             font=dict(size=14, color="dark grey"),
                             yanchor="top"))
    fig.add_hline(y=-30, line_dash="dash", line=dict(width=1.5), line_color='dark grey',
                  label=dict(text="Overload",
                             textposition="start",
                             font=dict(size=14, color="dark grey"),
                             yanchor="top"))

    fig.update_layout(legend=dict(font=dict(size=14)))

    fig.update_layout(plot_bgcolor='white', hovermode='x unified')

    return fig


def plot_fitness_trend(df_fitness, df_raw_trend_data, start_date):
    fig = plot_trend(df_fitness, df_raw_trend_data, start_date)

    fig.update_yaxes(title_text="Training Stress Score", secondary_y=True, range=[0, 300], showgrid=False)

    fig.update_layout(title=dict(text="TSS Fitness Trend Analysis", font=dict(size=20), automargin=True, yref='paper'))

    return fig


def plot_garmin_trend(df_fitness, df_raw_trend_data, start_date):
    fig = plot_trend(df_fitness, df_raw_trend_data, start_date)

    fig.update_yaxes(title_text="Training Stress Score", secondary_y=True, range=[0, 600], showgrid=False)

    fig.update_layout(title=dict(text="Garmin Load Fitness Trend Analysis", font=dict(size=20), automargin=True, yref='paper'))

    return fig


def plot_activities(df_activities, df_raw_trend_data, start_date):
    df_activities['dt'] = pd.to_datetime(df_activities['date_time'])
    df_activities['week'] = df_activities['dt'].dt.to_period('W')
    weekly_totals = df_activities.groupby('week')['duration'].sum().reset_index()
    weekly_totals['duration_hr'] = weekly_totals['duration'] / 60.0 / 60.0
    weekly_totals['duration_hr_avg'] = weekly_totals['duration_hr'].rolling(min_periods=1, center=True, window=10).mean()
    weekly_totals['week_start'] = weekly_totals['week'].apply(lambda x: x.start_time)

    df_activities['avg_TSS_w'] = df_activities['training_stress_score'].rolling(min_periods=1, center=False, window=7).mean()
    df_activities['avg_TSS_2w'] = df_activities['training_stress_score'].rolling(min_periods=1, center=False, window=14).mean()
    df_activities['avg_TSS_m'] = df_activities['training_stress_score'].rolling(min_periods=1, center=False, window=30).mean()
    df_activities['avg_load_w'] = df_activities['training_load'].rolling(min_periods=1, center=False, window=7).mean()
    df_activities['avg_load_m'] = df_activities['training_load'].rolling(min_periods=1, center=False, window=30).mean()
    df_activities['norm_power'] = df_activities['norm_power'].rolling(min_periods=1, center=True, window=3).max()
    #df_activities['max_hr'] = df_activities['max_hr'].rolling(min_periods=1, center=True, window=7).max()

    fig = make_subplots(specs=[[{"secondary_y": True}]])


    fig.add_trace(go.Scatter(
        x=weekly_totals['week_start'],
        y=weekly_totals['duration_hr'],
        name='duration (h/week)',
        mode='markers+lines',
        connectgaps=True,
        hovertemplate='%{y:.1f}',
        visible="legendonly"
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=weekly_totals['week_start'],
        y=weekly_totals['duration_hr_avg'],
        name='avg duration (h/week)',
        mode='markers+lines',
        connectgaps=True,
        hovertemplate='%{y:.1f}',
        visible="legendonly"
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df_raw_trend_data['dates'],
        y=df_raw_trend_data['vo2max'],
        name='V02max(Trend)',
        mode='markers+lines',
        connectgaps=True,
        hovertemplate='%{y:.1f}',
        visible="legendonly"
    ), secondary_y=False)

    trace_info = [
        ('vo2max', 'V02max(Act)'),
        ('norm_power', 'Norm Power, rolling 3d max'),
        ('max_hr', 'Max HR, rolling week max'),
        ('avg_power', 'Avg Power'),
        ('average_hr', 'Avg HR'),
        ('avg_TSS_w', 'TSS, rolling week'),
        ('avg_TSS_2w', 'TSS, rolling 2 weeks'),
        ('avg_TSS_m', 'TSS, rolling month'),
        ('avg_load_w', 'Load, rolling week'),
        ('avg_load_m', 'Load, rolling month')
    ]

    for column_name, trace_name in trace_info:
        y_data = df_activities[column_name] if column_name in df_activities else df_raw_trend_data[column_name]
        secondary_y = True if column_name not in ['vo2max'] else False
        fig.add_trace(go.Scatter(
            x=df_activities['date_time'] if column_name in df_activities else df_raw_trend_data['dates'],
            y=y_data,
            name=trace_name,
            mode='markers+lines',
            connectgaps=True,
            hovertemplate='%{y:.1f}',
            visible="legendonly"
        ), secondary_y=secondary_y)


    # Set x-axis title
    fig.update_xaxes(title_text="title", range=[start_date, max(df_activities.date_time)])

    fig.update_layout(plot_bgcolor='white', hovermode='x unified')

    return fig


