import plotly.graph_objects as go
import logging
import datetime
from plotly.subplots import make_subplots
from training_server import TrainingServerProxy
import grpc
import training_backend_pb2_grpc


# Configure debug logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_fitness_trend(df_plot, start_date):
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    df_plot_real = df_plot.loc[df_plot.Date <= str(datetime.date.today())]
    df_plot_projected = df_plot.loc[df_plot.Date >= str(datetime.date.today())]

    fig.add_trace(go.Bar(x=df_plot_real['Date'], y=df_plot_real['TSS'], name='TSS', hoverinfo='skip'), secondary_y=True)
    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['Fatigue'], name='Fatigue', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['Fitness'], name='Fitness', mode='lines'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_real['Date'], y=df_plot_real['Form'], name='Form', mode='lines', fill='tozeroy', fillcolor='rgba(0.1,0.7,0.1,0.2)'), secondary_y=False)

    fig.add_trace(go.Scatter(x=df_plot_projected['Date'], y=df_plot_projected['Fatigue'], name='Fatigue', line={'dash': 'dash'}, mode='lines', showlegend=False, hoverinfo='skip'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_projected['Date'], y=df_plot_projected['Fitness'], name='Fitness', line={'dash': 'dash'}, mode='lines', showlegend=False, hoverinfo='skip'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_plot_projected['Date'], y=df_plot_projected['Form'], name='Form', line={'dash': 'dash'}, mode='lines', showlegend=False, hoverinfo='skip', fill='tozeroy', fillcolor='rgba(0.1,0.7,0.1,0.2)'), secondary_y=False)

    ys = df_plot_real['Fatigue'].tolist() + df_plot_real['Fitness'].tolist() + df_plot_real['Form'].tolist() + [-30.0, 25.0]
    y_min = min(ys)*1.1
    y_max = max(ys)*1.1

    # Set x-axis title
    fig.update_xaxes(title_text="xaxis title", range=[start_date, max(df_plot.Date)])
    fig.update_yaxes(title_text="Training Stress Score", secondary_y=True, range=[0, 300], showgrid=False)
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

    fig.show()


if __name__ == '__main__':
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = training_backend_pb2_grpc.TrainingTrendsStub(channel)
        server = TrainingServerProxy(stub)

        server.update_activities()
        fitness_trend_df = server.get_fitness_trend()
        plot_fitness_trend(fitness_trend_df, '2022-09-10')
