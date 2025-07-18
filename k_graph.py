import streamlit as st
import plotly.graph_objects as go
import numpy as np

def generate_sunflower_data(num_points, angle_mult, radius, color_scheme):
    """Generate sunflower phyllotaxis data"""
    golden_angle = np.pi * (3 - np.sqrt(5)) * angle_mult
    t = np.linspace(0, 1, num_points)
    x, y, z, colors = [], [], [], []
    
    for i, time_val in enumerate(t):
        angle = i * golden_angle
        z_coord = 1 - (2 * i) / num_points
        r = np.sqrt(1 - z_coord**2)
        
        # 3D coordinates
        x.append(r * np.cos(angle) * radius)
        y.append(r * np.sin(angle) * radius)
        z.append(z_coord * radius)

        # Color mapping
        if color_scheme == "blue_to_red":
            r, g, b = int(255 * time_val), int(100 * (1 - time_val)), int(255 * (1 - time_val))
        elif color_scheme == "rainbow":
            hue = time_val * 360
            r = int(255 * (1 - abs((hue / 60) % 2 - 1)))
            g = int(255 * (1 - abs((hue / 60 - 1) % 2 - 1)))
            b = int(255 * (1 - abs((hue / 60 - 2) % 2 - 1)))
        elif color_scheme == "green_to_purple":
            r, g, b = int(128 + 127 * time_val), int(255 * (1 - time_val)), int(128 + 127 * time_val)
        
        colors.append(f'rgba({r},{g},{b},0.9)')
    
    return x, y, z, colors

def create_figure(x, y, z, colors):
    """Create Plotly 3D figure with rotation"""
    fig = go.Figure(
        go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            marker=dict(size=5, color=colors, opacity=0.9),
            hoverinfo='text'
        )
    )
    
    # Camera rotation animation
    frames = [go.Frame(
        layout=dict(scene_camera=dict(
            eye=dict(
                x=1.5 * np.cos(np.radians(a)),
                y=1.5 * np.sin(np.radians(a)),
                z=1
            )
        ))
    ) for a in np.linspace(0, 7200, 500)]
    
    fig.update(
        frames=frames,
        layout=dict(
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                bgcolor='black'
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            updatemenus=[{
                'type': 'buttons',
                'buttons': [
                    dict(label='Play', method='animate', args=[None]),
                    dict(label='Pause', method='animate', args=[[None], dict(mode='immediate')])
                ]
            }]
        )
    )
    return fig

def main():
    st.set_page_config(layout="wide")
    
    # Sidebar controls
    num_points = st.sidebar.slider("Points", 100, 3000, 1000)
    angle_mult = st.sidebar.slider("Angle Multiplier", 0.5, 2.0, 1.0, 0.1)
    radius = st.sidebar.slider("Radius", 5.0, 20.0, 10.0, 0.5)
    color_scheme = st.sidebar.selectbox("Colors", ["blue_to_red", "rainbow", "green_to_purple"])
    
    # Generate and display
    x, y, z, colors = generate_sunflower_data(num_points, angle_mult, radius, color_scheme)
    fig = create_figure(x, y, z, colors)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
