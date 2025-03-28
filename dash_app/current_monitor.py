import datetime
import math
import time
import dash
import plotly.graph_objects as go
import pandas as pd
import os
import threading
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context



def get_last_file_in_directory(directory):
    items = os.listdir(directory)
    sorted_items = sorted(items)
    return sorted_items[-1]


class CurrentDashboard:
    def __init__(self):
        self.df = None
        self.timestamp = None
        self.data = None
        self.channels = None
        self.file_path = None
        self.default_channels = [4,5]
        self.app = dash.Dash(__name__,update_title=None, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.server = self.app.server
        
        
    
        self.update_csv_data()
        self.figure = self.init_graph_build([' I_HV/uA'])
        self.setup_layout()
        

    def update_csv_data(self):
        """Reload CSV data whenever the file is updated, connect automaticaly to newest file"""
        self.logDir = "../logs/"
        self.csv_file = get_last_file_in_directory(self.logDir)
        self.file_path = os.path.join(self.logDir, self.csv_file)

        self.df = pd.read_csv(self.file_path)
        self.timestamp = pd.to_datetime(self.df.iloc[:, 0])
        self.data = self.df.iloc[:, 6:11]
        self.channels = self.data.columns
        self.voltages = self.df.iloc[:, 1:6]
        self.voltages_columns= self.voltages.columns

    def is_online(self):
        last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(self.file_path))
        current_time = datetime.datetime.now()
        if current_time-last_modified_time > datetime.timedelta(seconds=10):
            return False
        else:
            return True
        
    def init_graph_build(self, selected_channels):
        fig = go.Figure()
        for channel in selected_channels:
            
            fig.add_trace(go.Scatter(
                x=self.timestamp,
                y=self.data[channel],
                mode='lines',
                name=channel.split("/",1)[0]
            ))
        return self.build_dark_theme_graph(fig=fig)


    def setup_layout(self):
        self.app.layout = html.Div(id="main-container",
            children=[
                # 1) Row containing the graph and the sidebar
                html.Div(
                    children=[
                        # Graph Section
                        html.Div(
                            children=[
                                dcc.Graph(id='current-graph', className='graph', figure=self.figure),
                                dcc.Store(id='zoom_info')
                            ],
                            className='graph-style'
                        ),
                        # Sidebar Section
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.H2('Channels', className='dashboard-title'),
                                        html.Span('Running', id='status', className='status')
                                    ],
                                    className='header-container'
                                ),
                                # Two-column container for checkboxes and lastest values
                                html.Div(
                                    children=[
                                        # Left Column: Checkboxes with channel names
                                        html.Div(
                                            children=dcc.Checklist(
                                                id='channel-selector',
                                                options=[{'label': ch.split("/",1)[0], 'value': ch} for ch in self.channels],
                                                value=[' I_HV/uA'],
                                                inline=False,
                                                inputStyle={'margin-right': '5px'},
                                                labelStyle={'marginBottom': '10px',
                                                            'fontSize': '17px',
                                                            'display': 'block',
                                                            'font-family': 'Arial, sans-serif', 
                                                            'font-weight':'bold',
                                                            'color':'white'}
                                            ),
                                            className='left-column'
                                        ),
                                        # Right Column: Last values for each channel
                                        html.Div(className='right-column-div',id='last-values',
                                            children=[
                                                html.Div( className='right-column',
                                                    children=f"{self.data[ch].iloc[-1]:.2f} {ch.split('/',1)[1]}",
                                                )
                                                for ch in self.channels
                                            ],
                                            
                                        )
                                    ],
                                    className='two-column-container'
                                )
                            ],
                            className='sidebar-style'
                        )
                    ],
                    className='row-container'
                ),
            # 2) Secondary dashboard row
            html.Div([
                # Column 1: Set Temperature input
                html.Div(
                    children=[
                        # I_LV display
                        html.Div(
                            children=[
                                html.H2("LV"),
                                html.H1("---", id="i-lv-display"),
                                html.H1("---", id="u-lv-display")
                            ],
                            className='secondary-dashboard-item'
                        ),
                         # I_HV display
                        html.Div(
                            children=[
                                html.H2("HV"),
                                html.H1("---", id="i-hv-display"),
                                html.H1("---", id="u-hv-display")
                            ],
                            className='secondary-dashboard-item'
                        ),
                          # I_PWELL display
                        html.Div(
                            children=[
                                html.H2("PWELL"),
                                html.H1("---", id="i-pwell-display"),
                                html.H1("---", id="u-pwell-display")
                            ],
                            className='secondary-dashboard-item'
                        ),
                        
                        # I_PSUBWELL display
                        html.Div(
                            children=[
                                html.H2("PSUB - PWELL"),
                                html.H1("---", id="i-psubwell-display"),
                                html.H1("---", id="u-psubwell-display")
                            ],
                            className='secondary-dashboard-item'
                        ),
                    
                        
                    ],
                    className='secondary-dashboard' 
                ),
             ],className='second-row'
            ),

            # Interval component for live updates, etc.
            dcc.Interval(
                id='interval-component',
                interval=3*1000,
                n_intervals=0
            ),
        ],
        className='main-container'  
    )
        
    

    def build_dark_theme_graph(self,fig):
        fig.update_layout(
            font=dict(color='white'),
            title=dict(
            text='<b>Current Readings</b>',
            font=dict(size=30, color='white',family='Arial, sans-serif'),  # Neon blue title
            x=0.5  # Center align title
        ),
        xaxis=dict(
            title=dict(
                text='<b>Time</b>',
                font=dict(size=20, family='Arial, sans-serif')
            ),
            tickfont=dict(size=14),  # Corrected to tickfont
            showgrid=True,
            gridcolor='rgba(251, 245, 221, 0.2)',  # Light shadow effect with opacity
            gridwidth=0.5,  # You can adjust this value for more subtle or more pronounced gridlines
            linecolor='white'
        ),
        yaxis=dict(
            title=dict(
                text='<b>Current</b>',
                font=dict(size=20, family='Arial, sans-serif')
            ),
            tickfont=dict(size=14),  # Corrected to tickfont
            showgrid=True,
            gridcolor='rgba(251, 245, 221, 0.2)',  # Light shadow effect with opacity
            gridwidth=0.5,  # Adjust for desired effect
            linecolor='white'
        ),
            plot_bgcolor='#1e1e2e',  # Dark background
            paper_bgcolor='#1e1e2e',  # Dark theme for full graph
            legend=dict(
            font=dict(size=15, color='white'),
            bgcolor='#1e1e2e',
        ) 
        )
        return fig

    def update_graph_and_data(self, n_intervals, selected_channels, zoom_info):
        """Callback function to update graphs and values with newest data."""
        # 1) Reload the CSV file to update data
        self.update_csv_data()

        # 2) Build the graph
        fig = go.Figure()
        for channel in selected_channels:
            fig.add_trace(go.Scatter(
                x=self.timestamp,
                y=self.data[channel],
                mode='lines',
                name=channel.split("/",1)[0]
            ))
        fig = self.build_dark_theme_graph(fig)


        # 3) Build the list of last values for each channel (sidebar display)
        last_values_children = [
            html.Div(className='right-column',
                children=f"{self.data[ch].iloc[-1]:.2f} {ch.split('/',1)[1]}",
            )
            for ch in self.channels
        ]

        # 3) Second Dashboard 

        # currens
        i_lv = f"{self.data[self.channels[3]].iloc[-1]:.2f} mA"
        i_hv = f"{self.data[self.channels[4]].iloc[-1]:.3f} uA"
        i_pwell = f"{self.data[self.channels[1]].iloc[-1]:.2f} mA"
        i_psubwell = f"{self.data[self.channels[2]].iloc[-1]:.2f} mA"

        # voltages
        u_lv = f"{self.voltages[self.voltages_columns[3]].iloc[-1]:.2f} V"
        u_hv = f"{self.voltages[self.voltages_columns[4]].iloc[-1]:.3f} V"
        u_pwell = f"{self.voltages[self.voltages_columns[1]].iloc[-1]:.2f} V"
        u_psubwell = f"{self.voltages[self.voltages_columns[2]].iloc[-1]:.2f} V"



        # 6) Determine status (Running or Stopped)
        if self.is_online():
            status_value = "Running"
            background_style = {'backgroundColor': '#034c53'}  # Default background
        else:
            status_value = "Offline"
            background_style = {'backgroundColor': '#FE4F2D'} 
            

        # 7) Apply any zoom info (if the user zooms in/out on the graph)
        if zoom_info:
            for axis_name in ['axis', 'axis2']:
                if f'x{axis_name}.range[0]' in zoom_info:
                        fig['layout'][f'x{axis_name}']['range'] = [
                        zoom_info[f'x{axis_name}.range[0]'],
                        zoom_info[f'x{axis_name}.range[1]']
                    ]
                if f'y{axis_name}.range[0]' in zoom_info:
                        fig['layout'][f'y{axis_name}']['range'] = [
                        zoom_info[f'y{axis_name}.range[0]'],
                        zoom_info[f'y{axis_name}.range[1]']
                    ]

        # 8) Return everything to the corresponding Dash Outputs
        return (
            fig,                # Output -> temperature-graph.figure
            last_values_children,  # Output -> last-values.children
            i_lv,
            i_hv,
            i_pwell,
            i_psubwell,
            u_lv,
            u_hv,
            u_pwell,
            u_psubwell,
            status_value,        # Output -> status.children
            background_style      # Output -> Main container style
        )
    
    def update_graph(self, selected_channels):
        """Callback function to update the graph based on selected channels."""
        fig = go.Figure()
        for channel in selected_channels:
            fig.add_trace(go.Scatter(
                x=self.timestamp,
                y=self.data[channel],
                mode='lines',
                name=channel
            ))
        return self.build_dark_theme_graph(fig)
    
    def update_zoom_info(self, relayout_data, zoom_info):
            if zoom_info is None:
                return relayout_data
            else:
                zoom_info=relayout_data
                return zoom_info
    


    def setup_callbacks(self):
        """Setup the callbacks for the Dash app."""
        # First callback for 'temperature-graph' without allow_duplicate
        self.app.callback(
            Output('current-graph', 'figure'),
            Input('channel-selector', 'value'),
            prevent_initial_call=True
        )(self.update_graph)

        # Second callback for 'temperature-graph' with allow_duplicate
        self.app.callback(
            [Output('current-graph', 'figure', allow_duplicate=True),
            Output('last-values','children'),
            Output('i-lv-display','children'),
            Output('i-hv-display','children'),
            Output('i-pwell-display','children'),
            Output('i-psubwell-display','children'),
            Output('u-lv-display','children'),
            Output('u-hv-display','children'),
            Output('u-pwell-display','children'),
            Output('u-psubwell-display','children'),
            Output('status','children'),
            Output('main-container', 'style')],
            [Input('interval-component', 'n_intervals'),
            Input('channel-selector', 'value')], 
            State('zoom_info', 'data'),
            prevent_initial_call=True
        )(self.update_graph_and_data)

        self.app.callback(
        Output('zoom_info', 'data'),
        [Input('current-graph', 'relayoutData'),
        Input('zoom_info', 'data')]
         )(self.update_zoom_info)

                

    def run(self, debug=True):
        """Run the Dash server"""
        self.app.run(host='0.0.0.0', port=8060,debug=debug)

if __name__ == '__main__':
    dashboard = CurrentDashboard()
    dashboard.setup_callbacks()
    dashboard.run()
    
